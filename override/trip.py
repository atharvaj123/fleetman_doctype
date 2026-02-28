# Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from abz_vmm.abz_vmm.doctype.trip.trip import Trip

class CustomTrip(Trip):
    def before_submit(self):
        super().before_submit()
        try:
            # Updating Vehicle Maintenance Schedule vms_last_trip_odo vms_last_trip_ref Before submit of trip
            vms_doc = frappe.get_doc("Vehicle Maintenance Schedule", self.vehicle)
            vms_doc.vms_last_trip_odo = self.trip_end_odometer
            vms_doc.vms_last_trip_ref = self.name
            vms_doc.save()
        except frappe.DoesNotExistError:
            frappe.log_error(frappe.get_traceback(), _("Vehicle Maintenance Schedule not found for vehicle: {0}").format(self.vehicle))
        except frappe.ValidationError as e:
            frappe.log_error(frappe.get_traceback(), _("Validation error while updating Vehicle Maintenance Schedule: {0}").format(str(e)))
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Unexpected error in updating Vehicle Maintenance Schedule"))
