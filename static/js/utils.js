// 代表图表的类
var FrontendData2 = function(backendData) {
		var self = this;

		self.title = backendData['title']; // 本数据的标题
		self.subTitle = backendData['subtitle']; // 本数据的副标题
		self.seriesColumns = new Set(['value']); // 本对象中所有的待观察的数据序列，所对应的列的名字,默认为value字段
		
		self.originalData = backendData['rows']; // 后端返回的原始数据
		self.metaData = backendData['meta'];  // 关于原始数据的描述
		self.graphConfig = backendData['graph']; // 图表配置
		
		// 构建出列和其名字的映射关系
		self.columns = backendData['columns'];
		self.columnNames = backendData['columnNames'];
		self.columnTypes = backendData['types'];
		
		self.columnNameMapping = {}
		for (var index in self.columns) {
			self.columnNameMapping[self.columns[index]] = self.columnNames[index]; // 构建列和其显示名字的映射关系,方便在本对象中使用
		}
		
		self.dimensionList = [] // 从self.columns提取出所有的维度信息
		self.columns.forEach(function(column){
			if  (column != 'value') {
				self.dimensionList.push(column); // 后端返回的数据中，除value，所有其它字段都是维度列表的一部分
			}
		});
		self.dimensionList.sort();
		
		self.vCombinable = true; // 当前对象是否还允许垂直拼接
		
		// 原始数据经过处理之后的数据及其相关元数据
		self.processedData = {};  //  按照各维度值的组合进行分类，每一分类下分别有其对应的【上下文信息】和具体的数据【列表】
		self.processedColumns = [];
		self.processedColumnNames = [];
		self.processedColumnNameMapping = {};
		
		self.transposedDimensions = [];
		self.contextColumnMapping = {}; // 作为上下文而存在的列名
		self.contextProcessor = null;
		
		// 将后端数据先处理成统一格式的数据，方便后续使用
		self.processOriginalData = function() {
			self.processedData = {}; // 应对合并造成的重复问题
			self.originalData.forEach(function(td) {
				// 首先组合出对应的分类名
				var categoryValueCells = [];
				self.dimensionList.forEach(function(dimensionName) {
					categoryValueCells.push(td[dimensionName]);
				});
				var categoryKey = categoryValueCells.join("$$");
				
				// 进行必要的初始化，并将数据格式转换成统一的格式
				if ( !(categoryKey in self.processedData) ) {
					self.processedData[categoryKey] = {}; // 初始化分类下的值
				}
				
				self.processedData[categoryKey] = td; // 将真实的数据压入容器
			});
			
			// 处理后的数据也有对应的列和其显示名的映射，这个映射要重要于原始数据的映射，因为后续的显示都是基于处理后的数据和其相关信息的
			self.processedColumns = self.columns;
			self.processedColumnNames = self.columnNames;
			for (var index in self.processedColumns) {
				self.processedColumnNameMapping[self.processedColumns[index]] = self.processedColumnNames[index];
			}
		};
		self.processOriginalData(); // 构建处理后的数据，可将其看成是构造函数，一旦调用外部函数便会组织成新的数据格式
		
		// 垂直拼接，只限定于【原始数据】
		self.vCombine = function(otherData) {
			
			if (!self.vCombinable) {
				console.log("V must be called before hCombine");
				return;
			}
			
			var selfRefer = self.metaData['refer'];
			var otherRefer = otherData.metaData['refer'];
			
			if (selfRefer != otherRefer) {
				console.log("different refer are not V combinable");
				return;
			}
			
			if (self.dimensionList.length != otherData.dimensionList.length) {
				console.log("data with different [length] dimensionList are not V combinable");
				return; // 如果维度数量都不一样，直接返回
			} else {
				for (var index in self.dimensionList) { // 确保所关注的维度列表也是一样的
					if (self.dimensionList[index] != otherData.dimensionList[index]) {
						console.log("data with different [content] dimensionList are not V combinable");
						return;
					}
				}
			}
			
			self.originalData = self.originalData.concat(otherData.originalData); // 只限定于原始数据！！！！！
			self.processOriginalData(); // 刷新数据
		};
		
		// 水平拼接，可级联调用，扩展self.seriesColumns；
		self.hCombine = function(otherData, asContext=null) {
			self.vCombinable = false; // 水平拼接调用之后，禁止垂直拼接，因为会覆盖处理好的数据
			
			var selfRefer = self.metaData['refer'];
			var otherRefer = otherData.metaData['refer'];
			if (self.dimensionList.length != otherData.dimensionList.length) {
				console.log("data with different [length] dimensionList are not H combinable");
				return; // 如果维度数量都不一样，直接返回
			} else {
				for (var index in self.dimensionList) { // 确保所关注的维度列表也是一样的
					if (self.dimensionList[index] != otherData.dimensionList[index]) {
						console.log("data with different dimensionList [content] are not H combinable");
						return;
					}
				}
			}
			
			otherNewColumn = otherRefer;
			otherNewColumnName = otherData.title;
			self.processedColumnNameMapping[otherNewColumn] = otherNewColumnName;
			self.seriesColumns.add(otherNewColumn);
			
			if (asContext) {
				self.contextColumnMapping[asContext] = {}
				self.contextColumnMapping[asContext]['name'] = otherNewColumn; // 上下文的键和具体的列名之间的对应关系，需要在变化时维护好
				self.contextColumnMapping[asContext]['dimensionCutAt'] = self.transposedDimensions.length;
			}
			
			for (var categoryKey in self.processedData) { // 为自己的每一行数据水平拼接外部数据
				if (categoryKey in otherData.processedData) {
					self.processedData[categoryKey][otherNewColumn] = otherData.processedData[categoryKey]['value'];
				} else {
					self.processedData[categoryKey][otherNewColumn] = null;
				}
			}
		};
		
		// 数据转置
		self.transpose = function(dimensionNames) {
			var allNewseriesColumns = new Set(); // 转置完全会重置数值序列的布局
			var allNewDimensionList = []; 
			self.dimensionList.forEach(function(dimensionName) {
				if (dimensionNames.indexOf(dimensionName) < 0) { // 如果其不在转置维度列表中，才能够继续用作组织数据分类名的依据
					allNewDimensionList.push(dimensionName);
				}
			});
			self.dimensionList = allNewDimensionList; // 更新维度列表
			
			dimensionNames.forEach(function(dimensionName) {
				self.transposedDimensions.push(dimensionName);
			});
			
			var allNewData = {}; // 其分类名在转置之后会萎缩，用全新的allNewDimensionList去组织新的分类名
			for (var categoryValue in self.processedData) { // 每次循环新一条数据都可能会产生新的列
				var currentData = self.processedData[categoryValue];
				
				var newColumnCells = [];
				var newColumnNameCells = [];
				dimensionNames.forEach(function(dimensionName) { // 遍历所有需要转置的维度，从当前的这条数据中组织出新的分类名称
					if (dimensionName in currentData) {
						var dimensionValue = currentData[dimensionName];
						newColumnCells.push(dimensionValue);
						newColumnNameCells.push([self.processedColumnNameMapping[dimensionName], dimensionValue]);
					} else {
						newColumnNameCells.push([self.processedColumnNameMapping[dimensionName], null]);
					}
				});
				
				var newColumnPrefix = newColumnCells.join("_"); // 生成列前缀
				var _bridgeCells = []
				newColumnNameCells.forEach(function(pair){
					_bridgeCells.push(pair.join("="));
				});
				var newColumnNamePrefix = _bridgeCells.join("&"); // 列名前缀
				
				// 计算缩水后的分类名
				var newCategoryCells = [];
				self.dimensionList.forEach(function(newDimensionName){
					newCategoryCells.push(currentData[newDimensionName]);
				});
				var newCategoryKey = newCategoryCells.join("$$");
				// 填充此新的分类名下的值
				self.seriesColumns.forEach(function(seriesColumn) { // 遍历当前的所有的值列
					var currentValue = currentData[seriesColumn]; // 当前的值
					var newColumn = [newColumnPrefix, seriesColumn].join("$$"); 
					var newColumnName = [newColumnNamePrefix, self.processedColumnNameMapping[seriesColumn]].join("／");
					allNewseriesColumns.add(newColumn); // 添加新的数据系列
					self.processedColumnNameMapping[newColumn] = newColumnName; // 将新的列和其列名添加到公共位置供后续查询使用
					
					if ( !(newCategoryKey in allNewData) ) {
						allNewData[newCategoryKey] = {};
					}
					allNewData[newCategoryKey][newColumn] = currentValue;
				});
				
				// 在覆盖原数据之前，先将保留下来的维度的相关的值写入数据中，以保持数据的一致性
				self.dimensionList.forEach(function(dimensionName) {
					allNewData[newCategoryKey][dimensionName] = currentData[dimensionName];
				});
			}
			self.processedData = allNewData;
			self.seriesColumns = allNewseriesColumns // 数据序列定义更新
		};
		
		self.doEvolution = function() { // 根据目前的上下文演化出各种概念
			self.transposedDimensions.reverse();
			
			for (var categoryKey in self.processedData) {
				var categoryValue = self.processedData[categoryKey];
				var contextKeyValues = {};
				var dataKeyValues = {};
				var dimensionKeyValues = {};
				var dataContextMapping = {}; //  数据和其上下文的对应关系
				
				for (var dataKey in categoryValue) { //  第一次循环，将上下文字段和数据字段分离开来
					
					if (self.dimensionList.indexOf(dataKey) >= 0) { // 如果是维度字段，添加到维度字典中，结束循环
						dimensionKeyValues[dataKey] = categoryValue[dataKey];
						continue;
					}
					var dataKeyCells = dataKey.split("$$");
					var dataKeyClass = dataKeyCells[dataKeyCells.length-1];
					if (dataKeyClass in self.contextColumnMapping) { 
						contextKeyValues[dataKey] = categoryValue[dataKey];
					} else {
						dataKeyValues[dataKey] = categoryValue[dataKey];
					}
				}
				
				for (var dataKey in dataKeyValues) { // 为每个数据找到其对应的上下文信息
					var dataValue = dataKeyValues[dataKey];
					var dataKeyCells = dataKey.split("$$");
					
					for (var contextKey in self.contextColumnMapping) {
						var contextDefination = self.contextColumnMapping[contextKey];
						var contextCutAt = contextDefination['dimensionCutAt'];
						
						var _myContextKey = [dataKeyCells.slice(0, dataKeyCells.length - 1 - contextCutAt), contextKey].join("$$");
						var _myContextValue = contextKeyValues[_myContextKey];
						console.log(self.transposedDimensions, dataKey, dataValue, _myContextKey, _myContextValue, contextKey);
						
						if (self.contextProcessor) {
							var contextProcessorResult = self.contextProcessor(self.transposedDimensions, dataKey, dataValue, _myContextKey, _myContextValue, contextKey);
							
//							self.title = contextProcessorResult['title'];
//							self.subTitle = contextProcessorResult['subTitle'];
							self.processedData[categoryKey][contextProcessorResult['refer']] = contextProcessorResult['value'];
							self.seriesColumns.add(contextProcessorResult['refer']);
							self.processedColumnNameMapping[contextProcessorResult['refer']] = contextProcessorResult['title'];
							
							console.log(contextProcessorResult);
						}
						
//						console.log("context for " + dataKey + " " + contextKey + " is " + [dataKeyCells.slice(0, dataKeyCells.length - 1 - contextCutAt), contextKey].join("$$"));
					}
					
				}
				
				console.log("======");
				console.log(dimensionKeyValues)
				console.log(contextKeyValues);
				console.log(dataKeyValues);
				console.log("======");
				
				
			}
		};
		
		self.show = function() { // 渲染图和表的显示
			self.contextProcessor = function(transposedDimensions, dataKey, dataValue, contextKey, contextValue, contextKey) {
				var dataKeyCells = dataKey.split("$$");
				var dimensionValueMapping = {};
				for (var index in transposedDimensions) {
					dimensionValueMapping[transposedDimensions[index]] = dataKeyCells[index];
				}
				
				console.log(dimensionValueMapping, '.................');
				
				if (contextKey == 'dnu') {
					var title = null;
					var subTitle = null;
					
					if (dimensionValueMapping['lc_num'] == '1') {
						title = '次日留存率';
						subTitle = '次日留存率';
					} else {
						title = "渠道" + dimensionValueMapping['channelid'] + "的" +  dimensionValueMapping['lc_num'] + '天留存率';
					}
					
					return {
						value: parseInt((dataValue / contextValue) * 100),
						title: title,
						subTitle: subTitle,
						refer: dataKey + "_rate",
					}
				}
			}
			self.doEvolution();
		};
		
		self.renderGraph = function() {
			renderTo = "test_graph";
			var categories = [];
			for (var dataKey in self.processedData) {
				categories.push(dataKey);
			}
			categories.sort();
			var chart = Highcharts.chart(renderTo, {});
			chart.setTitle({text: self.title}, {text: self.subTitle});
			
			// 删除当前X轴和Y轴
			allAxises = chart.xAxis.concat(chart.yAxis);
			for(axisIndex in allAxises){
				Axis = allAxises[axisIndex];
				Axis.remove();
			}
			
			// 添加配置中的X轴
			for (xAxisIndex in self.graphConfig['xAxises']) {
				var xAxis = self.graphConfig['xAxises'][xAxisIndex];
				var xAxisTitle = xAxis['title']; // 此X轴上要显示的描述
				var	opposite = 'opposite' in xAxis ? xAxis['opposite'] : false; // 是否对换轴的位置
				
				chart.addAxis({
					id: 'X' + xAxisIndex,
					title : {
						text: xAxisTitle,
					},
					opposite: opposite,
				}, true, true);
			}
			
			// 添加配置中的Y轴
			for(yAxisIndex in self.graphConfig['yAxises']) {
				var yAxis = self.graphConfig['yAxises'][yAxisIndex];
				var yAxisSourceColumn = yAxis['sourceColumn'];
				var yAxisTitle = yAxis['title'];
				var	opposite = 'opposite' in yAxis ? yAxis['opposite'] : false;
				
				chart.addAxis({
					id: 'Y' + yAxisIndex,
					title : {
						text: yAxisTitle,  
					},
					opposite: opposite,
				}, false, true);
			}
			
			// 添加具体数据，可能包含多个数据序列
			var allSeries = [];
			self.seriesColumns.forEach(function(seriesColumn) {
				var series = {
						name: self.processedColumnNameMapping[seriesColumn], //  当前数据序列的名称
						type: 'line',
						xAxis: 'X0',
						yAxis: 'Y0',
						visible:true,
						data: [],
				};
				
				categories.forEach(function(category) {
					var currentCategory = self.processedData[category];
					if (seriesColumn in currentCategory) {
						series['data'].push(currentCategory[seriesColumn]);
					} else {
						series['data'].push(null);
					}
				});
				
				allSeries.push(series);
			});
			
			var xAxis = chart.get('X0');
			xAxis.setCategories(categories);
			allSeries.forEach(function(item) {
				console.log(item)
				console.log('+++++++++++++++')
				chart.addSeries(item);
			});
		};
};