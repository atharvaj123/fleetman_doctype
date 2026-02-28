# Copyright (c) 2024, Ambibuzz Technologies LLP and Contributors
# See license.txt

import frappe, json
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.utils import getdate
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_inter_company_sales_invoice
from erpnext.controllers.accounts_controller import get_taxes_and_charges


class VMJobCard(Document):
    def validate(self):
        if self.vmjc_jobs:
            for vmjc_job in self.vmjc_jobs:
                if vmjc_job.vmjcsd_resource_type == "Trailer" and not self.vmjc_trailer:
                    frappe.throw("Please select the Trailer in VM Job Card Form")

    # Method that runs before saving the document
    def before_save(self):
        self.update_last_service_info()
        self.update_part_service_info()
        self.update_job_service_info()

    # Method to update the last service information for the vehicle
    def update_last_service_info(self):
        if self.get("vmjc_vehicle"):
            filters = [
                ["VM Job Card", "vmjc_vehicle", "=", self.get("vmjc_vehicle")],
                ["VM Job Card", "docstatus", "=", "1"]
            ]
            fields = ["name", "vmjc_end_date"]
            vmjc_list = frappe.get_all("VM Job Card", fields=fields, filters=filters, page_length=1, order_by="vmjc_end_date desc")

            if vmjc_list and vmjc_list[0].get('name') != self.get('name'):
                self.vmjc_last_service_date = vmjc_list[0].get('vmjc_end_date')
                self.vmjc_last_vmjc_ref = vmjc_list[0].get('name')

    # Method to update service information for parts in the job card
    def update_part_service_info(self):
        filters = [
                ["VMJC Part Details", "vmjcpd_job_ref", "=", self.get("name")],
                ["VMJC Part Details", "vmjcpd_is_cancelled", "=", 0]
        ]
        fields = ["name"]
        vmjc_parts_list = frappe.get_all("VMJC Part Details", fields=fields, filters=filters)
        if vmjc_parts_list:
            for vmjc_parts in vmjc_parts_list:
                if vmjc_parts:
                    vmjc_parts_doc = frappe.get_doc("VMJC Part Details", vmjc_parts.get("name"))
                    vmjc_list = self.get_last_vm_job_card_parts(vmjc_parts_doc)
                    if vmjc_list and vmjc_list.get('name') != self.get('name'):
                        vmjc_parts_doc.vmjcpd_last_jc_date = vmjc_list.get('vmjc_end_date')
                        vmjc_parts_doc.vmjcpd_last_jc = vmjc_list.get('name')
                        vmjc_parts_doc.save()

    # Method to update service information for jobs in the job card
    def update_job_service_info(self):
        if self.vmjc_jobs:
            for vmjc_jobssd in self.vmjc_jobs:
                last_vmjc = self.get_last_vm_job_card_jobs(vmjc_jobssd)
                if last_vmjc and last_vmjc.get('name') != self.get('name'):
                    vmjc_jobssd.vmjcsd_last_jc_date = last_vmjc.get("vmjc_end_date")
                    vmjc_jobssd.vmjcsd_last_jc = last_vmjc.get('name')
                else:
                    vmjc_jobssd.vmjcsd_last_jc_date = ""
                    vmjc_jobssd.vmjcsd_last_jc = ""

    def get_last_vm_job_card_parts(self, vmjc_parts):
        # Define the doctypes
        VMJobCard = DocType("VM Job Card")
        VMJCPartDetails = DocType("VMJC Part Details")

        # Determine resource type and related fields
        resource_type = vmjc_parts.get("vmjcpd_resource_type")
        vmjc_resource = self.get(f"vmjc_{resource_type.lower()}")
        vmjcpd_part = vmjc_parts.get("vmjcpd_part")

        # Build the query
        query = (
            frappe.qb.from_(VMJobCard)
            .join(VMJCPartDetails)
            .on(VMJobCard.name == VMJCPartDetails.vmjcpd_job_ref)
            .where((VMJobCard[f"vmjc_{resource_type.lower()}"] == vmjc_resource) &
                (VMJCPartDetails.vmjcpd_part == vmjcpd_part) &
                (VMJCPartDetails.vmjcpd_resource_type == resource_type) &
                (VMJobCard.docstatus == 1))
            .select(VMJobCard.name, VMJobCard[f"vmjc_{resource_type.lower()}"], VMJobCard.vmjc_end_date, VMJobCard.modified)
            .orderby(VMJobCard.vmjc_end_date, order=frappe.qb.desc)
            .limit(1)
        )

        # Execute the query and fetch the result
        result = query.run(as_dict=True)

        # Return the result or None if not found
        if result:
            return result[0]
        else:
            return None
        
    def get_last_vm_job_card_jobs(self, vmjc_jobs):
        # Define the doctypes
        VMJobCard = DocType("VM Job Card")
        VMJCServiceDetails = DocType("VMJC Service Details")

        # Determine resource type and related fields
        resource_type = vmjc_jobs.get("vmjcsd_resource_type")
        vmjc_resource = self.get(f"vmjc_{resource_type.lower()}")
        vmjcsd_job = vmjc_jobs.get("vmjcsd_job")

        # Build the query
        query = (
            frappe.qb.from_(VMJobCard)
            .join(VMJCServiceDetails)
            .on(VMJobCard.name == VMJCServiceDetails.parent)
            .where((VMJobCard[f"vmjc_{resource_type.lower()}"] == vmjc_resource) &
                (VMJCServiceDetails.vmjcsd_job == vmjcsd_job) &
                (VMJCServiceDetails.vmjcsd_resource_type == resource_type) &
                (VMJobCard.docstatus == 1))
            .select(VMJobCard.name, VMJobCard[f"vmjc_{resource_type.lower()}"], 
                    VMJobCard.vmjc_end_date, VMJobCard.modified)
            .orderby(VMJobCard.modified, order=frappe.qb.desc)
            .limit(1)
        )

        # Execute the query and fetch the result
        result = query.run(as_dict=True)

        # Return the result or None if not found
        return result[0] if result else None

    # Method that runs before submitting the document
    def before_submit(self):
        # Validate odometer readings
        self.validate_odometer_reading()

        # Calculate the difference in days between start and end date
        self.calculate_service_duration()

        # Update schedule details for jobs and parts
        self.update_schedule_details_for_jobs()
        self.update_schedule_details_for_parts()

    # Validate that the end odometer reading is not less than the start odometer reading
    def validate_odometer_reading(self):
        if self.vmjc_end_odometer < 0 or self.vmjc_end_odometer < self.vmjc_in_odometer:
            frappe.throw("End Odometer cannot be less than Start Odometer")

    # Calculate the duration of the service in days
    def calculate_service_duration(self):
        date1 = getdate(self.get("vmjc_start_date"))
        date2 = getdate(self.get("vmjc_end_date"))
        date_diff = date2 - date1
        self.vmjc_difference_of_days = date_diff.total_seconds() / 86400

    # Update schedule details for jobs based on the job card
    def update_schedule_details_for_jobs(self):
        if self.vmjc_jobs:
            for vmjc_jobssd in self.vmjc_jobs:
                if not vmjc_jobssd.vmjcsd_is_external and not vmjc_jobssd.vmjcsd_dont_create_invoices:
                    try:
                        self.create_purchase_and_sales_invoice(vmjc_jobssd)
                    except Exception as e:
                        frappe.log_error(f"Failed to Submit VM Job Card {self.get('name')}", f"{e} {frappe.get_traceback()}")
                        frappe.throw(f"Failed to submit VM Job Card {self.get('name')}")
                    
                # Determine resource type and related fields
                resource_type = vmjc_jobssd.get("vmjcsd_resource_type")
                vmjc_resource = self.get(f"vmjc_{resource_type.lower()}")
                filters = [
                    ["VM Schedule Details", "vmsd_service", "=", vmjc_jobssd.get("vmjcsd_job")],
                    ["VM Schedule Details", "parent", "=", vmjc_resource],
                    ["VM Schedule Details", "parentfield", "=", "vms_schedule"],
                    ["VM Schedule Details", "parenttype", "=", "Vehicle Maintenance Schedule"]
                ]
                fields = ["name"]
                vms_list = frappe.get_all("VM Schedule Details", fields=fields, filters=filters)

                for vms in vms_list:
                    vmsd = frappe.get_doc("VM Schedule Details", vms.get('name'))
                    vmsd.vmsd_last_odometer = self.vmjc_end_odometer
                    vmsd.vmsd_last_maintenance_date = self.vmjc_end_date
                    vmsd.last_vm_job_reference = self.name
                    vmsd.save()

     # Update schedule details for parts based on the job card
    def update_schedule_details_for_parts(self):
        filters = [
                ["VMJC Part Details", "vmjcpd_job_ref", "=", self.get("name")]
        ]
        fields = ["name"]
        vmjc_parts_list = frappe.get_all("VMJC Part Details", fields=fields, filters=filters)
        if vmjc_parts_list:
            for vmjc_parts in vmjc_parts_list:
                vmjc_parts_doc = frappe.get_doc("VMJC Part Details", vmjc_parts.get("name"))
                if vmjc_parts_doc.vmjcpd_qty <= 0:
                    frappe.throw(f"{vmjc_parts_doc.get('vmjcpd_part')} Quantity cannot be negative or zero")
                
                # Determine resource type and related fields
                resource_type = vmjc_parts_doc.get("vmjcpd_resource_type")
                vmjc_resource = self.get(f"vmjc_{resource_type.lower()}")

                filters = [
                    ["VM Schedule Details", "vmsd_part", "=", vmjc_parts_doc.get("vmjcpd_part")],
                    ["VM Schedule Details", "parent", "=", vmjc_resource],
                    ["VM Schedule Details", "parentfield", "=", "vms_schedule"],
                    ["VM Schedule Details", "parenttype", "=", "Vehicle Maintenance Schedule"]
                ]
                fields = ["name"]
                vms_list = frappe.get_all("VM Schedule Details", fields=fields, filters=filters)

                for vms in vms_list:
                    vmsd = frappe.get_doc("VM Schedule Details", vms.get('name'))
                    vmsd.vmsd_last_odometer = self.vmjc_end_odometer
                    vmsd.vmsd_last_maintenance_date = self.vmjc_end_date
                    vmsd.last_vm_job_reference = self.name
                    vmsd.save()
    
    def update_vms_parts_job_on_cancelled(self):
        filters = [
            ["VM Schedule Details", "last_vm_job_reference", "=", self.get('name')]
        ]
        fields = ["name"]
        vms_list = frappe.get_all("VM Schedule Details", fields=fields, filters=filters)

        for vms in vms_list:
            vmsd = frappe.get_doc("VM Schedule Details", vms.get('name'))
            filters = [
                    ["VMJC Part Details", "vmjcpd_job_ref", "=", vmsd.get("last_vm_job_reference")],
                    ["VMJC Part Details", "vmjcpd_part", "=", vmsd.get("vmsd_part")]
            ]
            fields = ["name", "vmjcpd_last_jc"]
            vmjc_parts_list = frappe.get_all("VMJC Part Details", fields=fields, filters=filters)
            for vmjc_part in vmjc_parts_list:
                if vmjc_part.get("vmjcpd_last_jc"):
                    last_last_vmjc = frappe.get_doc("VM Job Card", vmjc_part.get("vmjcpd_last_jc"))
                    if last_last_vmjc:
                        vmsd.vmsd_last_odometer = last_last_vmjc.vmjc_end_odometer
                        vmsd.vmsd_last_maintenance_date = last_last_vmjc.vmjc_end_date
                        vmsd.last_vm_job_reference = last_last_vmjc.name
                        vmsd.save()
                else:
                    vmsd.vmsd_last_odometer = 0
                    vmsd.vmsd_last_maintenance_date = None
                    vmsd.last_vm_job_reference = None
                    vmsd.save()

            filters = [
                    ["VMJC Service Details", "parent", "=", vmsd.get("last_vm_job_reference")],
                    ["VMJC Service Details", "vmjcsd_job", "=", vmsd.get("vmsd_service")]
            ]
            fields = ["name", "vmjcsd_last_jc"]
            vmjc_service_list = frappe.get_all("VMJC Service Details", fields=fields, filters=filters)
            for vmjc_service in vmjc_service_list:
                if vmjc_service.get("vmjcsd_last_jc"):
                    last_last_vmjc = frappe.get_doc("VM Job Card", vmjc_service.get("vmjcsd_last_jc"))
                    if last_last_vmjc:
                        vmsd.vmsd_last_odometer = last_last_vmjc.vmjc_end_odometer
                        vmsd.vmsd_last_maintenance_date = last_last_vmjc.vmjc_end_date
                        vmsd.last_vm_job_reference = last_last_vmjc.name
                        vmsd.save()
                else:
                    vmsd.vmsd_last_odometer = 0
                    vmsd.vmsd_last_maintenance_date = None
                    vmsd.last_vm_job_reference = None
                    vmsd.save()

    def on_cancel(self):
        # Fetch all the VMJC Part Details linked to this Job Card
        part_details = frappe.get_all('VMJC Part Details', filters={'vmjcpd_job_ref': self.name}, fields=['name'])
        
        # Loop through each part and set vmjcpd_is_cancelled = 1
        for part in part_details:
            frappe.set_value('VMJC Part Details', part['name'], 'vmjcpd_is_cancelled', 1)

        self.update_vms_parts_job_on_cancelled()
        self.cancel_vmjc_pi_and_si()
    
        
    def cancel_vmjc_pi_and_si(self):
        if self.vmjc_jobs:
            for vmjc_jobssd in self.vmjc_jobs:
                if vmjc_jobssd.vmjcsd_is_external or vmjc_jobssd.vmjcsd_dont_create_invoices:
                    continue
                si_ref = vmjc_jobssd.vmjcsd_sales_invoice
                pi_ref = vmjc_jobssd.vmjcsd_purchase_invoice
                # Cancel Sales Invoice
                if si_ref:
                    try:
                        si = frappe.get_doc("Sales Invoice", si_ref)
                        if si.docstatus == 1:
                            si.cancel()
                    except frappe.DoesNotExistError:
                        frappe.throw(f"Failed to cancel VM Job Card")
                # Cancel Purchase Invoice
                if pi_ref:
                    try:
                        pi = frappe.get_doc("Purchase Invoice", pi_ref)
                        if pi.docstatus == 1:
                            pi.cancel()
                    except frappe.DoesNotExistError:
                        frappe.throw(f"Failed to cancel VM Job Card")


    # Create a Purchase Invoice and Sales Invoice for the job card
    def create_purchase_and_sales_invoice(self, vmjc_jobssd):
        pass
        # # Validate job amount 
        # if int(vmjc_jobssd.vmjcsd_amount) <= 0:
        #     frappe.throw(f"Amount for Job {vmjc_jobssd.get('vmjcsd_job')} cannot be negative or zero")

        # # Create a new Purchase Invoice
        # pi = frappe.new_doc("Purchase Invoice")
        # pi.supplier = "World King Garage LLC"
        # pi.set_posting_time = 1
        # pi.posting_date = vmjc_jobssd.vmjcsd_date

        # # Conditionally add taxes to Purchase Invoice
        # if vmjc_jobssd.vmjcsd_is_tax:
        #     if not vmjc_jobssd.vmjcsd_p_taxes_and_charges:
        #         frappe.throw("Please select Purchase Taxes and Charges Template in VM Job Card Form {vmjc_jobssd.get('vmjcsd_job')}")
        #     purchase_tax_template = vmjc_jobssd.vmjcsd_p_taxes_and_charges
        #     pi.taxes_and_charges = purchase_tax_template
        #     taxes = get_taxes_and_charges("Purchase Taxes and Charges Template", pi.taxes_and_charges)
        #     for tax in taxes:
        #         pi.append("taxes", tax)
                
        # pi.set("items", [])
        # pi.append("items", {
        #     "item_code": vmjc_jobssd.get("vmjcsd_job"),
        #     "qty": "1",
        #     "rate": vmjc_jobssd.get("vmjcsd_amount")
        # })
        # # # Save and submit the Purchase Invoice
        # pi.insert(ignore_permissions=True)
        # pi.flags.ignore_permissions = True
        # pi.submit()
        # vmjc_jobssd.vmjcsd_purchase_invoice = pi.name
        # there is a permission issue with make_inter_company_sales_invoice for sometime we are commenting this code
        # if pi.docstatus == 1:
        #     # Check inter-company setup and create Sales Invoice            
        #     # Create Sales Invoice
        #     sales_invoice = make_inter_company_sales_invoice(pi.name)
        #     sales_invoice.set_posting_time = 1
        #     sales_invoice.posting_date = vmjc_jobssd.vmjcsd_date
        #     # Conditionally add taxes to Sales Invoice
        #     if vmjc_jobssd.vmjcsd_is_tax:
        #         if not vmjc_jobssd.vmjcsd_s_taxes_and_charges:
        #             frappe.throw("Please select Sales Taxes and Charges Template in VM Job Card Form {vmjc_jobssd.get('vmjcsd_job')}")
        #         sales_tax_template = vmjc_jobssd.vmjcsd_s_taxes_and_charges  # Can be same or different template
        #         sales_invoice.taxes_and_charges = sales_tax_template
        #         taxes = get_taxes_and_charges("Sales Taxes and Charges Template", sales_invoice.taxes_and_charges)
        #         for tax in taxes:
        #             sales_invoice.append("taxes", tax)

        #     sales_invoice.insert()
        #     sales_invoice.submit()
        #     vmjc_jobssd.vmjcsd_sales_invoice = sales_invoice.name