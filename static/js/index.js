$(function(){
	function IndexViewMode() {
		var self = this;
		
		self.initView = function() {
			var matrixLocation = getLocalValue('MATRIX_LOCATION') || '/dashboard/';
			window.location = matrixLocation;
		}
		
		self.initView();
	}

	ko.applyBindings(new IndexViewMode());	
})
