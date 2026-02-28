# Copyright (c) 2024, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance
from frappe.query_builder import DocType


class VMJCPartDetails(Document):
	def before_save(self):
		self.create_stock_entry()	
		if self.vmjcpd_is_cancelled:
			self.cancel_stock_entry()	
		
		vmjc_list = self.get_last_vm_job_card_parts()
		if vmjc_list and vmjc_list.get('name') != self.get('name'):
			self.vmjcpd_last_jc_date = vmjc_list.get('vmjc_end_date')
			self.vmjcpd_last_jc = vmjc_list.get('name')

	def get_last_vm_job_card_parts(self):
		# Define the doctypes
		VMJobCard = DocType("VM Job Card")
		VMJCPartDetails = DocType("VMJC Part Details")
		vmjc_doc = frappe.get_doc("VM Job Card", self.vmjcpd_job_ref)
		# Determine resource type and related fields
		resource_type = self.get("vmjcpd_resource_type")
		vmjc_resource = vmjc_doc.get(f"vmjc_{resource_type.lower()}")
		vmjcpd_part = self.get("vmjcpd_part")

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
	
	def cancel_stock_entry(self):
		"""Cancel the associated stock entry if it exists."""
		if self.vmjcpd_stock_ref:
			try:
				# Fetch the stock entry document
				stock_entry = frappe.get_doc("Stock Entry", self.vmjcpd_stock_ref)
				self.vmjcpd_cancelling_date = frappe.utils.now()

				# Check if the stock entry is already canceled
				if stock_entry.docstatus == 2:
					# frappe.msgprint(f"Stock Entry {self.vmjcpd_stock_ref} is already canceled.")
					return

				# Cancel the stock entry
				stock_entry.cancel()
				# frappe.msgprint(f"Stock Entry {self.vmjcpd_stock_ref} has been successfully canceled.")

			except Exception as e:
				# Log the error and throw an error message
				frappe.log_error(f"Error while canceling Stock Entry {self.vmjcpd_stock_ref}: {str(e)}", f"VM Job Card {self.name} Stock Entry Cancelation Error")
				# frappe.throw(f"Unable to cancel Stock Entry {self.vmjcpd_stock_ref} due to the following error: {str(e)}")
				
	# Create a stock entry for the parts used in the job
	def create_stock_entry(self):
		"""Create a stock entry for the parts used in the VM Job Card after validating stock availability."""

		if self.vmjcpd_stock_ref:
			self.vmjcpd_stock_cost = frappe.get_value("Stock Entry", self.vmjcpd_stock_ref, "total_amount")
			return 
		
		# Initialize a new Stock Entry document
		stock_entry = frappe.get_doc({
			'doctype': 'Stock Entry',
			'truck_assigned': self.vmjcpd_vehicle,
			'stock_entry_type': 'Material Issue',  # or 'Material Receipt', based on your use case
			'items': []
		})

		if self.vmjcpd_resource_type == "Trailer":
			stock_entry.truck_assigned = self.vmjcpd_trailer


		if self.vmjcpd_part and self.vmjcpd_qty > 0:
			# Check stock availability for each part before adding it to the stock entry
			available_qty = self.get_available_stock(self.vmjcpd_warehouse, self.vmjcpd_part)

			# If stock is insufficient, throw an error
			if available_qty < self.vmjcpd_qty:
				frappe.throw(f"Insufficient stock for part {self.vmjcpd_part} in warehouse {self.vmjcpd_warehouse}. "
							f"Available: {available_qty}, Required: {self.vmjcpd_qty}. Unable to Save.")

			# If stock is sufficient, append the item to the Stock Entry
			item =  {
				'item_code': self.vmjcpd_part,
				'qty': self.vmjcpd_qty,
				's_warehouse': self.vmjcpd_warehouse,
				'allow_zero_valuation_rate': 1,
			}
			if self.vmjcpd_batch:
				item["batch_no"] = self.vmjcpd_batch
				item["use_serial_batch_fields"] = 1
			if self.vmjcpd_serial_no:
				item["serial_no"] = self.vmjcpd_serial_no
				item["use_serial_batch_fields"] = 1
				
			stock_entry.append('items', item)

		# Validate that at least one item is added to the stock entry
		if not stock_entry.items:
			frappe.throw(f"No valid items available in VM Job Card {self.name}")

		try:
			# Try to insert and submit the Stock Entry
			stock_entry.insert()
			stock_entry.submit()
			self.vmjcpd_stock_ref = stock_entry.get("name")
			self.vmjcpd_stock_cost = stock_entry.get("value_difference")

		except Exception as e:
			# Log the exception or notify the user that submission failed
			frappe.log_error("Error during stock entry submission from vmjob card issue parts", f"Error during stock entry submission: {str(e)} VM Job Card {self.name} Stock Entry Error")

			# Throw a user-friendly error message specific to the VM Job Card
			frappe.throw(f"Unable to submit VM Job Card {self.name} due to the following error: {str(e)}")

 
	 # Update schedule details for parts based on the job card
	
	

	def get_available_stock(self, warehouse, item):
		"""
		Fetch the available stock for a given item in a specific warehouse using the Stock Ledger Entry.
		:param warehouse: Warehouse from which to check stock.
		:param item: Item for which stock availability is checked.
		:return: Available stock quantity.
		"""
		stock_balance = get_stock_balance(item, warehouse)

		# Return the available quantity or 0 if no record is found
		return stock_balance if stock_balance else 0
