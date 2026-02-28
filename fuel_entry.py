import frappe
from frappe.model.document import Document

class FuelEntry(Document):
	
	def create_stock_entry(self):
		try:
			# Create a new Stock Entry document
			doc = frappe.new_doc("Stock Entry")
			date = str(self.get('date'))
			date = date.split(" ")
			doc.update({
				"stock_entry_type": 'Material Issue',
				"posting_date": date[0],
				"posting_time": date[1],
				"set_posting_time": 1,
				"remarks": self.name,
				"driver": self.driver_operator,
				"taxi_vehicle": self.taxi_vehicle if self.driver_operator == "Taxi Driver" else None,
				"truck_assigned": self.vehicle if self.driver_operator != "Taxi Driver" else None,
			})
			# Append item details to the Stock Entry
			doc.append("items", {
				'item_code': self.item,
				'uom': self.stock_uom,
				'qty': self.quantity,
				's_warehouse': self.warehouse
			})
			# Save and submit the Stock Entry
			doc.insert(ignore_permissions=True)
			doc.submit()
			# Update the reference in the fuel entry document
			self.stock_entry_ref = doc.name
		except Exception as error:
			frappe.log_error(message=str(error), title="Fuel Entry create_stock_entry error")
			frappe.throw("Stock not available")

	def before_submit(self):
		self.create_stock_entry()