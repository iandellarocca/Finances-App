""" Bill module
"""

class Bill:
	def __init__(self, **kwargs):
		kwlib = {"name":"", 
				 "value":0.0, 
				 "date":0,
				 "account":None,
                 "standing":False}
		kwlib.update(kwargs)
		self.name = kwlib["name"]
		self.value = kwlib["value"]
		self.date = kwlib["date"]
		self.account = kwlib["account"]
        # True if standing order, false if Direct Debit
		self.is_standing_order = kwlib["standing"]
        
	def get_value(self):
		return self.value
	
	def render_xml_node(self):
		return '\t\t<Bill name="{}" value="{}" date="{}" standing="{}" />'.format(self.name, self.value, self.date, int(self.is_standing_order))
		
	@classmethod
	def load_from_xml(cls, element):
		try:
			standing=bool(element.attrib["standing"])
		except:
			standing=False
		return cls(name=element.attrib["name"],
				   value=float(element.attrib["value"]),
				   date=int(element.attrib["date"]),
                   standing=standing)

class Income(Bill):
	def render_xml_node(self):
		return '\t\t<Income name="{}" value="{}" date="{}" />'.format(self.name, self.value, self.date)
        

class Transfer:
	def __init__(self, **kwargs):
		kwlib = {"name":"",
				 "value":0.0,
				 "date":0,
				 "rule":None,
				 "source":None,
				 "target":None,
				 "sys":None
                 }
		kwlib.update(kwargs)
		self.name = kwlib["name"]
		self.value = kwlib["value"]
		self.date = kwlib["date"]
		self.source = kwlib["source"]	
		self.target = kwlib["target"]
		self.sys = kwlib["sys"]
		self.rule = kwlib["rule"]
		
	def set_rule(self, rule=None):
		self.rule = rule
		
	def get_value(self):
		if self.rule is None:
			return self.value
		else:
			try:
				exec("self.value = " + self.rule)
			except:
				rule = None
				print "Rule not set."
		return self.value
		
	def render_xml_node(self):
		node = '\t<Transfer name="{}" value="{}" date="{}"'.format(self.name, self.value, self.date)
		if self.rule is not None: 
			node += ' rule="{}"'.format(self.rule)
		node += ' source="{}"'.format(self.sys.account_index(self.source))
		node += ' target="{}"/>'.format(self.sys.account_index(self.target))
		return node
		
	@classmethod
	def load_from_xml(cls, sys, element):
		try:
			rule = element.attrib["rule"]
		except:
			rule = None
		transfer = cls(name=element.attrib["name"],
					   value=float(element.attrib["value"]),
				       date=int(element.attrib["date"]),
				       rule=rule,
				       source=sys.accounts[int(element.attrib["source"])],
				       target=sys.accounts[int(element.attrib["target"])],
				       sys=sys)
		if transfer.rule == "":
			transfer.rule = None
		transfer.source.transfers.append(transfer)
		transfer.target.transfers.append(transfer)
		return transfer
		
if __name__ == "__main__":
	#bill = Bill(name="abc", value=500.)
	#print bill.name, bill.value
	#income = Income(name="cba", value=5.)
	#print income.name, income.value
	transfer = Transfer(name="xyz")
	#print transfer.name
	transfer.set_rule("45")
	print transfer.get_value()