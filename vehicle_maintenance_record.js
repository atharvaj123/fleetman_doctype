// Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Maintenance Record', {
	refresh(frm) {
		frappe.call({
            method: "ampower_fleetman.ampower_fleetman.api.datatable_vm_job_card.main",
            args: {
                'data': frm.doc
            },
            callback: function(data) {
                if(data) {
                    const datatable = new DataTable('*[data-fieldname="vm_job_card_datatable"]', {
                        columns: data.columns,
                        data: data.data,
                        get_row_data: (row) => {
                            // Define action button click behavior
                            row.action = $('<button class="btn btn-default btn-sm">View Details</button>').on('click', function() {
                                var docname = row.name;
                                frappe.set_route('Form', 'VM Job Card', docname);
                            });
                            return row;
                        }
                      });
                }
            }
        });
	}
})
