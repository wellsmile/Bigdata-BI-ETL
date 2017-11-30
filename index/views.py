#coding=utf-8
import json

from elasticsearch import Elasticsearch

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.contrib.auth.models import Group

from etl.models import StorageEnigne
from etl.models import ReportUnit
from etl.models import ProductIdName
from elasticsearch.exceptions import NotFoundError, RequestError

@login_required
def index(request, template):
    return render(request, template)

def report(request):
    '''get report by report's id'''
#     user = request.user
#     username = user.get_username()
#     print(username)
#     group = Group.objects.get(user=user)
#     print(group.name)
#     
    dimensions_names = {'channel_id': '渠道' ,'server_id': '服务器'}
    unit_name = ''
    param_names = ['product_id',
                   'refer',
                   'start_date',
                   'end_date'
                   ]
    # get dimensions name
    dimensions = request.GET.get('dimensions', '["ds","product_id"]')
    dimensions_list = json.loads(dimensions)
    tmp_column_name = ''
    tmp_column = ''
    for dim in dimensions_list:
        dim_value = request.GET.get(dim, None)
        if dim not in ['ds','product_id'] and not dim_value:
            tmp_column_name = dimensions_names.get(dim, 'unknown')
            tmp_column = dim
    dimensions_list.sort()
    extra_condition = request.GET.get('extra', '{}') # {a:[b],c:[d,e]}
    extra_condition = json.loads(extra_condition)
    
    param_getter = lambda x: request.GET.get(x, None)
    param_map = dict(zip(param_names, map(param_getter, param_names)))
    
    refer = param_map.get('refer')
    product_id = str(param_map.get('product_id'))
    start_date = param_map.get('start_date')
    end_date = param_map.get('end_date')
    
    complex_search = request.GET.get('complex', '{}')
    complex_search = json.loads(complex_search)
    
    
    if all(param_map.values()):
        try:
            # get product name by its id
            product = ProductIdName.objects.get(id=product_id)
            product_name = product.name
        except Exception:
            product_name = '未知'
        
        # get storage settings, init storage object
        storage = StorageEnigne.objects.filter(stype='RESULT',setype='ELASTICSEARCH')[0]
        conf = json.loads(storage.conf)
        
        es_connect = conf.get('connect_settings')
        es_index = conf.get('index_name')
        es_doctype = conf.get('type_name')
        es = Elasticsearch(es_connect)
        
        # the base condition, need append conditions later
        condition = {"query": {"bool": {"should":[{"bool": {"must": [{ "match": { "refer": refer } },{ "match": { "product_id": product_id } },{"range":{"ds":{"gte":start_date,"lte":end_date}}}]}}]}}}
            
        if dimensions_list: # if get dimensions, build unit name from it
            unit_name = '_'.join(dimensions_list)
            for dimension in dimensions_list:
                dimension_value = request.GET.get(dimension, '[]')
                dimension_value = json.loads(dimension_value)
                if dimension_value and dimension != 'product_id': # if this dimension has value, must add it to base conditions
                    condition["query"]["bool"]["should"][0]["bool"]["must"].append({ "terms": { dimension: dimension_value } })
                else: # if this dimension has not value, use it to build unit name,but not add to conditions
                    pass
        else: # if cant get dimensions ,default is 'matrix_token'
            unit_name = 'matrix_token'
        condition["query"]["bool"]["should"][0]["bool"]["must"].append({ "match": { 'unit_name': unit_name } })
        
        if extra_condition:
            for extra in extra_condition.keys():
                condition["query"]["bool"]["should"][0]["bool"]["must"].append({ "terms": { extra: extra_condition[extra] } })
            
        response = None
        # read report unit settings
        try:
            report_unit = ReportUnit.objects.filter(refer=refer)[0]
        except Exception:
            response = JsonResponse({'code': -2, 'msg': 'report unit setting not found'})
        else:
            visualization = report_unit.visualization
            try:
                visualization_dict = json.loads(visualization)
            except Exception:
                response = JsonResponse({'code': -3, 'msg': '{0} report unit visualization error'.format(refer)})
            else:
                sort_dict = visualization_dict.get('sort', {'columns':['ds'],'order':['asc']})
                sort_zip = zip(sort_dict.get('columns',['ds']), sort_dict.get('order',['asc']))
                sort_condition = [':'.join(x) for x in sort_zip]
                
                if complex_search:
                    for key in complex_search.keys():
                        condition["query"]["bool"]["should"].append({'bool':{'must': [{'terms':{key:[complex_search[key]]}}]}})
                try:
#                     print('★★★★★  '+ str(condition))
                    # get es doc by conditions
                    esget_resp = es.search(index=es_index, doc_type=es_doctype, body=condition, sort=sort_condition, size=9999)
                except NotFoundError:
                    response = JsonResponse({'code': -6, 'msg': 'ES storage error:index not found'})
                else:
                    try:
                        hitslist = esget_resp.get('hits', {}).get('hits', None)
                    except Exception:
                        response = JsonResponse({'code': -5, 'msg': 'ES response error'})
                    else:
                        if hitslist:
                            resultlist = [ i.get('_source') for i in hitslist ]
                        else:
                            resultlist = []
                        for dem in dimensions_list:
                            if dem not in visualization_dict['dimensions'].keys() and dem != 'product_id':
                                visualization_dict['dimensions'][dem] = {'name': dimensions_names.get(dem, 'unknown'), 'type': 'str'}
                        if tmp_column and tmp_column_name:
                            visualization_dict['table']['columns'][0] = tmp_column
                            visualization_dict['table']['columnNames'][0] = tmp_column_name
                        
                        visualization_dict['refer'] = refer
                        visualization_dict['product_id'] = product_id
                        visualization_dict['product_name'] = product_name
                        visualization_dict['start_date'] = start_date
                        visualization_dict['end_date'] = end_date
                        
                        result_dict = {}
                        result_dict['meta'] = visualization_dict
                        result_dict['rows'] = resultlist
                        
                        response = JsonResponse(result_dict)

    else:
        response = JsonResponse({'code': -1, 'msg': 'params missing'})
        
    response['Access-Control-Allow-Origin'] = '*'
    return response


@login_required
def dashboard(request, template):
    '''get dashboard data'''
    return render(request, template)

@login_required
def retention(request, template):
    return render(request, template)

@login_required
def active(request, template):
    return render(request, template)

@login_required
def revenue(request, template):
    return render(request, template)

def meta(request):
    user = request.user
    try:
        groups = Group.objects.filter(user=user)
    except TypeError:
        groups = None
        
    permissions = []
    view_all_permission = False
    try:
        if groups:
            for group in groups:
                permissions.append(group.name.split('-')[0])
            if ('all' in permissions) or ('super user' in permissions):
                view_all_permission = True
    except Exception:
        pass

    product_id_name = []
    products = ProductIdName.objects.all()
    for product in products:
        if (str(product.product_id) in permissions) or view_all_permission:
            product_id_name.append({'product_name': product.name, 'product_id': product.product_id})
    
    response = HttpResponse(json.dumps(product_id_name))
    response['Access-Control-Allow-Origin'] = '*'
    return response

def get_doc_by_conditions(request):
    conditions = request.GET.get('conditions', '{"query":{"match_all":{}}}')
    conditions = json.loads(conditions)
    storage = StorageEnigne.objects.filter(stype='RESULT',setype='ELASTICSEARCH')[0]
    conf = json.loads(storage.conf)
    
    es_connect = conf.get('connect_settings')
    es_index = conf.get('index_name')
    es_doctype = conf.get('type_name')
    es = Elasticsearch(es_connect)
    
    try:
        esget_resp = es.search(index=es_index, doc_type=es_doctype, body=conditions, sort='ds:asc', size=9999)
    except RequestError:
        return JsonResponse({'code': -2, 'msg': 'elasticsearch requesterror'})
    else:
        hitslist = esget_resp.get('hits', {}).get('hits', None)
        resultlist = [ i.get('_source') for i in hitslist ]
        return JsonResponse({'rows': resultlist})
