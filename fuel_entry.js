// Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fuel Entry", {
	onload(frm, cdt, cdn) {
        // Set a custom query for the "item" field based on Item Group "Fuel"
        frm.set_query('item', function () {
            return {
                filters: {
                    'item_group': ['in', ['Fuel', 'Diesel', 'Lubricants']]
                }
            };
        });
        // refresh available qty of stock
        find_available_quantity(frm, cdt, cdn);
    },
    item: (frm, cdt, cdn) => {
        find_available_quantity(frm, cdt, cdn);
    },
    date: (frm, cdt, cdn) => {
        find_available_quantity(frm, cdt, cdn);
    },
    warehouse: (frm, cdt, cdn) => {
        find_available_quantity(frm, cdt, cdn);
    },
});

function find_available_quantity(frm, cdt, cdn) {
    if (frm.doc.docstatus === 0) {
        var warehouse = frm.doc.warehouse;
        var date = frm.doc.date;
        var item = frm.doc.item;
        date = date.split(' ');
        if (warehouse && date && item) {
            frappe.call({
                method: 'erpnext.stock.doctype.quick_stock_balance.quick_stock_balance.get_stock_item_details',
                args: {
                    "warehouse": warehouse,
                    "date": date[0] /* get date only */,
                    "item": item
                },
                callback: function (r) {
                    if (!r.exc) {
                        frm.set_value("available_quantity", r.message.qty);
                        // check for if document is already in draft state
                        if (frm.doc.docstatus === 0 && frm.doc.__islocal != 1) {
                            frm.save();
                        }
                    }
                }
            });
        }
    }
};
