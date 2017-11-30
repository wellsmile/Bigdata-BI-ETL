var wauData1 = {
		meta: {
			product_id: 3,
			product_name: '兽血再燃',	
			refer: 'wau',
			title: '最近7天活跃用户数',
			
			dimensions: {
				ds: {name: '日期', type: 'str'},
				channelid: {name: '渠道', type: 'str'},
			},
			
			values: {
				value: {name: '周活跃用户数', type: 'int'}
			}
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', value: 1070},
			{ds: '2016-12-28', channelid: '310', value: 1060},
			{ds: '2016-12-29', channelid: '309', value: 1090},
			{ds: '2016-12-29', channelid: '310', value: 990},
			{ds: '2016-12-30', channelid: '309', value: 4190},
			{ds: '2016-12-30', channelid: '310', value: 2190},
			{ds: '2016-12-31', channelid: '309', value: 7540},
			{ds: '2016-12-31', channelid: '310', value: 4540},
		],
};


var wauData2 = {
		meta: {
			product_id: 3,
			product_name: '兽血再燃',	
			refer: 'wau',
			title: '最近7天活跃用户数',
			
			dimensions: {
				ds: {name: '日期', type: 'str'},
				channelid: {name: '渠道', type: 'str'},
			},
			
			values: {
				value: {name: '周活跃用户数', type: 'int'}
			}
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', value: 1070},
			{ds: '2016-12-28', channelid: '310', value: 1060},
			{ds: '2017-12-29', channelid: '309', value: 1090},
			{ds: '2017-12-29', channelid: '310', value: 990},
			{ds: '2017-12-30', channelid: '309', value: 4190},
			{ds: '2017-12-30', channelid: '310', value: 2190},
			{ds: '2017-12-31', channelid: '309', value: 7540},
			{ds: '2017-12-31', channelid: '310', value: 4540},
		],
};

var drruData1 = {
		meta: {
			product_id: 3,
			product_name: '兽血再燃',	
			refer: 'drru',
			title: '用户留存',
			
			dimensions: {
				ds: {name: '日期', type: 'str'},
				channelid: {name: '渠道', type: 'str'},
				lc_num: {name: '留存天数', type:'int'},
			},
			
			values: {
				value: {name: '留存人数', type: 'int'}
			}
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', lc_num: 1, value: 70},
			{ds: '2016-12-28', channelid: '310', lc_num: 1, value: 60},
			{ds: '2016-12-29', channelid: '309', lc_num: 1, value: 90},
			{ds: '2016-12-29', channelid: '310', lc_num: 1, value: 99},
			{ds: '2016-12-30', channelid: '309', lc_num: 1, value: 90},
			{ds: '2016-12-30', channelid: '310', lc_num: 1, value: 21},
			{ds: '2016-12-31', channelid: '309', lc_num: 1, value: 75},
			{ds: '2016-12-31', channelid: '310', lc_num: 1, value: 45},
		],
};

var drruData2 = {
		meta: {
			product_id: 3,
			product_name: '兽血再燃',	
			refer: 'drru',
			title: '用户留存',
			
			dimensions: {
				ds: {name: '日期', type: 'str'},
				channelid: {name: '渠道', type: 'str'},
				lc_num: {name: '留存天数', type:'int'},
			},
			
			values: {
				value: {name: '留存人数', type: 'int'}
			}
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', lc_num: 2, value: 80},
			{ds: '2016-12-28', channelid: '310', lc_num: 2, value: 68},
			{ds: '2016-12-29', channelid: '309', lc_num: 2, value: 91},
			{ds: '2016-12-29', channelid: '310', lc_num: 2, value: 99},
			{ds: '2016-12-30', channelid: '309', lc_num: 2, value: 90},
			{ds: '2016-12-30', channelid: '310', lc_num: 2, value: 91},
			{ds: '2016-12-31', channelid: '309', lc_num: 2, value: 78},
			{ds: '2016-12-31', channelid: '310', lc_num: 2, value: 85},
		],
};


var dnuDataByChannel = {
		meta: {
			product_id: 3,
			product_name: '兽血再燃',	
			refer: 'dnu',
			title: '新注册用户',
			
			dimensions: {
				ds: {name: '日期', type: 'str'},
				channelid: {name: '渠道', type: 'str'},
			},
			
			values: {
				value: {name: '注册人数', type: 'int'}
			}
		},
		
		rows: [
			{ds: '2016-12-28', channelid: '309', value: 180},
			{ds: '2016-12-28', channelid: '310', value: 168},
			{ds: '2016-12-29', channelid: '309', value: 191},
			{ds: '2016-12-29', channelid: '310', value: 199},
			{ds: '2016-12-30', channelid: '309', value: 190},
			{ds: '2016-12-30', channelid: '310', value: 191},
			{ds: '2016-12-31', channelid: '309', value: 178},
			{ds: '2016-12-31', channelid: '310', value: 185},
		],
};



var dataDau = {'rows': [{'ds': '2016-12-26', 'unit_name': 'ds', 'value': 5.0, 'computation_ds': '2016-12-26', 'refer': 'dau', 'product_id': '3'}, {'ds': '2016-12-27', 'unit_name': 'ds', 'value': 20.0, 'computation_ds': '2016-12-27', 'refer': 'dau', 'product_id': '3'}], 'meta': {'title': '日活跃用户量变化趋势', 'sort': {'columns': ['ds'], 'order': ['asc']}, 'product_name': '兽血再燃_IOS', 'values': {'value': {'name': '日活跃用户数', 'type': 'int'}}, 'start_date': '2016-12-26', 'end_date': '2016-12-27', 'refer': 'dau', 'dimensions': {'ds': {'name': '日期', 'type': 'str'}}, 'product_id': '3'}}