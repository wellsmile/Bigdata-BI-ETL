/**
 * Theme: Ubold Admin Template
 * Author: Coderthemes
 * Component: Datatable
 * 
 */
var handleDataTableButtons = function() {
        "use strict";
        0 !== $("#datatable-buttons").length && $("#datatable-buttons").DataTable({
            dom: "Brtip",
            fixedHeader: true,
//            bFilter: false,
            
            buttons: [{
                extend: "csv",
                text: "导出CSV",
                className: "btn-sm"
            }, {
                extend: "excel",
                text: "导出Excel",
                className: "btn-sm"
            }, {
                extend: "pdf",
                text: "导出PDF",
                className: "btn-sm"
            }, {
                extend: "print",
                text: "通过打印机打印",
                className: "btn-sm"
            }
            
//            ,{
//            		extend: "colvis",
//            		text: "设置列的可见行",
//            		className: "btn-lg",
//            		postfixButtons: ['colvisRestore'],
//            }
            ],
            responsive: !0
        })
    },
    TableManageButtons = function() {
        "use strict";
        return {
            init: function() {
                handleDataTableButtons()
            }
        }
    }();