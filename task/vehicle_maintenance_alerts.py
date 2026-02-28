# Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe.utils
from frappe.utils import getdate, today
from datetime import timedelta

def main():
    #Fetch all Vehicle Maintenance Schedule list
    vms_list = frappe.get_all("Vehicle Maintenance Schedule",fields=["*"])
    for vms in vms_list:
        #Fetch all VM Schedule Details list refrence to vms
        vms_details_list = frappe.get_all("VM Schedule Details", fields=["*"], filters=[["parent","=",vms.get("name")],["parenttype","=","Vehicle Maintenance Schedule"],["parentfield","=","vms_schedule"]])
        vms_last_trip_odo = int(vms.get("vms_last_trip_odo"))
        for vms_details in vms_details_list:
            vmsd_distance = vms_details.get("vmsd_distance")
            vmsd_maintenance_period_type = vms_details.get("vmsd_maintenance_period_type")

            # Alert on mileage condition
            if vmsd_maintenance_period_type == "Mileage":
                mileage = vms_details.get("mileage")
                if vms_last_trip_odo > mileage and not vms_details.get("dont_send_alert"):
                    create_alert(vms, vms_details)

            # Alert on Distance condition
            if vmsd_maintenance_period_type == "Distance":
                vmsd_last_odometer = vms_details.get("vmsd_last_odometer")
                if (vms_last_trip_odo-vmsd_last_odometer) >= vmsd_distance:
                    create_alert(vms, vms_details)

            # Alert on Duration condition
            if vmsd_maintenance_period_type == "Duration":
                date1 = getdate(vms_details.get("vmsd_last_maintenance_date"))
                date2 = getdate(today())
                date_diff = date2 - date1
                vmsd_duration = vms_details.get("vmsd_duration") / 86400
                days_difference = date_diff.total_seconds() / 86400
                if days_difference >= vmsd_duration:
                    create_alert(vms, vms_details)

            # Alert on Date condition
            if vmsd_maintenance_period_type == "Date" and not vms_details.get("dont_send_alert"):
                date1 = getdate(vms_details.get("date"))
                date2 = getdate(today())
                date_diff = date2 - date1
                days_difference = date_diff.total_seconds() / 86400
                if days_difference >= 0:
                    create_alert(vms, vms_details)


def create_alert(vms, vms_details):
    alert = frappe.new_doc("Vehicle Job Alert")
    alert.vehicle = vms.get("vms_vehicle")
    alert.date = frappe.utils.now()
    partorservice = vms_details.get("vmsd_part") if vms_details.get("vmsd_part") else vms_details.get("vmsd_service")
    alert.reason = f"Maintenance  of {partorservice} Part / Service of {vms.get('vms_vehicle')}"
    alert.vehicle_maintenance_schedule = vms.get("name")
    alert.save()
