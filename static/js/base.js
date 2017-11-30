var setLocalValue = function(k, v) {
	try {
		window.localStorage.setItem(k, v);
	} catch (e) {
		console.log(e);
	}
};

var getLocalValue = function(k) {
	try{
		return window.localStorage.getItem(k);
	} catch (e) {
		console.log(e);
	}
};

// 代表图表的类
var FrontendData = function(backendData) {
		var self = this;

		self.title = backendData['title'];
		self.subTitle = backendData['subtitle'];
		self.categoryColumn = backendData['categoryColumn'];
		self.seriesColumns = [];
		
		self.originalData = backendData['rows']; // 后端返回的原始数据
		self.metaData = backendData['meta'];  // 关于原始数据的描述
		self.graphConfig = backendData['graph']; // 图表配置
		
		// 构建出列和其名字的映射关系
		self.columns = backendData['columns'];
		self.columnNames = backendData['columnNames'];
		self.columnTypes = backendData['types'];
		self.columnNameMapping = {}
		for (index in self.columns) {
			self.columnNameMapping[self.columns[index]] = self.columnNames[index]; // 构建列和其显示名字的映射关系,方便后续的使用
		}
		
		self.processedData = {}; // 原始数据经过处理之后的数据
		self.processedColumns = [];
		self.processedColumnNames = [];
		self.processedColumnNameMapping = {};
		self.combinationData = [];
		self.combinationPolicy = {};
		
		self.globalConfig = {} //全局的数据布局调整信息，比如如何用行信息转成列
		
		self.processOriginalData = function() {
			self.originalData.forEach(function(td){
				var category = td[self.categoryColumn];
				if ( !(category in self.processedData) ) {
					self.processedData[category] = {};
				}
				
				if ( !('data' in self.processedData[category]) ) {
					self.processedData[category]['data'] = [];
				}
				
				if ( !('context' in self.processedData[category]) ) {
					self.processedData[category]['context'] = {};
				}
				
				self.processedData[category]['data'].push(td);
			})
		};
		self.processOriginalData(); // 构建处理后的数据，可将其看成是构造函数，一旦调用外部函数便会组织成新的数据格式
		
		// 添加组合数据，用于组合不同的数据集合
		self.addCombinationData = function(otherData) {
			for (var categoryKey in self.processedData) {
				if (categoryKey in otherData.processedData) {
					var otherDataValues = otherData.processedData[categoryKey]['data'];
					otherDataValues.forEach(function(data){
						self.processedData[categoryKey]['data'].push(data);
					});
				}
			}
		};
		
		// 添加上下文数据，对于相应category下的数据有辅助计算的作用
		self.addCombinationContextData = function(otherData) {
			var otherRefer = otherData.metaData['refer'];
			for (var categoryKey in self.processedData) {
				if (categoryKey in otherData.processedData) {
					var contextData = otherData.processedData[categoryKey];
					self.processedData[categoryKey]['context'][otherRefer] = contextData;
				}
			}
		};
		
		// 添加全局的数据布局调整信息，比如如何用行信息转成列
		self.addGlobalConfig = function(k, v) {
			self.globalConfig[k] = v;
		}
		
		// 处理全局设置，务必在添加完所有设置之后再调用此方法
		self.processGlobalConfig = function () {
			// 如果要覆盖本数据对象的分类列的名字则提供相应的回调函数
			var categoryNameCallback = 'categoryNameCallback'; 
			var _categoryNameCallback = function(item) {
				return item;
			};
			if (categoryNameCallback in self.globalConfig) {
				_categoryNameCallback = self.globalConfig[categoryNameCallback];
			}
			self.processedColumnNameMapping[self.categoryColumn] = _categoryNameCallback(self.columnNameMapping[self.categoryColumn]); // 分类列的名字更新
			
			// 转置相关配置
			var transpositionDimension = 'transpositionDimension';
			var transpositionColumnNameCallback = 'transpositionColumnNameCallback';
			
			if (transpositionDimension in self.globalConfig) {
				var _transpositionDimension = self.globalConfig[transpositionDimension]; // 从哪个维度转置
				var _transpositionColumnNameCallback = function (item) { // 默认的回调函数，用来生成转置后生成的新的列名
					return item;
				}
				
				if (transpositionColumnNameCallback in self.globalConfig) { // 如果指定了列名生成函数，则覆盖默认的生成函数
					_transpositionColumnNameCallback = self.globalConfig[transpositionColumnNameCallback];
				}
				
				var transpositionDatas = [];
				for (var categoryKey in self.processedData) {
					var transpositionData = {}; // 每条数据转置后的具体数据
					var categoryValue = self.processedData[categoryKey];
					transpositionData[self.categoryColumn] = categoryKey; // 首先填充对应的category的值
					
					categoryValue['data'].forEach(function(item) {
						var transpositionColumnValue = item[_transpositionDimension]; // 获取到转置列的值
						if ( !(transpositionColumnValue in self.processedColumnNameMapping) ) {
							var transpositionColumnName = _transpositionColumnNameCallback(transpositionColumnValue); // 从转置列的值生成对应的列名
							self.processedColumnNameMapping[transpositionColumnValue] = transpositionColumnName;
							self.seriesColumns.push(transpositionColumnValue); // 一个新的值列，对应了图表中单独的一条线，或者一组柱
						}
						transpositionData[transpositionColumnValue] = item['value']; // 为对应的值列进行赋值
						transpositionDatas.push(transpositionData);
					});
				}
				self.processedData[categoryKey]['data'] = transpositionDatas;
			}
			
			if (self.seriesColumns.length == 0) {
				self.seriesColumns.push('value'); // 如果没有经过任何操作
			}
			
		};
		
		self.renderGraph = function() {
			var renderTo = self.metaData['refer'] + "_graph";
			renderTo = "test_graph";
			var categories = [];
			for (var dataKey in self.processedData) {
				categories.push(dataKey);
				//categories.push(self.processedData[dataKey]['data'][self.categoryColumn]);
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
				var	opposite = 'opposite' in xAxis ? xAxis['opposite'] : false; // 是否兑换轴的位置
				
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
			for (seriesColumnIndex in self.seriesColumns) {
				seriesColumn = self.seriesColumns[seriesColumnIndex];
				var series = {
						name: self.processedColumnNameMapping[seriesColumn], //  当前数据序列的名称
						type: 'line',
						xAxis: 'X0',
						yAxis: 'Y0',
						data: [],
				};
				
				categories.forEach(function(category) {
					var currentCategory = self.processedData[category];
					if (seriesColumn in currentCategory['data']) {
						series['data'].push(currentCategory['data'][seriesColumn]);
					} else {
						series['data'].push(null);
					}
				});
				
				allSeries.push(series);
			}
			
			console.log(allSeries);
			
			var xAxis = chart.get('X0');
			xAxis.setCategories(categories);
			allSeries.forEach(function(item) {
				chart.addSeries(item);
			});
		}
};

// 渲染图表的类
var renderGraph = function(data) {
	var self = this;
	
	self.renderTo = data['graphDomID'];
	self.refer = data['meta']['refer'];
	self.productId = data['meta']['product_id'];
	self.productName = data['meta']['product_name'];
	
	self.orignalData = data['rows']; // 原始数据
	
	// 横向、纵向对比数据
	self.compare = function(other, type){ 
	};
	
	// 组合数据，用来生成新的数据指标定义，典型代表就是更具某天的注册用户数量，和这批用户的次日留存用户数量，计算其次日留存率
	self.combine = function(other) {
	};
	
	var title = data['graph']['title']; // 图表标题
	var subtitle = data['graph']['subtitle']; // 图表子标题
	
	self.chart = Highcharts.chart(self.renderTo, {}); // 渲染到对应DOM ID的位置
	self.chart.setTitle({text: title}, {text: subtitle}); // 显示标题和副标题
	
	// 删除当前X轴和Y轴
	allAxises = self.chart.xAxis.concat(self.chart.yAxis);
	for(axisIndex in allAxises){
		Axis = allAxises[axisIndex];
		Axis.remove();
	}
	
	// 添加配置中的X轴
	for (xAxisIndex in data['graph']['xAxises']){
		var xAxis = data['graph']['xAxises'][xAxisIndex];
		var xAxisTitle = xAxis['title']; // 此X轴上要显示的描述
		var	opposite = 'opposite' in xAxis ? xAxis['opposite'] : false; // 是否兑换轴的位置
		
		self.chart.addAxis({
			id: 'X' + xAxisIndex,
			title : {
				text: xAxisTitle,
			},
			opposite: opposite,
		}, true, true);
	}
	
	// 添加配置中的Y轴
	for(yAxisIndex in data['graph']['yAxises']){
		var yAxis = data['graph']['yAxises'][yAxisIndex];
		var yAxisSourceColumn = yAxis['sourceColumn'];
		var yAxisTitle = yAxis['title'];
		var	opposite = 'opposite' in yAxis ? yAxis['opposite'] : false;
		
		self.chart.addAxis({
			id: 'Y' + yAxisIndex,
			title : {
				text: yAxisTitle,  
			},
			opposite: opposite,
		}, false, true);
	}
	
	// 添加具体数据，可能包含多个数据序列
	for (var seriesIndex in data['graph']['series']) {
		var seriesConfig = data['graph']['series'][seriesIndex];
		var seriesColumn = seriesConfig['seriesColumn'];
		var seriesName = seriesConfig['seriesName'];
		var seriesType = seriesConfig['seriesType'];
		var xAxisID = seriesConfig['xAxisID'];
		var yAxisID = seriesConfig['yAxisID'];
		
		var xAxis = self.chart.get(xAxisID);
		var categoryColumn = seriesConfig['categoryColumn'];
		var seriesColumn = seriesConfig['seriesColumn'];
		var seriesName = seriesConfig['seriesName'];
		var seriesType = seriesConfig['seriesType'];
		var xAxisID = seriesConfig['xAxisID'];
		var yAxisID = seriesConfig['yAxisID'];
		// 从数据中提取categories信息并设置X轴信息
		
		var categories = [];
		var seriesData = [];
		
		self.orignalData.forEach(function(x){ // 对应好相关的数据
			categories.push(x[categoryColumn]);
			seriesData.push(x[seriesColumn]);
		});
		xAxis.setCategories(categories);
		self.chart.addSeries({
			name: seriesName,
			type: seriesType,
			xAxis: xAxisID,
			yAxis: yAxisID,
			data: seriesData,
		});
	}
	return self.chart;
};

var renderDatatable = function() {
	var self = this;
    "use strict";
    self.table = null;
    if(0 !== $("#datatable-buttons").length) {
    	self.table = $("#datatable-buttons").DataTable({
    		dom: "Brtip",
    		fixedHeader: true,
        	bFilter: false,
	        buttons: [{
	            extend: "csv",
	            text: "CSV",
	            className: "btn-sm"
	        }, {
	            extend: "excel",
	            text: "Excel",
	            className: "btn-sm"
	        }, {
	            extend: "pdf",
	            text: "PDF",
	            className: "btn-sm"
	        }, {
	            extend: "print",
	            text: "Printer",
	            className: "btn-sm"
	        }],
	        responsive: !0
    	});
    }
    return self.table;
};