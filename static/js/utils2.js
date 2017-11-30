var Data = function(initialData) {
	var self = this;
	
	self.productID = initialData['meta']['product_id'];
	self.productName = initialData['meta']['product_name'];
	self.refer = initialData['meta']['refer'];
	self.title = initialData['meta']['title'];
	
	self.dimensions = initialData['meta']['dimensions']; // 关于维度列的描述 永远保持不变
	self.values = initialData['meta']['values']; // 关于值列的描述 永远保持不变
	
	self.tableColumns = initialData['meta']['table']['columns'];
	self.tableColumnNames = initialData['meta']['table']['columnNames'];
	
	self.dimensionNames = []; // 随着对数据操作不断变更
	self.valueNames = new Set(); // 随着对数据的变化不断变更
	self.evolutionValueNames = new Set();
	self.context = {}; // 上下文
	
	self.rows = initialData['rows']; // 最原始数据，永远保持不变
	self.data = {}; // 随着对数据的处理不断变更
	self._AllMapping = {}; // 用于数据可视化的相关信息，会随着对数据的处理不断变更
	self.transposedDimensions = []; // 本数据集经过哪些列的转置操作
	
	self.seperator = "$$";

	// 判断两个数据集的维度是否完全一样
	self._isDimensionsTheSame = function(otherData) {
		for (var index in self.dimensionNames) {
			if (self.dimensionNames[index] != otherData.dimensionNames[index]) {
				console.log("data with different dimensions");
				return false;
			}
		}
		return self.dimensionNames.length === otherData.dimensionNames.length;
	};
	
	// 判断值列是否一致
	self._isValuesTheSame = function(otherData) {
		if (self.refer != otherData.refer) { 
			console.log("data with different refers")
			return false;
		}
		
		self.valueNames.forEach(function(valueName){
			if (!otherData.valueNames.has(valueName)) {
				console.log("data with different value name");
				return false;
			}
		})
		
		return self.valueNames.size === otherData.valueNames.size;
	};
	
	// 判断是否能够进行垂直合并
	self._isVCombinable = function(otherData) {
		return self._isDimensionsTheSame(otherData) && self._isValuesTheSame(otherData);
	};
	
	// 判断两个数据集是否能够进行水平合并
	self._isHCombinable = function(otherData) {
		if (self.refer == otherData.refer) {
			console.error("data with the same refer try to do H combination !");
			return false;
		}
		return self._isDimensionsTheSame(otherData);
	};
	
	// 初始化函数，只在创建对象的时候调用一次，以后永远都不会再调用
	self._init = function() {
		for (var dimensionColumn in self.dimensions) {
			self.dimensionNames.push(dimensionColumn);
			self._AllMapping[dimensionColumn] = self.dimensions[dimensionColumn]['name']
		}
		self.dimensionNames.sort();
		
		for (var valueColumn in self.values) {
			self.valueNames.add(valueColumn);
			self._AllMapping[valueColumn] = self.values[valueColumn]['name'];
		}
		
		self.rows.forEach(function(row) {
			 var categoryKeyCells = [];
			 self.dimensionNames.forEach(function(dimensionName) {
				 categoryKeyCells.push(row[dimensionName]);
			 });
			 var categoryKey = categoryKeyCells.join(self.seperator);
			 self.data[categoryKey] = row; // 将数据组织到对应的分类下
		});
	};
	self._init();
	
	// 垂直扩展实现(UNION ALL)
	self.vCombine = function(otherData) {
		console.log("doing V combine");
		if (self._isVCombinable(otherData)) {
			for (otherDataCategoryKey in otherData.data) {
				if (otherDataCategoryKey in self.data) {
					console.warn("vCombine: otherData overwrite categoryKey: " + otherDataCategoryKey);
				}
				self.data[otherDataCategoryKey] = otherData.data[otherDataCategoryKey]; // 垂直合并核心操作，不需要变更_AllMapping
			}
		} else {
			console.error("vCombine failed");
		}
	};
	
	// 水平扩展实现(JOIN ON)
	self.hCombine = function(otherData) {
		console.log("doing H combine");
		var otherRefer = otherData.refer;
		if (self._isHCombinable(otherData)) {
			for (var categoryKey in self.data) {
				if (categoryKey in otherData.data) {
					var otherDataObj = otherData.data[categoryKey];
					otherData.valueNames.forEach(function(valueName) {
						var newName = [otherRefer, valueName].join(self.seperator);
						self.data[categoryKey][newName] = otherData.data[categoryKey][valueName];
						self._AllMapping[newName] = otherData._AllMapping[valueName]; // 本数据是什么数据
						self.valueNames.add(newName); //  产生一个新的值列
					});
				}
			};
		} else {
			console.error("hCombine failed");
		}
	};
	
	// 转置数据实现(TRANPOSITION)
	self.transpose = function(transposeDimensions) {
		var newDimensionNames = []; // 维度列
		var newValueNames = new Set(); // 数值列
		
		self.dimensionNames.forEach(function(dimensionName) {
			if (transposeDimensions.indexOf(dimensionName) < 0) {
				newDimensionNames.push(dimensionName);
			}
		});
		self.dimensionNames = newDimensionNames;
		
		transposeDimensions.forEach(function(transposeDimension){
			self.transposedDimensions.push(transposeDimension);
		});
		
		var newData = {} // 用来代替self.data
		for (var categoryKey in self.data) {
			var currentData = self.data[categoryKey];
			var newColumnCells = [];
			var newColumnNameCells = [];
			
			transposeDimensions.forEach(function(dimensionName) {
				if (dimensionName in currentData) {
					var dimensionValue = currentData[dimensionName];
					newColumnCells.push([dimensionName, dimensionValue]);
					newColumnNameCells.push([self._AllMapping[dimensionName], dimensionValue]);
				} else {
					newColumnNameCells.push([self._AllMapping[dimensionName], null]);
				}
			});
			
			var _bridgeCells1 = [];
			newColumnCells.forEach(function(item) {
				var cell = item.join("=");
				_bridgeCells1.push(cell);
			});
			var newColumnPrefix = _bridgeCells1.join(self.seperator); // 生成列前缀
			
			var _bridgeCells = []
			newColumnNameCells.forEach(function(pair){
				_bridgeCells.push(pair.join("="));
			});
			var newColumnNamePrefix = _bridgeCells.join("&"); // 列名前缀
			
			// 计算缩水后的分类名
			var newCategoryCells = [];
			self.dimensionNames.forEach(function(newDimensionName){
				newCategoryCells.push(currentData[newDimensionName]);
			});
			var newCategoryKey = newCategoryCells.join(self.seperator);
			// 填充此新的分类名下的值
			self.valueNames.forEach(function(seriesColumn) { // 遍历当前的所有的值列
				var currentValue = currentData[seriesColumn]; // 当前的值
				var newColumn = [newColumnPrefix, seriesColumn].join("$$"); 
				var newColumnName = [newColumnNamePrefix, self._AllMapping[seriesColumn]].join("／");
				newValueNames.add(newColumn); // 添加新的数据系列
				self._AllMapping[newColumn] = newColumnName; // 将新的列和其列名添加到公共位置供后续查询使用
				
				if ( !(newCategoryKey in newData) ) {
					newData[newCategoryKey] = {};
				}
				newData[newCategoryKey][newColumn] = currentValue;
			});
			
			// 在覆盖原数据之前，先将保留下来的维度的相关的值写入数据中，以保持数据的一致性
			self.dimensionNames.forEach(function(dimensionName) {
				newData[newCategoryKey][dimensionName] = currentData[dimensionName];
			});
		}
		
		self.data = newData;
		self.valueNames = newValueNames;
	};
	
	// 具体数据和其上下文的匹配
	self.contextKeyMatch = function(data, contextData) {
		
	};
	
	// 概念演化实现(EVOLUTION)，通过callBack的返回值添加新的列（列描述）和值
	self.doEvolution = function(contextData, callBack) {
		
		var selfTransposedDimensions = [];
		var contextTransposedDimensions = [];
		
		self.transposedDimensions.forEach(function(transposedDimension) {
			selfTransposedDimensions.push(transposedDimension);
		});
		
		contextData.transposedDimensions.forEach(function(transposedDimension) {
			contextTransposedDimensions.push(transposedDimension);
		});
		
		selfTransposedDimensions.reverse();
		contextTransposedDimensions.reverse();
		
		/////////////////////////////////////////////////////////////////
		for (var categoryKey in self.data) {
			var _data = self.data[categoryKey];
			
			var _contextDicts = [];
			if (categoryKey in contextData.data) {
				var _contextData = contextData.data[categoryKey];
				for (var _categoryDataKey in _contextData) {
					if (contextData.valueNames.has(_categoryDataKey)) {
						var _contextDict = {};
						var _contextValue = _contextData[_categoryDataKey];
						var _categoryDataKeyCells = _categoryDataKey.split(self.seperator);
						_categoryDataKeyCells.forEach(function(item) {
							var itemCells = item.split("=");
							if (itemCells.length == 2) {
								_contextDict[itemCells[0]] = itemCells[1];
							} else if (itemCells.length == 1) {
								_contextDict[itemCells[0]] = _contextValue;
							}
						});
						_contextDicts.push(_contextDict)
					}
				}
			} else {
				_contextDicts = null;
			}
			
			for (var _dataKey in _data) {
				if (self.valueNames.has(_dataKey)) {
					var _dataDict = {};
					var _dataValue = _data[_dataKey];
					var _dataKeyCells = _dataKey.split(self.seperator);
					_dataKeyCells.forEach(function(item) {
						var itemCells = item.split("=");
						if (itemCells.length == 2) {
							_dataDict[itemCells[0]] = itemCells[1];
						} else if (itemCells.length == 1) {
							_dataDict[itemCells[0]] = _dataValue;
						}
					});
					
					var _dataDictKeyCells = [];
					contextTransposedDimensions.forEach(function(item){
						if (item in _dataDict) {
							_dataDictKeyCells.push([item, _dataDict[item]]);
						} else {
							_dataDictKeyCells.push([item, null]);
						}
					})
					
					var _dataDictKeyBridge = [];
					_dataDictKeyCells.forEach(function(item) {
						_dataDictKeyBridge.push(item.join("="))
					})
					var _dataDictKey = _dataDictKeyBridge.join(self.seperator);
					
					var __myContext = null;
					if (_contextDicts) {
						for (var __myIndex in _contextDicts) {
							var __contextDict = _contextDicts[__myIndex];
							var __contextDictKeyCells = [];
							contextTransposedDimensions.forEach(function(item) {
								if (item in __contextDict) {
									__contextDictKeyCells.push([item, __contextDict[item]]);
								} else {
									__contextDictKeyCells.push([item, null]);
								}
							});
							
							var __contextDictKeyBridge = [];
							__contextDictKeyCells.forEach(function(item) {
								__contextDictKeyBridge.push(item.join("="));
							})
							var __contextDictKey = __contextDictKeyBridge.join(self.seperator);
							if (__contextDictKey == _dataDictKey) {
								__myContext = __contextDict;
								break;
							} else {
								continue;
							}
						}
					} else {
						console.log("no need to search context....")
					}
					
					var newColumnName = [_dataKey, contextData.refer].join(self.seperator);
					var result = callBack(_dataDict, __myContext);
					var newValue = result[0];
					var newDesc = result[1];
					self.data[categoryKey][newColumnName] = newValue;
					self._AllMapping[newColumnName] = newDesc;
					self.evolutionValueNames.add(newColumnName);
				}
			}
		}
	};
};


var Chart = function(data, chartConfig=null) {
	var self = this;
	
	self.data = data;
	
	renderTo = self.data.graphDomID;
	var categories = [];
	for (var dataKey in self.data.data) {
		categories.push(dataKey);
	}
	categories.sort();
	
	var chart = Highcharts.chart(renderTo, {});
	chart.setTitle({text: self.data.title}, {text: self.data.subTitle});
	// 删除当前X轴和Y轴
	allAxises = chart.xAxis.concat(chart.yAxis);
	for(axisIndex in allAxises){
		Axis = allAxises[axisIndex];
		Axis.remove();
	}
	
	var xTitleCells = [];
	self.data.dimensionNames.forEach(function(item){
		xTitleCells.push(self.data._AllMapping[item]);
	})
	var xTitle = xTitleCells.join("/");
	
	chart.addAxis({
		id: 'X0',
		title : {
			text: xTitle
		},
		opposite: false,
	}, true, true);
	
	chart.addAxis({
		id: 'Y0',
		title : {
			text: '',  
		},
		opposite: false,
	}, false, true);
	
	
	
	var choosedNames = self.data.valueNames;
	if (self.data.evolutionValueNames.size > 0) {
		choosedNames = self.data.evolutionValueNames;
	}
	var allSeries = [];
	
	choosedNames.forEach(function(seriesColumn) {
		var series = {
				name: self.data._AllMapping[seriesColumn], //  当前数据序列的名称
				type: 'line',
				xAxis: 'X0',
				yAxis: 'Y0',
				visible:true,
				data: [],
		};
		
		categories.forEach(function(category) {
			var currentCategory = self.data.data[category];
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
		chart.addSeries(item);
	});
	
	return chart;
}

var Table = function() {
	var self = this;
}

