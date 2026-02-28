# Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt
import frappe, json

@frappe.whitelist()
def main():
    vehicle_maintenance_record = json.loads(frappe.form_dict.data)
    if vehicle_maintenance_record and vehicle_maintenance_record.get("name"):
        filters = [["VM Job Card", "vmjc_vmr", "=", vehicle_maintenance_record.get("name")], ["VM Job Card", "docstatus", "=", "1"]]
        fields = ["name", "vmjc_end_odometer", "vmjc_end_time", "vmjc_end_date", "vmjc_in_odometer", "vmjc_start_time", "vmjc_start_date", "vmjc_difference_of_days"]
        vm_job_card_list = frappe.get_all("VM Job Card", fields=fields, filters=filters)
        columns = [
            {"editable": False, "width": 150,"name":"Job"},
            {"editable": False, "width": 150,"name":"Start Date"},
            {"editable": False, "width": 150,"name":"End Date"},
            {"editable": False, "width": 150,"name":"Start Time"},
            {"editable": False, "width": 150,"name":"End Time"},
            {"editable": False, "width": 150,"name":"Start Odometer"},
            {"editable": False, "width": 150,"name":"End Odometer"},
            {"editable": False, "width": 150,"name":"Difference of Days"},
        ]
        data = []
        for i in vm_job_card_list:
            data.append([
                {"content": '<a class="btn btn-default btn-xs" onclick="frappe.set_route(\'Form\', \'VM Job Card\',\''+i.get("name")+'\')">'+i.get("name")+'</a>'},
                {"content":i.get("vmjc_start_date")},
                {"content":i.get("vmjc_end_date")},
                {"content":i.get("vmjc_start_time")},
                {"content":i.get("vmjc_end_time")},
                {"content":i.get("vmjc_in_odometer")},
                {"content":i.get("vmjc_end_odometer")},
                {"content":i.get("vmjc_difference_of_days")},
            ])
        frappe.response['data'] = data
        frappe.response['columns'] = columns
    else:
        frappe.response["message"] = "vehicle data is required"
