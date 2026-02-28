// Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Maintenance Schedule', {
        onload: function (frm, cdt, cdn) {
		frm.set_query("vmsd_service", "vms_schedule", function (doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			return {
				"filters": {"item_group": "Maintenance Jobs"},
			};
		});
		frm.set_query("vmsd_part", "vms_schedule", function (doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			return {
				"filters": {"item_group": "Spare Parts"},
			};
		});
	},
});
