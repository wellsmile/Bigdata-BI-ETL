$(function(){
	function RevenueViewModel() {
		var self = this;
		
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
		
		self.dpm_data = ko.observable(); // 每日付费额
		self.dpu_data = ko.observable(); // 日付费用户数
		
		self.drpm_data = ko.observable(); // 日角色付费总额
		self.dpr_data = ko.observable(); // 日付费角色数
		
		self.dnp_data = ko.observable(); // 新增付费用户
		self.dnpm_data = ko.observable(); // 新增付费用户的付费额
		
		
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
			
			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "dpm"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "dpm_graph";
				self.dpm_data(dataObj);
			}, "json")
		
			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "dpu"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "dpu_graph";
				self.dpu_data(dataObj);
			}, "json")
			
			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "drpm"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "drpm_graph";
				self.drpm_data(dataObj);
			}, "json")

			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "dpr"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "dpr_graph";
				self.dpr_data(dataObj);
			}, "json")
			
			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "dnp"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "dnp_graph";
				self.dnp_data(dataObj);
			}, "json")
			
			$.get('/report/', {
				product_id: matrixToken,
				start_date: self.startDate(),
				end_date: self.endDate(),
				dimensions: JSON.stringify(['ds','product_id']),
				refer: "dnpm"
			}, function(data) {
				var dataObj = new Data(data);
				dataObj.graphDomID = "dnpm_graph";
				self.dnpm_data(dataObj);
			}, "json")
			
		};
		
		// 显示图表的工具方法
		self.showChart = function(data){
			var chart = new Chart(data);
//			renderGraph(data);
		};
		
		// 显示Modal细节
		self.showModalDetail = function(data) {
			console.log(data);
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
	ko.applyBindings(new RevenueViewModel());
})