$(function(){
	function DashboardViewModel() {
		var self = this;
		
		self.dashboardRefers = ['dnu', 
			'dtu', 
			'dtd', 
			'dar', 
			'dnr', 
			'dnd', 
			'dfp', 
			'dfpm', 
			'tpu',
			'tpr', 
			'duot', 
			'duoa', 
			'onu',
			'nna',
			'rcr',
			'pcu',
			'acu',
			'snog',
			'anog',
			'dai',
			'war',
			'wai',
			'mar',
			'mai'];
		
		// 将报表数据绑定到一个KO变量中，以监测其变化
		self.reportsData = ko.observableArray();
		
		// 当前数据表、图及其对应的数据
		self.focusData = ko.observable();
		self.focusGraph = null;
		self.focusTable = null;
		
		// 条件选择器对应的值
		self.selectedProduct = ko.observable();
		self.dateRange = ko.observable();
		self.startDate = ko.observable();
		self.endDate = ko.observable();
		
		// 当前用户能够看到的产品列表
		self.products = ko.observableArray([]);
		
		self.initConditionView = function() {
			// 初始化日期范围条件选择器
			$('#datepicker-start-date').datepicker({
	        		format: "yyyy-mm-dd",
	            	autoclose: true,
	            	todayHighlight: true
	        });
        
	        $('#datepicker-end-date').datepicker({
	        		format: "yyyy-mm-dd",
	            	autoclose: true,
	            	todayHighlight: true
	        });
	        
			// 日期范围初始值设置
			var savedStartDate = getLocalValue('savedStartDate') || null;
			var savedEndDate = getLocalValue('savedEndDate') || null;
			
			if (savedStartDate && savedEndDate){
				self.startDate(savedStartDate);
				self.endDate(savedEndDate);
			} else {
				var start_date = moment().subtract(14, 'days').format('YYYY-MM-DD');
				var end_date = moment().subtract(1, 'days').format('YYYY-MM-DD');
				self.startDate(start_date);
				self.endDate(end_date);
			}
			
			// 创建产品选择下拉列表
			$('.selectpicker').select2();
			var savedProductID = getLocalValue('savedProductID') || null;
			$.get('/meta/', function(data) {
				for (var i in data) {
					self.products.push(data[i]);
					if (savedProductID && data[i].product_id == savedProductID) {
						self.selectedProduct(self.products()[i]);
					}
				}
				
				if(self.selectedProduct()) {
					self.fillDashboard();
				}
				
			}, "json");
		};
		self.initConditionView(); // 初始化条件选择器
		
		self.onConditionChange = function() {
			if (self.selectedProduct()){
				setLocalValue('savedProductID', self.selectedProduct().product_id);
				setLocalValue('savedStartDate', self.startDate());
				setLocalValue('savedEndDate', self.endDate());
				self.fillDashboard();
			} else {
				setLocalValue('savedProductID', null);
				self.reportsData.removeAll();
			}
		};
		
		// 请求后端，填充Dashboard内容
		self.fillDashboard = function(){
			self.reportsData.removeAll();
			
			var matrixToken = self.selectedProduct().product_id;
			for(var i in self.dashboardRefers) {
				var refer = self.dashboardRefers[i];
				$.get('/report/', {
					product_id: matrixToken,
					start_date: self.startDate(),
					end_date: self.endDate(),
					dimensions: JSON.stringify(['ds','product_id']),
					refer: refer
				}, function(data) {
					var dataObj = new Data(data);
					dataObj.graphDomID = data['meta']['refer'] + "_graph";
					self.reportsData.push(dataObj);
				}, "json")
			}
		};
		
		// 显示图表的工具方法
		self.showChart = function(data){
			var chart = new Chart(data);
//			renderGraph(data);
		};
		
		// 显示Modal细节
		self.showModalDetail = function(data) {
			data.graphDomID = data.graphDomID + "_focus";
			self.focusData(data);
			
			var modalDom = $("#full-width-modal");
			modalDom.on("shown.bs.modal", function(e){
				var _dom = $("#"+data.graphDomID);
				_dom.resize(); // 触发resize事件，以获取到正确的容器长度和宽度
				self.focusGraph = Chart(self.focusData());
				self.focusTable = renderDatatable();
			}).on("hide.bs.modal", function(e){
				self.focusGraph.destroy();
				self.focusTable.destroy();
				self.focusData(null);
			}).on("hidden.bs.modal", function(e) {
				modalDom.off();
			});
		};
	}
	ko.applyBindings(new DashboardViewModel());
})