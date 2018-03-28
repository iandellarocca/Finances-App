""" Account module
"""

from Bill import Bill, Income, Transfer

class Account:
	def __init__(self, **kwargs):
		kwlib = {"name":"",
				 "owner":""}
		kwlib.update(kwargs)
		self.name = kwlib["name"]
		self.owner = kwlib["owner"]
		self.bills = []
		self.incomes = []
		self.transfers = []
		
	def add_bill(self, **kwargs):
		self.bills.append(Bill(**kwargs))
		
	def add_income(self, **kwargs):
		self.incomes.append(Income(**kwargs))
		
	def total_income(self):
		value = self.total_in_transfers()
		for income in self.incomes:
			value += income.value
		return value
		
	def total_income_t(self):
		value = 0.
		for income in self.incomes:
			value += income.value
		return value
	
	def in_transfers(self):
		list = []
		for trans in self.transfers:
			if trans.target is self:
				list.append(trans)
		return list
	
	def total_in_transfers(self):
		value = 0.
		for trans in self.in_transfers():
			value += trans.get_value()
		return value
	
	def out_transfers(self):
		list = []
		for trans in self.transfers:
			if trans.source is self:
				list.append(trans)
		return list
		
	def total_out_transfers(self):
		value = 0.
		for trans in self.out_transfers():
			value += trans.get_value()
		return value
		
	def total_outgoings(self):
		value = self.total_out_transfers()
		for bill in self.bills:
			value += bill.value
		return value
		
	def delete_transfer_by_index(self, index):
		del(self.transfers[index])
		
	def delete_transfer_by_reference(self, transref):
		for i, trans in enumerate(self.transfers):
			if trans is transref:
				self.delete_transfer_by_index(i)
				return
		
	def render_xml_node(self):
		node = '\t<Account name="{}" owner="{}" > \n'.format(self.name, self.owner)
		for bill in self.bills:
			node += bill.render_xml_node() + '\n'
		for income in self.incomes:
			node += income.render_xml_node() + '\n'
		return node + '\t</Account>'
		
	@classmethod
	def load_from_xml(cls, element):
		acc = cls(name=element.attrib["name"],
			      owner=element.attrib["owner"])
		for bill_element in element.findall("Bill"):
			acc.bills.append(Bill.load_from_xml(bill_element))
		for income_element in element.findall("Income"):
			acc.incomes.append(Income.load_from_xml(income_element))
		return acc
		
if __name__ == "__main__":
	acc = Account(name="abc", owner="ABC")
	acc.add_income(value=10.)
	acc.add_income(value=20.)
	print acc.name, acc.owner, acc.total_income()
	