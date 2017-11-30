var exampleData = {
		title: '用户留存趋势',
		subtitle: '每天的新用户数',
		categoryColumn: 'ds', 
		columns: ['ds', 'value', 'lc_num'],
		columnNames: ['日期', '留存用户数', '留存天数'],
		types: ['str', 'int', 'str'],

		meta: {
				refer: 'drru',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds', 'lc_num'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户留存', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', value: 47, lc_num: '1'},
			{ds: '2016-12-29', value: 99, lc_num: '1'},
			{ds: '2016-12-30', value: 129, lc_num: '1'},
			{ds: '2016-12-31', value: 174, lc_num: '1'}
		],
};

var exampleData3 = {
		title: '用户注册留存',
		subtitle: '用户注册留存',
		categoryColumn: 'ds',
		columns: ['ds', 'value', 'lc_num', 'channelid'],
		columnNames: ['日期', '留存用户数', '留存天数', '渠道'],
		types: ['str', 'int', 'str'],
		
		meta: {
				refer: 'drru',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds', 'lc_num'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户留存', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', value: 27, channelid:'309', lc_num: '2'},
			{ds: '2016-12-28', value: 21, channelid:'310', lc_num: '2'},
			{ds: '2016-12-29', value: 89, channelid:'309', lc_num: '2'},
			{ds: '2016-12-29', value: 59, channelid:'310', lc_num: '2'},
			{ds: '2016-12-30', value: 19, channelid:'309', lc_num: '2'},
			{ds: '2016-12-30', value: 79, channelid:'310', lc_num: '2'},
			{ds: '2016-12-31', value: 134, channelid:'309', lc_num: '2'},
			{ds: '2016-12-31', value: 114, channelid:'310', lc_num: '2'}
		],
};

var exampleData2 = {
		title: '新注册用户量',
		subtitle: '新用户数',
		categoryColumn: 'ds', 
		columns: ['ds', 'channelid', 'value'],
		columnNames: ['日期', '渠道', '新注册用户数'],
		types: ['str', 'str', 'int'],

		meta: {
				refer: 'dnu',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户总量趋势', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', value: 270},
			{ds: '2016-12-28', channelid: '310', value: 300},
			{ds: '2016-12-29', channelid: '309', value: 690},
			{ds: '2016-12-29', channelid: '310', value: 430},
			{ds: '2016-12-30', channelid: '309', value: 1190},
			{ds: '2016-12-30', channelid: '310', value: 990},
			{ds: '2016-12-31', channelid: '309', value: 1540},
			{ds: '2016-12-31', channelid: '310', value: 1140}
		],
};

var exampleData4 = {
		title: '每天活跃用户数',
		subtitle: '每天活跃用户数',
		categoryColumn: 'ds', 
		columns: ['ds', 'value'],
		columnNames: ['日期', '活跃用户数'],
		types: ['str', 'int'],

		meta: {
				refer: 'dau',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户总量趋势', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', value: 770},
			{ds: '2016-12-29', value: 890},
			{ds: '2016-12-30', value: 2190},
			{ds: '2016-12-31', value: 4540}
		],
};


var exampleData5 = {
		title: '最近7天活跃用户数',
		subtitle: '最近7天活跃用户数',
		categoryColumn: 'ds', 
		columns: ['ds', 'value'],
		columnNames: ['日期', '周活跃用户数'],
		types: ['str', 'int'],

		meta: {
				refer: 'wau',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户总量趋势', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', value: 1070},
			{ds: '2016-12-29', value: 1090},
			{ds: '2016-12-30', value: 4190},
			{ds: '2016-12-31', value: 7540}
		],
};

var exampleData6 = {
		title: '用户留存趋势',
		subtitle: '每天的新用户数',
		categoryColumn: 'ds', 
		columns: ['ds', 'value', 'lc_num'],
		columnNames: ['日期', '留存用户数', '留存天数'],
		types: ['str', 'int', 'str'],

		meta: {
				refer: 'drru',
				product_id: 3,
				product_name: '兽血再燃',
				dimensions: ['ds', 'lc_num'],
		},
		
		graph: {
			xAxises :[{
				title: '日期', // X轴显示什么描述
				opposite: false,
			}],
			
			yAxises: [{
				title: '用户留存', // Y轴显示什么描述
				opposite: false,
			}],
			
			series: [{
				categoryColumn: 'ds',
				seriesColumn: 'value', // 数据序列的值来自于哪一列
				seriesName: '用户总量', // 本数据序列名称
				seriesType: 'area', // 本数据序列将以什么类型的图显示
				xAxisID: 'X0', // 所附着的X轴ID	
				yAxisID: 'Y0', // 所附着的Y轴ID
			}],
		},
		
		rows: [
			{ds: '2016-12-28', value: 27, lc_num: '3'},
			{ds: '2016-12-29', value: 89, lc_num: '3'},
			{ds: '2016-12-30', value: 29, lc_num: '3'},
		],
};