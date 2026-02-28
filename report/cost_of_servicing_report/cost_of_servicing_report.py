# Copyright (c) 2025, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt

import frappe,json

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	result = []

	start_date = filters.get("start_date")
	end_date = filters.get("end_date")
	part = filters.get("part")
	vehicle = filters.get("vehicle")
	type_filter = filters.get("type")

	if type_filter == "Parts" or type_filter == None:
		# Define filters for VMJC Part Details
		vmjc_part_details_filters = {
			"vmjcpd_date": ["between", [start_date, end_date]]
		}
		if part:
			vmjc_part_details_filters["vmjcpd_part"] = part
		if vehicle:
			vmjc_part_details_filters["vmjcpd_vehicle"] = vehicle

		vmjc_part_details = frappe.get_all(
			"VMJC Part Details",
			filters=vmjc_part_details_filters,
			fields=["vmjcpd_date as date", "vmjcpd_job_ref as job_card_number", "vmjcpd_part as item", "vmjcpd_vehicle as vehicle", "vmjcpd_stock_cost as cost", "vmjcpd_stock_ref as document", "'Parts' as Type"]
		)

		for part_details in vmjc_part_details:
			part_details["cost"] = frappe.get_value("Stock Entry", part_details["document"], "total_amount")
	else:
		vmjc_part_details = []


	if type_filter == "Service" or type_filter == None:
		# Define filters for VMJC Service Details
		vmjc_service_details_filters = {
			"vmjcsd_date": ["between", [start_date, end_date]]
		}
		if part:
			vmjc_service_details_filters["vmjcsd_job"] = part
		if vehicle:
			vmjc_service_details_filters["parent"] = ['like', f'VMJC-{vehicle}%']

		vmjc_service_details = frappe.get_all(
			"VMJC Service Details",
			filters=vmjc_service_details_filters,
			fields=["vmjcsd_date as date", "parent as job_card_number", "vmjcsd_job as item", "vmjcsd_purchase_invoice as document", "'Service' as Type"]
		)

		# Modify the vehicle field to extract the second part of the parent field
		for service in vmjc_service_details:
			if service["job_card_number"]:
				parent_parts = service["job_card_number"].split("-")
				if len(parent_parts) > 1:
					service["vehicle"] = parent_parts[1]

		for service in vmjc_service_details:
			service["cost"] = frappe.get_value("Purchase Invoice", service["document"], "total") or 0
	else:
		vmjc_service_details = []

	result =  vmjc_part_details + vmjc_service_details
	# Calculate total cost
	total_cost = sum(item["cost"] for item in result if "cost" in item)

	# Add a row for total cost
	result.append({
		"date": "",
		"vehicle": "",
		"job_card_number": "",
		"item": "",
		"Type": "<b>Total</b>",
		"cost": total_cost,
		"document": ""
	})
	return [] if not result else result

def get_columns():
	columns = [
		{"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
		{"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Resource", "width": 150},
		{"label": "Job Card Number", "fieldname": "job_card_number", "fieldtype": "Link", "options": "VM Job Card", "width": 150},
		{"label": "Name", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 200},
		{"label": "Type", "fieldname": "Type", "fieldtype": "Data", "width": 100},
		{"label": "Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 120},
		{"label": "Document", "fieldname": "document", "fieldtype": "Data", "width": 200}
	]
	return columns