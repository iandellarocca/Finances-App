""" System module
"""

from Account import Account
from Bill import Transfer
from datetime import datetime, date, time
import gzip
from lxml import etree

class System:
	def __init__(self):
		self.accounts = []
		self.transfers = []
		self.datetime = datetime.now()
		
	def add_account(self, **kwargs):
		account = Account(**kwargs)
		self.accounts.append(account)
		return account
		
	def delete_account(self, index):
		trans = []
		for i, transfer in enumerate(self.transfers):
			if transfer.source is self.accounts[index]:
				transfer.target.delete_transfer_by_reference(transfer)
				trans.append(i)
			elif transfer.target is self.accounts[index]:
				transfer.source.delete_transfer_by_reference(transfer)
				trans.append(i)
		for i in range(len(trans)):
			del(self.transfers[trans.pop()])
		del(self.accounts[index])
		
	def add_transfer(self, source, target, **kwargs):
		kwargs.update({"source":source, "target":target, "sys":self})
		transfer = Transfer(**kwargs)
		self.transfers.append(transfer)
		source.transfers.append(transfer)
		target.transfers.append(transfer)
		
	def total_income(self):
		value = 0.
		for account in self.accounts:
			value += (account.total_income() - account.total_out_transfers())
		return value
		
	def total_outgoings(self):
		value = 0.
		for account in self.accounts:
			value += (account.total_outgoings() - account.total_in_transfers())
		return value
		
	def render_xml_node(self):
		node = '<System date="{}" > \n'.format(self.datetime.isoformat())
		for account in self.accounts:
			node += account.render_xml_node() + "\n"
		for transfer in self.transfers:
			node += transfer.render_xml_node() + "\n"
		return node + "</System> \n"
		
	def render_lib_node(self, comment):
		node = '<Instance date="{}" '.format(date.today().isoformat())
		node += 'time="{}" '.format(datetime.now().time().isoformat())
		node += 'comment="' + comment + '" />\n'
		return node
		
	def write_xml(self, comment=""):
		with gzip.open("fgzlib.lib", "a") as fgzlib:
			fgzlib.write(self.render_lib_node(comment))
		with gzip.open(date.today().isoformat() + ".fgz", "a") as xmlfile:
			xmlfile.write(self.render_xml_node())
		
	def account_index(self, account):
		for i, acc in enumerate(self.accounts):
			if acc is account:
				return i
		return -1
		
	@classmethod
	def load_from_xml(cls, filenm, instance=-1):
		with gzip.open(filenm) as fgz:
			root = etree.fromstring("<root>" + fgz.read() + "</root>")
		sysnode = root.findall("System")[instance]
		sys = cls()
		for accnode in sysnode.findall("Account"):
			sys.accounts.append(Account.load_from_xml(accnode))
		for transnode in sysnode.findall("Transfer"):
			sys.transfers.append(Transfer.load_from_xml(sys, transnode))
		return sys
		
	@classmethod
	def load_most_recent(cls):
		with gzip.open("fgzlib.lib") as fgzlib:
			root = etree.fromstring("<root>" + fgzlib.read() + "</root>")
		recent = root.findall("Instance")[-1].attrib["date"]
		return cls.load_from_xml(recent + ".fgz")
		
def fgzlib_date_list():
	with gzip.open("fgzlib.lib") as fgzlib:
		root = etree.fromstring("<root>" + fgzlib.read() + "</root>")
	dates = []
	for entry in root.findall("Instance"):
		if entry.attrib['date'] not in dates:
			dates.append(entry.attrib['date'])
	return dates

def fgzlib_time_list(date):
	with gzip.open("fgzlib.lib") as fgzlib:
		root = etree.fromstring("<root>" + fgzlib.read() + "</root>")
	times = []
	comments = []
	for entry in root.findall("Instance"):
		if entry.attrib["date"] == date:
			times.append(entry.attrib['time'])
			comments.append(entry.attrib['comment'])
	return times, comments
	
if __name__ == "__main__":
	sys = System()
	a = sys.add_account(name="A")
	b = sys.add_account(name="B")
	sys.accounts[0].add_bill(name="Bill1", value=200.)
	sys.accounts[0].add_bill(name="Bill2", value=300.)
	sys.accounts[1].add_bill(name="Bill3", value=400.)
	sys.accounts[1].add_bill(name="Bill4", value=500.)
	sys.add_transfer(a, b, value=100.)
	print a.transfers
	a.delete_transfer_by_index(0)
	print a.transfers
	sys.write_xml()
	print sys.render_xml_node()
	sys3 = System.load_most_recent()
	print sys3.render_xml_node()
	sys3.add_transfer(sys3.accounts[0], sys3.accounts[1], value=100.)
	sys3.add_transfer(sys3.accounts[1], sys3.accounts[0], value=100.)
	print sys3.render_xml_node()
	sys3.delete_account(1)
	print sys3.render_xml_node()
	