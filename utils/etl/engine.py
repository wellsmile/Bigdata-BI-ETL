#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''
from collections import defaultdict
import getopt
import itertools
import json
import logging
import multiprocessing.dummy
import os
import sys
import time

from db import DB
from storage.es import ES
from computation.hive import Hive
from computation.presto import Presto
from elasticsearch.exceptions import NotFoundError
from analysis_generator import ALL_ANALYSIS

class ETLEngine(object):
    '''ETL execution engine'''
    def __init__(self, **kwargs):
        logging.info('init engine...')
        
        self.cylinder_num = 4
        self.db = DB()
        self.to_update = kwargs.get('update', False)
        self.specify_date = kwargs.get('specify_date', None)
        self.delete = kwargs.get('delete', False)
        self.no_insert = kwargs.get('no_insert', False)
        self.specify_report = kwargs.get('specify_report', [])
        self.oldversion = kwargs.get('oldversion', False)
        self.bothversion = kwargs.get('bothversion', False)
        self.__init_context()
        self.__init_storage_engine()
        self.__init_compute_engine()
        self.__init_computations()
        self.__init_report_units()
        self.result_buffer = []
    
    def __init_context(self):
        context = dict()
        
        if self.specify_date:
            today_time = time.mktime(time.strptime(self.specify_date,'%Y-%m-%d'))
        else:
            today_time = time.time()-86400
            
        localtime_today = time.localtime(today_time)
        context['today'] = time.strftime('%Y-%m-%d', localtime_today)
        
        self.context = context
    
    def __init_storage_engine(self):
        storage_engine_info = defaultdict(list)
        storage_engine_settings = self.db.get_storage_engine_settings()
        today_str = str(self.context.get('today'))
        condition = {"query":{"match": {
                                            "computation_ds": today_str
                                        }
                            }
                    }

        if self.specify_report:
            condition = {"query": {"bool": {"must": [{ "terms": { "refer": self.specify_report } },{ "match": { "computation_ds": today_str } }]}}}
        
        for storage_engine_setting in storage_engine_settings:
            stype = storage_engine_setting.stype
            setype = storage_engine_setting.setype
            
            if setype == 'ELASTICSEARCH':
                storage = ES(storage_engine_setting)
                if self.to_update or self.delete:
                    storage.delete(conditions=condition)
                    if self.delete:
                        sys.exit()
                else:
                    try:
                        get_result = storage.get(conditions=condition)
                    except NotFoundError:
                        get_result = None
                    if get_result:
                        print('data in {0} has exist, if you want to overwrite it, you must provide the update argu'.format(self.context['today']))
                        sys.exit()
        
            storage_engine_info[stype].append(storage)
        self.storage_engine_info = storage_engine_info
        
    def __init_compute_engine(self):
        computation_engine_info = dict()
        computation_engine_settings = self.db.get_computation_engine_settings()
        
        for computation_engine_setting in computation_engine_settings:
            ctype = computation_engine_setting.ctype
            
            if ctype == 'HIVE':
                compute = Hive(computation_engine_setting)
            elif ctype == 'PRESTO':
                compute = Presto(computation_engine_setting)
            
            computation_engine_info[computation_engine_setting.id] = compute
        self.computation_engine_info = computation_engine_info
    
    def __init_computations(self):
        computation_info = defaultdict(list)
        computation_settings = self.db.get_computation_settings()
        
        for computation_setting in computation_settings:
            layer = computation_setting.layer
            computation_info[layer].append(computation_setting)
        self.computation_info = computation_info

    def __init_report_units(self):
        report_unit_list = list()
        report_unit_settings = self.db.get_report_unit_settings()
        
        for report_unit_setting in report_unit_settings:
            report_unit_list.append(report_unit_setting)
        self.report_unit_list = report_unit_list
    
    def _worker(self, computation):
        engine_id = computation.engine_id
        sql_template = computation.template # the computation template, default sql
        output = computation.output
        
        if sql_template != 'select': # if sql is 'select', skip it
            if (not output) and (not self.no_insert):
                sql = sql_template.format(**self.context) # render the computation template
                print('/n--------------------------\n' + sql + '\n-----------------------------\n')
    #             logging.info('worker: ' + sql)
                engine_object = self.computation_engine_info.get(engine_id) # get engine object
                results = engine_object.execute(sql = sql) # execute will start a new subprocess to carry out the workload, so it's thread-safe
                
            if output:
                refer = computation.refer
                if (not self.specify_report) or (refer in self.specify_report):
                    dimension = computation.dimension
                    dimension = json.loads(dimension)
                    dimension.sort()
                    if not dimension:
                        dimension = ['matrix_token']
                        
                    dimension_num = len(dimension)
                    grouping_sets_list = []
                    grouping_sets_list += dimension
                    if dimension_num > 1:
                        if dimension_num > 3:
                            dimension_num = 3
                        for i in range(2, dimension_num+1):
                            grouping_sets_list += list(itertools.combinations(dimension,i))
                    group_by_str = ','.join(dimension)
                    grouping_sets_str = str(grouping_sets_list).replace('[','(').replace(']',')').replace('\'','')
                    
                    self.context['group_by'] = group_by_str
                    self.context['grouping_sets'] = grouping_sets_str
                    
                    as_others = "grouping__id AS unit_name,'{today}' AS computation_ds,"
                    as_value = 'AS value,'
                    as_ds = 'AS ds, count(1),'
                    
                    as_dimension_list = []
                    for each_dimension in dimension:
                        if each_dimension == 'matrix_token':
                            as_dimension_list.append('matrix_token AS product_id')
                        elif each_dimension == 'ds':
                            pass
                        else:
                            as_dimension_list.append('{0} AS {0}'.format(each_dimension))
                            
                    dimension_str = ','.join(as_dimension_list)
                    as_others = as_others + dimension_str
                    
                    self.context['as_others'] = as_others
                    self.context['as_value'] = as_value
                    self.context['as_ds'] = as_ds
                    
                    output_conf = json.loads(output)
                    if 'ds' in dimension:
                        tmplist = []
                        for i in dimension:
                            if i != 'ds':
                                tmplist.append(i)
                        column_names = ['ds', 'value', 'unit_name', 'computation_ds'] + tmplist
                    else:
                        column_names = ['ds', 'value', 'unit_name', 'computation_ds'] + dimension
                    column_names = ['product_id' if x == 'matrix_token' else x for x in column_names]
                    name_type_mapping = output_conf
                    
                    sql = sql_template.format(**self.context).format(**self.context) # render the computation template
                    print('\n=========='+refer+'===========\n' + sql + '\n=========================\n')
    #                 logging.info('worker: ' + sql)
                    engine_object = self.computation_engine_info.get(engine_id) # get engine object
                    results = engine_object.execute(sql = sql)
                    
                    if results:
                        for result in results:
                            result = result.strip() # clear the heading and tailing blank spaces
                            if result:
                                result_items = result.split('\t') # split tsv output
                                result_items.pop(1)
                                name_data_mapping = dict(zip(column_names, result_items))
                                tmpmap = name_data_mapping.copy()
                                for resultkey in tmpmap.keys():
                                    resultvalue = tmpmap[resultkey]
                                    if resultvalue == 'NULL':
                                        name_data_mapping.pop(resultkey)
                                        
                                for resultkey in name_data_mapping.keys():
                                    resultvalue = name_data_mapping[resultkey]
                                    field_type = name_type_mapping.get(resultkey, 'str')
                                    if field_type == 'str':
                                        name_data_mapping[resultkey] = str(resultvalue)
                                    elif field_type == 'int':
                                        name_data_mapping[resultkey] = float(resultvalue)
                                    elif field_type == 'date':
                                        name_data_mapping[resultkey] = str(resultvalue)
                                    else:
                                        pass
                    
                                name_data_mapping['refer'] = refer
                                intstr = name_data_mapping.get('unit_name')
                                binstr = bin(int(intstr)).replace('0b','')
                                
                                if len(binstr) < len(dimension):
                                    binstr = '0'*(len(dimension)-len(binstr)) + binstr
                                binstr = ''.join(reversed(binstr))
                                if 'ds' not in dimension:
                                    unitname_list = ['ds']
                                else:
                                    unitname_list = []
                                binstr_index = 0
                                for hasornot in binstr:
                                    if hasornot == '1':
                                        unitname_list.append(dimension[binstr_index])
                                    binstr_index += 1
                                unitname_list = ['product_id' if x == 'matrix_token' else x for x in unitname_list]
                                unitname_list.sort()
                                unit_name = '_'.join(unitname_list)
                                name_data_mapping['unit_name'] = unit_name
                                    
                                self.result_buffer.append(name_data_mapping)
                            else: # if no result,not put it
                                pass
                    else:
                        print('★★★★★  '+ refer +' ERROR:' + sql)
    
    def _worker_by_sqlgenerator(self, analysis):
        sql_template = analysis.analysis_sql().replace('\n',' ')
        self.context['computation_ds'] = self.context['today']
        sql = sql_template.format(**self.context)
        
        dimensions = analysis.analysis_dimensions
        output_consts = analysis.analysis_output_consts
        output_dimensions = analysis.analysis_output_dimensions
        output_metrics = analysis.analysis_output_metrics
        column_names_init = output_dimensions + output_metrics
        
        to_run = False
        for output_metric in output_metrics:
            if not self.specify_report:
                to_run = True
            elif output_metric in self.specify_report and output_metric != 'dummy':
                to_run = True
        
        if to_run:
            '''此处要获取engine_object要修改'''
            tmp = list(self.computation_engine_info.keys())[0]
            engine_object = self.computation_engine_info.get(tmp)
            print('\n--------------------------\n' + sql + '\n-----------------------------\n')
            results = engine_object.execute(sql = sql)
            if results:
                for result in results:
                    column_names = []
                    column_names = [x for x in column_names_init]
                    result = result.strip() # clear the heading and tailing blank spaces
                    if result:
                        result_items = [str(x) for x in result.split('\t')] # split tsv output
                        name_data_mapping = dict(zip(column_names, result_items))
                        if output_consts: # if has consts configration, add it into result
                            for key in output_consts.keys():
                                name_data_mapping[key] = output_consts[key].format(**self.context)
                        name_data_mapping.pop('dummy')
                        column_names.remove('dummy')
                        
                        # build unit_name
                        intstr = name_data_mapping.pop('gid')
                        column_names.remove('gid')
                        binstr = bin(int(intstr)).replace('0b','')
                        
                        if len(binstr) < len(dimensions):
                            binstr = '0'*(len(dimensions)-len(binstr)) + binstr
                        binstr = ''.join(reversed(binstr))
                        if 'ds' not in dimensions:
                            unitname_list = ['ds']
                        else:
                            unitname_list = []
                        binstr_index = 0
                        for hasornot in binstr:
                            if hasornot == '1':
                                unitname_list.append(dimensions[binstr_index])
                            binstr_index += 1
                        unitname_list = [x for x in unitname_list]
                        unitname_list.sort()
                        unit_name = '_'.join(unitname_list)
                        
                        # build refer
                        common_column_names = []
                        common_column_names = column_names + [x for x in output_consts.keys()]
                        [common_column_names.remove(x) for x in output_metrics if x != 'dummy']
                        for output_metric in output_metrics:
                            if output_metric == 'dummy':
                                continue
                            refer = output_metric
                            if (not self.specify_report) or (refer in self.specify_report):
                                result_dict = {}
                                result_dict['computation_ds'] = self.context['today']
                                result_dict['refer'] = refer
                                result_dict['unit_name'] = unit_name
                                result_dict['value'] = float(name_data_mapping.get(output_metric, '0.0'))
                                
                                hook = analysis.analysis_metrics.get(refer, {}).get('analysis_metric_hook', None)
                                if hook:
                                    result_dict['value'] = float(hook(result_dict['value']))
                                
                                for common_column_name in common_column_names:
                                    result_dict[common_column_name] = name_data_mapping.get(common_column_name, 'unknown')
                                
                                tobe_delete = []    
                                for key in result_dict.keys():
                                    if result_dict[key] == 'NULL':
                                        tobe_delete.append(key)
                                for key in tobe_delete:
                                    result_dict.pop(key)
                                    
                                self.result_buffer.append(result_dict)
            else:
                print('★★★★★   ERROR: ' + sql)            

                            
    def start(self):
        logging.info('Engine Start!')
        
        if not self.no_insert:
        # first of all, start all the datawarehouse-related computations
            layer_range = range(4)
            for layer in layer_range:
                layer_computation_list = self.computation_info.get(layer, [])
                 
                with multiprocessing.dummy.Pool(4) as computation_pool:
                    computation_pool.map(self._worker, layer_computation_list)
        # first of all, start all the datawarehouse-related computations END
        if self.oldversion or self.bothversion:     
            # all report units computations
            with multiprocessing.dummy.Pool(8) as computation_pool:
                computation_pool.map(self._worker, self.report_unit_list)
            # all report units computations END
            
        # all sql generator computations
        if (not self.oldversion) or self.bothversion:
            with multiprocessing.dummy.Pool(8) as computation_pool:
                computation_pool.map(self._worker_by_sqlgenerator, ALL_ANALYSIS)
        # all sql generator computations end
        
        logging.info('Engine Done')

    def replay(self, storge_name, **kwargs):
        logging.info('Storge Replay!')
        logfile_num = 9999
        specify_date = kwargs.get('date', None)
        while logfile_num >= 0:
            lognum_str = ('.' + str(logfile_num)) if logfile_num else ''
            file_path = '/data/log/elasticsearch/es_log.log' + lognum_str
            logfile_num = logfile_num - 1
            if not os.path.exists(file_path):
                continue
            file_path_new = file_path+'.backup'+str(int(time.time()))
            os.rename(file_path, file_path_new)
            with open(file_path_new, 'r') as logfile:
                for logline in logfile:
                    log_list = logline.split('\t')
                    if log_list[0] != storge_name or str(log_list[5]) == 'False':
                        continue
                    if specify_date:
                        if log_list[1].split(' ')[0] != specify_date:
                            continue
                    for storage in self.storage_engine_info['RESULT']: # store with all storage_engine
                        # reinit the es_logger to write log to the new file
                        storage.es_logger = storage.__init_logger__(storge_name, file_path)
                        if log_list[3] == 'PUT':
                            storage.put(doc = json.loads(log_list[4]))
                        elif log_list[3] == 'DELETE':
                            storage.delete(conditions = json.loads(log_list[4]))
    
    def flush_buffer(self):
        logging.info('Flush Buffer...')
        for storage in self.storage_engine_info['RESULT']: # store with all storage_engine
            storage.puts(docs = self.result_buffer)
            
if __name__ == '__main__':
    
    start_engine_time = time.time()
    help_text = '''
    Hi, I'm a engine to run your pixel settings.I have some argus:
    
        --help        To watch the help text.
                        e.g. python3 engine.py --help
        --date        To specify a date to run engine.
                        e.g. python3 engine.py --date=2017-01-01
        --noinsert    If given this argu,I won't run the sql of 'insert overwrite'.(Only used in old version)
                        e.g. python3 engine.py --noinsert
        --report      To specify some report to run engine.
                        e.g. python3 engine.py --report=dau,dtu,drru
        --oldversion  To run this engine only by oldversion way.
                        e.g. python3 engine.py --oldversion
        --bothversion To run this engine by both the new and the old version way.
                        e.g. python3 engine.py --bothversion
        -y            To auto anwser yes for all question.
                        e.g. python3 engine.py --update -y --date=2017-01-01
        \033[1;31;40m--update\033[0m      Delete the data of the specify_date before run engine.
                        e.g. python3 engine.py --update --date=2017-01-01
        \033[1;31;40m--replay\033[0m      To specify a storage name,I will replay it to your storage from your storage log file.
                        e.g. python3 engine.py --replay=ES_01
        \033[1;31;40m--delete\033[0m      To delete data of the specify_date.
                        e.g. python3 engine.py --delete --date=2017-01-01
                        
        ps:  The red font word is the argus which can change your date.
                '''
    
    opt,args = getopt.getopt(sys.argv[1:], "yd:r:", ['update','date=','replay=','help','delete','noinsert','report=', 'oldversion', 'bothversion'])
    
    update = False
    specify_date = None
    replay = None
    delete = False
    choose_yes = False
    no_insert = False
    oldversion = False
    bothversion = False
    specify_report = []
    
    for op,value in opt: # get argus
        if op in ('-h', '--help'):
            print(help_text) 
            sys.exit()
        if op in ('--update'):
            if not value:
                update = True
            else:
                print('update argu must have no value')
                sys.exit()
        if op in ('d', '--date'):
            specify_date = str(value).lower()
        if op in ('-r', '--replay'):
            replay = str(value)
        if op in ('--delete'):
            if not value:
                delete = True
            else:
                print('delete argu must have no value')
                sys.exit()
        if op in ('-y'):
            if not value:
                choose_yes = True
            else:
                print('-y argu must have no value')
                sys.exit()
        if op in ('--noinsert'):
            if not value:
                no_insert = True
            else:
                print('noinsert argu must have no value')
                sys.exit()
        if op in ('--report'):
            specify_report = str(value).split(',')
        if op in ('--oldversion'):
            if not value:
                oldversion = True
            else:
                print('oldversion argu must have no value')
                sys.exit()
        if op in ('--bothversion'):
            if not value:
                bothversion = True
                if oldversion:
                    print('use bothversion argu must have no oldversion argu')
                    sys.exit()
            else:
                print('bothversion argu must have no value')
                sys.exit()
    
    if replay: # To specify a storage name,I will replay it to your storage from your storage log file.
        if any(update, specify_date, delete):
            print('if you choose replay, you mustn\'t provide other argu')
            sys.exit()
        else:
            if choose_yes:
                choose = 'yes'
            else:
                choose = input('\033[1;31;40mThis command will overwrite your data. Are you sure to continue?\033[0m').lower()
            if not (choose == 'yes' or choose == 'y'):
                sys.exit()
            else:
                engine = ETLEngine()
                engine.replay(replay)
                sys.exit()
    
    if update: # Delete the data of the specify_date before run engine.
        if delete:
            print('update and delete argu can\'t appear together')
            sys.exit()
        if choose_yes:
            choose = 'yes'
        else:
            choose = input('\033[1;31;40mThis command will overwrite your data. Are you sure to continue?\033[0m').lower()
        if not (choose == 'yes' or choose == 'y'):
            sys.exit()
        elif not specify_date:
            print('update must has the date argu')
            sys.exit()
            
    if delete: # To delete data of the specify_date.
        if choose_yes:
            choose = 'yes'
        else:
            choose = input('\033[1;31;40mThis command will overwrite your data. Are you sure to continue?\033[0m').lower()
        if not (choose == 'yes' or choose == 'y'):
            sys.exit()
        if not specify_date:
            print('delete must has the date argu')
            sys.exit()
    
    engine = ETLEngine(update=update, 
                       specify_date=specify_date, 
                       delete=delete, 
                       no_insert=no_insert, 
                       specify_report=specify_report, 
                       oldversion=oldversion, 
                       bothversion=bothversion)
    engine.start()
    engine.flush_buffer()
    
    end_engine_time = time.time()
    cost_time = str(int(end_engine_time - start_engine_time))
    print('spend: about {0} seconds.'.format(cost_time))

