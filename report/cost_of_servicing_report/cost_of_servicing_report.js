// Copyright (c) 2025, Ambibuzz Technologies LLP and contributors
// For license information, please see license.txt

frappe.query_reports["Cost of Servicing Report"] = {
	"filters": [
		{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
				"reqd": 1
		},
		{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
				"reqd": 1
		},
		{
			"fieldname": "vehicle",
			"label": "Vehicle",
			"fieldtype": "Link",
			"options": "Resource"
		},
		{
			"fieldname": "part",
			"label": "Part / Service",
			"fieldtype": "Link",
			"options": "Item",
				"filters": {
				"item_group": ["in", ["Spare Parts", "Lubricants", "Maintenance Jobs"]]
			}
		},
		{
			"fieldname": "type",
			"label": "Type",
			"fieldtype": "Select",
			"options": "\nService\nParts"
		}
	]
};
