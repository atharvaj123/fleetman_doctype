// Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on('VM Job Card', {
    refresh: function(frm) {
        // Only show the 'Issue Part' button if the document is not submitted (docstatus is 0)
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Issue Part'), function() {
                // Define a custom dialog (modal) with fields from VMJC Part Details
                let d = new frappe.ui.Dialog({
                    title: 'Issue Part',
                    fields: [
                        {
                            label: 'Resource Type',
                            fieldname: 'vmjcpd_resource_type',
                            fieldtype: 'Select',
                            options: '\nVehicle\nTrailer',
                            reqd: 1
                        },
                        {
                            fieldname: 'section_break_1',
                            fieldtype: 'Section Break'
                        },
                        {
                            label: 'Warehouse',
                            fieldname: 'vmjcpd_warehouse',
                            fieldtype: 'Link',
                            options: 'Warehouse',
                            change: function() {
                                // Fetch available quantity when warehouse changes
                                fetch_quantity_available(d);
                            },
                            reqd: 1
                        },
                        {
                            label: 'Part',
                            fieldname: 'vmjcpd_part',
                            fieldtype: 'Link',
                            options: 'Item',
                            get_query: function() {
                                return {
                                    filters: {
                                        'item_group': ["in", ['Spare Parts', 'Lubricants']]  // Apply a filter to the link field
                                    }
                                };
                            },
                            reqd: 1,
                            change: function() {
                                // Fetch UOM when part is selected
                                const part = d.get_value('vmjcpd_part');
                                if (part) {
                                    frappe.call({
                                        method: 'frappe.client.get',
                                        args: {
                                            doctype: 'Item',
                                            name: part
                                        },
                                        callback: function(r) {
                                            if (r.message) {
                                                d.set_value('vmjcpd_uom', r.message.stock_uom); // Set UOM
                                            }
                                        }
                                    });
                                }
                                // Fetch available quantity when part changes
                                fetch_quantity_available(d);
                            }
                        },
                        {
                            label: 'UOM',
                            fieldname: 'vmjcpd_uom',
                            fieldtype: 'Link',
                            options: 'UOM',
                            read_only: 1
                        },
                        {
                            label: 'Available Quantity',
                            fieldname: 'vmjcpd_available_quantity',
                            fieldtype: 'Float',
                            read_only: 1
                        },
                        {
                            fieldname: 'column_break_1',
                            fieldtype: 'Column Break'
                        },
                        {
                            label: 'Quantity',
                            fieldname: 'vmjcpd_qty',
                            fieldtype: 'Float',
                            reqd: 1
                        },
                        {
                            label: 'Date',
                            fieldname: 'vmjcpd_date',
                            fieldtype: 'Date',
                            default: frappe.datetime.get_today(),
                            change: function() {
                                // Fetch available quantity when date changes
                                fetch_quantity_available(d);
                            }
                        },
                        {
                            label: 'Batch',
                            fieldname: 'vmjcpd_batch',
                            fieldtype: 'Link',
                            options: 'Batch',
                            get_query: function() {
                                return {
                                    filters: {
                                        'item': d.get_value('vmjcpd_part')
                                    }
                                };
                            }
                        },
                        {
                            label: 'Purchase Invoice',
                            fieldname: 'vmjcpd_purchase_invoice',
                            fieldtype: 'Link',
                            options: 'Purchase Invoice',
                            get_query: function() {
                                return {
                                    filters: {
                                        'docstatus': 1
                                    }
                                };
                            }
                        },
                        {
                            label: 'Is External Job',
                            fieldname: 'vmjcpd_is_external_job',
                            fieldtype: 'Check',
                        },
                        {
                            fieldname: 'section_break_1',
                            fieldtype: 'Section Break'
                        },
                        {
                            label: 'Notes',
                            fieldname: 'vmjcpd_notes',
                            fieldtype: 'Small Text'
                        }
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        // Resource Type Validation
                        if (!values.vmjcpd_resource_type) {
                            frappe.msgprint(__('Please select a Resource Type (either Vehicle or Trailer).'));
                            return;  // Stop submission if validation fails
                        }

                        // Validation based on selected Resource Type
                        if (values.vmjcpd_resource_type === 'Trailer' && !frm.doc.vmjc_trailer) {
                            frappe.msgprint(__('Please set a Trailer in the VM Job Card before proceeding.'));
                            return;  // Stop submission if Trailer is not set
                        }

                        if (values.vmjcpd_resource_type === 'Vehicle' && !frm.doc.vmjc_vehicle) {
                            frappe.msgprint(__('Please set a Vehicle in the VM Job Card before proceeding.'));
                            return;  // Stop submission if Vehicle is not set
                        }
                        // Handle the form submission and insert data into VMJC Part Details
                        frappe.call({
                            method: 'frappe.client.insert',
                            args: {
                                doc: {
                                    doctype: 'VMJC Part Details',
                                    vmjcpd_part: values.vmjcpd_part,
                                    vmjcpd_batch: values.vmjcpd_batch,
                                    vmjcpd_serial_no: values.vmjcpd_serial_no,
                                    vmjcpd_date: values.vmjcpd_date,
                                    vmjcpd_qty: values.vmjcpd_qty,
                                    vmjcpd_uom: values.vmjcpd_uom,
                                    vmjcpd_warehouse: values.vmjcpd_warehouse,
                                    vmjcpd_available_quantity: values.vmjcpd_available_quantity,
                                    vmjcpd_resource_type: values.vmjcpd_resource_type,
                                    vmjcpd_notes: values.vmjcpd_notes,
                                    vmjcpd_vehicle: frm.doc.vmjc_vehicle,
                                    vmjcpd_purchase_invoice: values.vmjcpd_purchase_invoice,
                                    vmjcpd_is_external_job: values.vmjcpd_is_external_job,
                                    vmjcpd_job_ref: frm.doc.name  // Link to the VM Job Card
                                }
                            },
                            callback: function(response) {
                                if (response.message) {
                                    frappe.msgprint(__('Part added successfully'));
                                    d.hide();  // Close the modal on success
                                    frm.reload_doc();  // Reload the parent form to reflect changes
                                }
                            }
                        });
                    }
                });

                // Show the dialog (modal)
                d.show();
            });
        }

        render_parts_datatable(frm);
    },
    vmjc_refresh_parts: function(frm) {
        render_parts_datatable(frm);
    },
    onload: function(frm) {
        // When the form is loaded, attach click event to tabs
        $('#vm-job-card-job_details_tab-tab').on( "click",function(e) {
            var clicked_tab = $(e.target).text().trim();  // Get the name of the clicked tab
            // Check if a Job Details tab is clicked
            if (clicked_tab === "Job Details") {
                render_parts_datatable(frm);
            }
        });
            // Apply set_query to the link field in the child table
        frm.fields_dict['vmjc_jobs'].grid.get_field('vmjcsd_job').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: {
                    'item_group': 'Maintenance Jobs'
                }
            };
        };
    }
});

function fetch_quantity_available(d) {
    const part = d.get_value('vmjcpd_part');
    const warehouse = d.get_value('vmjcpd_warehouse');
    const date = d.get_value('vmjcpd_date') || frappe.datetime.get_today();

    // Validate if both 'part' and 'warehouse' are set
    if (!part || !warehouse) {
        return;  // Stop further execution if validation fails
    }

    frappe.call({
        method: 'erpnext.stock.doctype.quick_stock_balance.quick_stock_balance.get_stock_item_details',
        args: {
            "warehouse": warehouse,
            "item": part,
            "date": date
        },
        callback: function (r) {
            if (!r.exc) {
                // Set the available quantity in the dialog
                if (r.message.qty !== undefined && r.message.qty !== null) {
                    d.set_value('vmjcpd_available_quantity', r.message.qty);
                } else {
                    // Handle the case when qty is not returned or is invalid
                    d.set_value('vmjcpd_available_quantity', "0");
                }
            }
        }
    });
}

function render_parts_datatable(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'VMJC Part Details',
            limit_page_length: 1000,  // Limit the number of records fetched
            filters: { 'vmjcpd_job_ref': frm.doc.name },  // Fetch parts related to the current Job Card
            fields: ['name', 'vmjcpd_part', 'vmjcpd_qty', 'vmjcpd_uom', 'vmjcpd_warehouse', 'vmjcpd_available_quantity', 'vmjcpd_resource_type', 'vmjcpd_date', 'vmjcpd_stock_ref', 'vmjcpd_is_cancelled', 'vmjcpd_stock_cost']  // Include Stock Ref
        },
        callback: function(response) {
            if (response.message) {
                // Prepare data for the DataTable using key-value pairs
                let part_data = response.message.map(row => ({
                    vmjcpd_part: `<a href="/app/vmjc-part-details/${row.name}" target="_blank">${row.vmjcpd_part}</a>`,  // Clickable link to VMJC Part Details
                    vmjcpd_qty: row.vmjcpd_qty,
                    vmjcpd_uom: row.vmjcpd_uom,
                    vmjcpd_warehouse: row.vmjcpd_warehouse,
                    vmjcpd_available_quantity: row.vmjcpd_available_quantity,
                    vmjcpd_resource_type: row.vmjcpd_resource_type,
                    vmjcpd_date: row.vmjcpd_date,
                    vmjcpd_stock_cost: row.vmjcpd_stock_cost,
                    vmjcpd_stock_ref: row.vmjcpd_stock_ref ? `<a href="/app/stock-entry/${row.vmjcpd_stock_ref}" target="_blank">${row.vmjcpd_stock_ref}</a>` : '-',  // Clickable link for Stock Ref
                    action: (frm.doc.docstatus === 0 && row.vmjcpd_is_cancelled === 0) ?  `<button class="btn btn-danger btn-xs return-btn" data-name="${row.name}">Return</button>` : (row.vmjcpd_is_cancelled === 1 ? "Returned" : "-")  // Return button
                }));

                // Define the columns with fieldtype and options for Links
                let columns = [
                    {
                        id: 'vmjcpd_part',
                        name: 'Part',
                        fieldtype: 'Link',  // Specifies this as a Link field
                        options: 'Item',  // If this links to Item Doctype, else change accordingly
                        editable: false,
                        width: 150
                    },
                    { id: 'vmjcpd_qty', name: 'Quantity', fieldtype: 'Data', editable: false, width: 150 },
                    { id: 'vmjcpd_uom', name: 'UOM', fieldtype: 'Data', editable: false, width: 150},
                    { id: 'vmjcpd_warehouse', name: 'Warehouse', fieldtype: 'Link', options: 'Warehouse', editable: false, width: 150 },  // Warehouse link
                    { id: 'vmjcpd_available_quantity', name: 'Available Qty', fieldtype: 'Data', editable: false, width: 150 },
                    { id: 'vmjcpd_resource_type', name: 'Resource Type', fieldtype: 'Data', editable: false, width: 150 },
                    { id: 'vmjcpd_date', name: 'Date', fieldtype: 'Date', editable: false , width: 150 },
                    { id: 'vmjcpd_stock_cost', name: 'Stock Cost', fieldtype: 'Currency', editable: false , width: 150 },
                    {
                        id: 'vmjcpd_stock_ref',
                        name: 'Stock Ref',
                        fieldtype: 'Link',  // Specifies this as a Link field
                        options: 'Stock Entry',  // Target Doctype for Stock Ref Link
                        editable: false,
                        width: 150
                    },
                    { id: 'action', name: 'action', fieldtype: 'Data', editable: false, width: 150  }
                ];

                // Render DataTable in the HTML field
                const datatable = new DataTable('*[data-fieldname="vmjc_part_datatable"]', {
                    columns: columns,
                    data: part_data,
                });
                

                // Attach 'click' event listener for return buttons
                $('.return-btn').on('click', function() {
                    let part_name = $(this).data('name');
                    frappe.confirm(
                        'Are you sure you want to return this part?',
                        function() {
                            // Update vmjcpd_is_cancelled field to 1 on confirmation
                            frappe.call({
                                method: 'frappe.client.set_value',
                                args: {
                                    doctype: 'VMJC Part Details',
                                    name: part_name,
                                    fieldname: 'vmjcpd_is_cancelled',
                                    value: 1
                                },
                                callback: function(response) {
                                    if (!response.exc) {
                                        frappe.msgprint('Part returned successfully');
                                        frm.reload_doc();  // Reload the form to reflect changes
                                    }
                                }
                            });
                        }
                    );
                });
            }
        }
    });
}
