#coding=utf-8
import copy
import uuid
from collections import defaultdict


class TableSet(object):
    def __init__(self, source_table, deduplicate_on_core_dimensions=True):
        # self.source_table: could be a real table or a subquery
        self.source_table = source_table
        self.core_dimensions = defaultdict()
        self.core_filters = defaultdict(list)
        self.core_metrics = defaultdict()
        self.deduplicate_on_core_dimensions = deduplicate_on_core_dimensions

        self.analysis_dimensions = []
        self.analysis_grouping_sets = list()
        self.analysis_metrics = defaultdict()

        self.analysis_output_dimensions = []
        self.analysis_output_metrics = []
        self.analysis_output_consts = {}
        self.analysis_base_grouping_items = set()

        self.intersection_layer = 0

    def add_core_dimension(self, core_dimension_name,
                           core_dimension_column,
                           core_dimension_display_name,
                           core_dimension_type='str'):
        """Add a core dimension definition"""
        self.core_dimensions[core_dimension_name] = {
            "core_dimension_column": core_dimension_column,
            "core_dimension_display_name": core_dimension_display_name,
            "core_dimension_type": core_dimension_type
        }

    def add_analysis_dimension(self, name):
        self.analysis_dimensions.append(name)

    def add_analysis_grouping_set(self, grouping_set):
        grouping_set_str = ''
        if isinstance(grouping_set, (tuple, list)):
            _grouping_set = set(grouping_set)
            _grouping_set = tuple(_grouping_set.union(self.analysis_base_grouping_items))
            one_grouping_set_template = ','.join(['{}' for _ in range(len(_grouping_set))])
            one_grouping_set = one_grouping_set_template.format(*_grouping_set)
            grouping_set_str = one_grouping_set.join(['(', ')'])
        elif isinstance(grouping_set, str):
            grouping_set_str = grouping_set
            if self.analysis_base_grouping_items:
                _new_grouping_set = set()
                _new_grouping_set = _new_grouping_set.union(self.analysis_base_grouping_items)
                _new_grouping_set.add(grouping_set)
                _new_grouping_set = tuple(_new_grouping_set)

                one_grouping_set_template = ','.join(['{}' for _ in range(len(_new_grouping_set))])
                one_grouping_set = one_grouping_set_template.format(*_new_grouping_set)
                grouping_set_str = one_grouping_set.join(['(', ')'])
        self.analysis_grouping_sets.append(grouping_set_str)

    def add_core_filter(self, core_filter_dimension_name,
                        core_filter_condition_type,
                        core_filter_condition,
                        core_filter_group='default group'):
        """Add a core filter definition"""
        self.core_filters[core_filter_group].append({
            "core_filter_dimension_name": core_filter_dimension_name,
            "core_filter_condition_type": core_filter_condition_type,
            "core_filter_condition": core_filter_condition
        })

    def remove_core_filter(self, core_filter_dimension_name,
                           core_filter_group='default group'):
        core_filter_list = self.core_filters[core_filter_group]
        new_core_filter_list = []
        for core_filter in core_filter_list:
            _core_filter_dimension_name = core_filter['core_filter_dimension_name']
            if core_filter_dimension_name == _core_filter_dimension_name:
                continue
            new_core_filter_list.append(core_filter)
        self.core_filters[core_filter_group] = new_core_filter_list

    def add_core_metric(self, core_metric_name,
                        core_metric_dimension_name,
                        core_metric_display_name,
                        core_metric_type='COUNT_DISTINCT',
                        core_metric_dimensions=[]):
        """集合本身的度量定义，这些度量定义主要用于衍生出新的维度。
        比如根据单个ip地址上的账号的个数来定义正常用户和非正常用户"""
        self.core_metrics[core_metric_name] = {
            "core_metric_type": core_metric_type,
            "core_metric_dimension_name": core_metric_dimension_name,
            "core_metric_display_name": core_metric_display_name,
            "core_metric_dimensions": core_metric_dimensions
        }

    def shrink_to_dimensions(self, core_dimensions=[], as_name=None):
        if not as_name:
            as_name = 'RAND_TABLE_{}'.format(uuid.uuid4().hex)
        new_source_table = self.core_sql().join(['(', ')']) + ' AS {}'.format(as_name)
        shrinked_table_set = TableSet(source_table=new_source_table)
        for core_dimension_name in core_dimensions:
            shrinked_table_set.add_core_dimension(core_dimension_name,
                                                  core_dimension_name,
                                                  self.core_dimensions[core_dimension_name]['core_dimension_display_name'],
                                                  self.core_dimensions[core_dimension_name]['core_dimension_type'])
        shrinked_table_set.core_filters = defaultdict()
        shrinked_table_set.core_metrics = defaultdict()
        return shrinked_table_set

    def add_analysis_metric(self, analysis_metric_name,
                            analysis_metric_dimension_name,
                            analysis_metric_display_name,
                            analysis_metric_type='COUNT_DISTINCT',
                            hook=None):
        self.analysis_metrics[analysis_metric_name] = {
            "analysis_metric_type": analysis_metric_type,
            "analysis_metric_dimension_name": analysis_metric_dimension_name,
            "analysis_metric_display_name": analysis_metric_display_name,
            "analysis_metric_hook": hook
        }

    def add_analysis_output_const(self, key, value):
        self.analysis_output_consts[key] = value

    def add_analysis_base_grouping_item(self, analysis_base_grouping_item):
        self.analysis_base_grouping_items.add(analysis_base_grouping_item)
    
    def new_tableset_from_analysis_sql(self, as_name=None):
        
        if not as_name:
            as_name = 'RAND_TABLE_{}'.format(uuid.uuid4().hex)
        
        source_table = self.analysis_sql().join(['(', ')']) + 'AS {}'.format(as_name)
        new_set = TableSet(source_table=source_table)
        return new_set
    
    def new_tableset_from_core_sql(self, as_name=None):
        
        if not as_name:
            as_name = 'RAND_TABLE_{}'.format(uuid.uuid4().hex)
        
        source_table = self.core_sql().join(['(', ')']) + 'AS {}'.format(as_name)
        new_set = TableSet(source_table=source_table)
        return new_set
    
    def intersection(self, other,
                     on=[],
                     extra_dimensions=[]):
        """用sql联接模拟集合的交集操作，并可能派生出新的维度到返回的集合中"""
        self_core_sql = self.core_sql()
        other_core_sql = other.core_sql()

        self_table_alias = 'SELF_{}'.format(self._get_intersection_layer())
        other_table_alias = 'OTHER_{}'.format(other._get_intersection_layer())

        self_table = self_core_sql.join(['(', ')']) + ' AS {}'.format(self_table_alias)
        other_table = other_core_sql.join(['(', ')']) + ' AS {}'.format(other_table_alias)
        
        core_table = '\nJOIN\n'.join([self_table, other_table])

        on_clause = ''
        on_units = []
        for each_on in on:
            self_on = '.'.join([self_table_alias, each_on])
            other_on = '.'.join([other_table_alias, each_on])
            on_cell = ' = '.join([self_on, other_on])
            on_units.append(on_cell)
        if on_units:
            on_clause = 'ON {}'.format(' AND\n'.join(on_units))
        intersection_table = '\n'.join([core_table, on_clause])
        intersection_table_set = TableSet(source_table=intersection_table)

        for core_dimension in self.core_dimensions:
            core_dimension_column = '.'.join([self_table_alias, core_dimension])
            intersection_table_set.add_core_dimension(core_dimension,
                                                      core_dimension_column,
                                                      self.core_dimensions[core_dimension]['core_dimension_display_name'])

        # {
        # 'name': 'retention_days',
        # 'def': 'datediff({self_table_alias}.ds, {other_table_alias}.ds)',
        # 'display_name': '活跃留存天数'
        # }
        for extra_dimension in extra_dimensions:
            intersection_table_set.add_core_dimension(extra_dimension['name'],
                                                      extra_dimension['def'].format(**{'self_table_alias': self_table_alias,
                                                                                       'other_table_alias': other_table_alias}),
                                                      extra_dimension['display_name'])

        #  返回新的数据集
        return intersection_table_set
    
#     def substraction(self, other, on=[], extra_dimensions=[]):
#         '''用sql模拟集合的减法操作，并可能派生出新的维度到返回的集合中'''
#         self_core_sql = self.core_sql()
#         other_core_sql = other.core_sql()
#         self_table_alias = 'SELF_{}'.format(self._get_intersection_layer())
#         other_table_alias = 'OTHER_{}'.format(other._get_intersection_layer())
#         self_table = self_core_sql.join(['(', ')']) + ' AS {}'.format(self_table_alias)
#         other_table = other_core_sql.join(['(', ')']) + ' AS {}'.format(other_table_alias)
#         
#         core_table = '\nFULL OUTER JOIN\n'.join([self_table, other_table])
#         on_clause = ''
#         on_units = []
#         for each_on in on:
#             self_on = '.'.join([self_table_alias, each_on])
#             other_on = '.'.join([other_table_alias, each_on])
#             on_cell = ' = '.join([self_on, other_on])
#             on_units.append(on_cell)
#         if on_units:
#             on_clause = 'ON {}'.format(' AND\n'.join(on_units))
#         substraction_table = '\n'.join([core_table, on_clause])
#         substraction_table_set = TableSet(source_table=substraction_table)
# 
#         for core_dimension in self.core_dimensions:
#             core_dimension_column = '.'.join([self_table_alias, core_dimension])
#             substraction_table_set.add_core_dimension(core_dimension,
#                                                       core_dimension_column,
#                                                       self.core_dimensions[core_dimension]['core_dimension_display_name'])
# 
#         for extra_dimension in extra_dimensions:
#             substraction_table_set.add_core_dimension(extra_dimension['name'],
#                                                       extra_dimension['def'].format(**{'self_table_alias': self_table_alias,
#                                                                                        'other_table_alias': other_table_alias}),
#                                                       extra_dimension['display_name'])
# 
#         #  返回新的数据集
#         return substraction_table_set    
                
        
    def core_sql(self):
        """核心sql用来代表本集合定义"""
        select_clause = self._core_select_clause()
        from_clause = self._core_from_clause()
        where_clause = self._core_where_clause()
        groupby_clause = self._core_groupby_clause()
        sql_components = [select_clause, from_clause, where_clause, groupby_clause]
        sql_components = [sql_component for sql_component in sql_components if sql_component]
        return '\n'.join(sql_components)

    def analysis_sql(self):
        """最终构建出的分析sql语句"""
        sql_components = [self._analysis_select_clause(),
                          self._analysis_from_clause(),
                          self._analysis_groupby_clause(),
                          self._analysis_grouping_sets_clause()]
        return '\n'.join(sql_components)

    def _analysis_grouping_sets_clause(self):
        grouping_sets_clause = ''
        if self.analysis_grouping_sets:
            a = ', '.join(self.analysis_grouping_sets)
            b = a.join(['(', ')'])
            grouping_sets_clause = 'GROUPING SETS {}'.format(b)
        return grouping_sets_clause

    def _get_intersection_layer(self):
        current_layer = self.intersection_layer
        self.intersection_layer += 1
        return current_layer

    def _core_select_clause(self):
        """构建出核心集合的select子句"""
        selectors = []
        select_clause = ''
        for core_dimension_name in self.core_dimensions:
            core_dimension_cell = (self.core_dimensions[core_dimension_name]['core_dimension_column'], core_dimension_name)
            core_dimension_cell_str = ' AS '.join(core_dimension_cell)
            selectors.append(core_dimension_cell_str)
        
        for core_metric_name in self.core_metrics:
            core_metric = self.core_metrics[core_metric_name]
            if core_metric['core_metric_type'] == 'WINDOWING':
                self.deduplicate_on_core_dimensions = False
                core_metric_cell = (core_metric['core_metric_dimension_name'], core_metric_name)
                core_metric_cell_str = ' AS '.join(core_metric_cell)
                selectors.append(core_metric_cell_str)
        
        if selectors:
            select_clause = 'SELECT ' + ',\n'.join(selectors)
        return select_clause

    def _analysis_select_clause(self):
        selectors = []
        select_clause = ''
        for analysis_dimension_name in self.analysis_dimensions:
            self.analysis_output_dimensions.append(analysis_dimension_name)
            core_dimension_cell = (analysis_dimension_name,
                                   analysis_dimension_name)
            core_dimension_cell_str = ' AS '.join(core_dimension_cell)
            selectors.append(core_dimension_cell_str)

        if self.analysis_grouping_sets:
            self.analysis_output_dimensions.append('gid')
            grouping_id_str = 'GROUPING__ID AS gid'
            selectors.append(grouping_id_str)

        for analysis_metric_name in self.analysis_metrics:
            self.analysis_output_metrics.append(analysis_metric_name)
            analysis_metric = self.analysis_metrics[analysis_metric_name]
            analysis_metric_type = analysis_metric['analysis_metric_type']
            analysis_metric_dimension_name = analysis_metric['analysis_metric_dimension_name']

            metric_str = None
            if analysis_metric_type == 'COUNT_DISTINCT':
                metric_str = 'COUNT(DISTINCT {})'.format(analysis_metric_dimension_name)
            elif analysis_metric_type == 'COUNT':
                metric_str = 'COUNT({})'.format(analysis_metric_dimension_name)
            elif analysis_metric_type == 'SUM':
                metric_str = 'SUM({})'.format(analysis_metric_dimension_name)
            elif analysis_metric_type == 'AVG':
                metric_str = 'AVG({})'.format(analysis_metric_dimension_name)
            elif analysis_metric_type == 'MAX':
                metric_str = 'MAX({})'.format(analysis_metric_dimension_name)
            elif analysis_metric_type == 'MIN':
                metric_str = 'MIN({})'.format(analysis_metric_dimension_name) 
            elif analysis_metric_type.startswith('PERCENTILE'):
                pass
            else:
                raise
            metric_cell = (metric_str, analysis_metric_name)
            metric_selector = ' AS '.join(metric_cell)
            selectors.append(metric_selector)

        # resolve the grouping__id bug
        self.analysis_output_metrics.append('dummy')
        metric_cell = ('COUNT(1)', 'dummy')
        metric_selector = ' AS '.join(metric_cell)
        selectors.append(metric_selector)

        if selectors:
            select_clause = 'SELECT ' + ', \n'.join(selectors)
        return select_clause

    def _analysis_groupby_clause(self):
        groupby_clause = ''
        analysis_groupby_columns = []
        for core_dimension in self.analysis_dimensions:
            analysis_groupby_columns.append(core_dimension)
        if analysis_groupby_columns:
            core_groupby_str = ',\n'.join(analysis_groupby_columns)
            groupby_clause = 'GROUP BY ' + core_groupby_str
        return groupby_clause

    def _core_from_clause(self):
        return 'FROM ' + self.source_table

    def _analysis_from_clause(self):
        return 'FROM ' + self.core_sql().join(['(', ')']) + ' AS ANALYSIS_TABLE'

    def _core_where_clause(self):
        where_clause = ''
        where_groups = []
        for core_filter_group in self.core_filters:
            current_filter_group = self.core_filters[core_filter_group]
            filters = []
            for _filter in current_filter_group:
                core_filter_condition_type = _filter['core_filter_condition_type']
                core_filter_dimension_name = _filter['core_filter_dimension_name']
                core_filter_condition = _filter['core_filter_condition']

                core_dimension_column = self.core_dimensions[core_filter_dimension_name]['core_dimension_column']
                core_dimension_type = self.core_dimensions[core_filter_dimension_name]['core_dimension_type']

                core_condition_unit_str = ''
                if core_filter_condition_type.lower() == 'in':
                    core_filter_condition_cell = tuple(core_filter_condition)
                    core_condition_unit_str = ' IN '.join([core_dimension_column, str(core_filter_condition_cell)])
                elif core_filter_condition_type.lower() == 'in_function':
                    core_filter_condition_values_template = ', '.join(['{}' for _ in range(len(core_filter_condition))])
                    core_condition_unit_str = ' IN '.join(core_dimension_column,
                                                          core_filter_condition_values_template.format(*core_filter_condition))
                elif core_filter_condition_type.lower() == 'equal':
                    core_condition_unit_str = ' = '.join([core_dimension_column, '{!r}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'equal_function':
                    core_condition_unit_str = ' = '.join([core_dimension_column, '{}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'between':
                    core_condition_unit_str = ' AND '.join(core_filter_condition)
                    core_condition_unit_str = ' BETWEEN '.join([core_dimension_column, core_condition_unit_str])
                elif core_filter_condition_type.lower() == 'between_function':
                    core_filter_condition_values_template = ' AND '.join(['{}' for _ in range(len(core_filter_condition))])
                    core_condition_unit_str = core_filter_condition_values_template.format(*core_filter_condition)
                    core_condition_unit_str = ' BETWEEN '.join([core_dimension_column, core_condition_unit_str])
                elif core_filter_condition_type.lower() == 'gt':
                    core_condition_unit_str = ' > '.join([core_dimension_column, '{}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'gt_function':
                    core_condition_unit_str = ' > '.join([core_dimension_column, '{!r}'.format(core_filter_condition)])    
                elif core_filter_condition_type.lower() == 'gte':
                    core_condition_unit_str = ' >= '.join([core_dimension_column, '{}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'gte_function':
                    core_condition_unit_str = ' >= '.join([core_dimension_column, '{!r}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'lte':
                    core_condition_unit_str = ' <= '.join([core_dimension_column, '{}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'lte_function':
                    core_condition_unit_str = ' <= '.join([core_dimension_column, '{!r}'.format(core_filter_condition)])
                elif core_filter_condition_type.lower() == 'null':
                    core_condition_unit_str = 'IS NULL'
                elif core_filter_condition_type.lower() == 'not_null':
                    core_condition_unit_str = 'IS NOT NULL'
                else:
                    raise RuntimeError('not supported condition type')
                filters.append(core_condition_unit_str)
            core_condition_str = '\nAND '.join(filters)
            core_condition_str = core_condition_str.join(['(', ')'])
            where_groups.append(core_condition_str)

        if where_groups:
            where_clause = 'WHERE ' + ' OR '.join(where_groups)
        return where_clause

    def _core_groupby_clause(self):
        groupby_clause = ''
        if self.deduplicate_on_core_dimensions:
            core_groupby_columns = []
            for core_dimension in self.core_dimensions:
                core_groupby_columns.append(self.core_dimensions[core_dimension]['core_dimension_column'])
            if core_groupby_columns:
                core_groupby_str = ',\n'.join(core_groupby_columns)
                groupby_clause = 'GROUP BY ' + core_groupby_str
        return groupby_clause

    def copy(self):
        new_set = TableSet(source_table=self.source_table)
        new_set.core_dimensions = copy.deepcopy(self.core_dimensions)
        new_set.core_filters = copy.deepcopy(self.core_filters)
        return new_set
