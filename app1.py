""" Finances web app
"""

from Finances.System import System, fgzlib_date_list, fgzlib_time_list
from flask import Flask, render_template, redirect, url_for, request
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class Instance:
	def __init__(self):
		self.sys = None
		self.save = True
		
	def set_sys(self, sys):
		self.sys = sys
	
	def set_save(self, save=True):
		self.save = save

app = Flask(__name__)
sys = Instance()

@app.route('/Finances')
def financesMain():
	return render_template("index.html")

@app.route('/Finances/load/date-<date>/entry-<entry>')
def start(date, entry):
	if date == "recent":
		sys.set_sys(System.load_most_recent())
	else:
#		try:
		sys.set_sys(System.load_from_xml(date + ".fgz", int(entry)))
#		except:
			# Return to menu which selects set up, if fails.
#			return redirect(url_for("list_dates"))
	return redirect(url_for("display_summary"))

@app.route('/Finances/other')
def list_other_start_options():
	return render_template("other_start_options.html")
	
@app.route('/Finances/other/<option>')
def start_option_select(option):
	if option == "review":
		sys.set_save(False)
		return redirect(url_for("list_dates"))
	elif option == "reload":
		sys.set_save()
		return redirect(url_for("list_dates"))
	else:
		return redirect(url_for("list_other_start_options"))
	
@app.route('/Finances/datelist')
def list_dates():
	return render_template("datelist.html", dates=fgzlib_date_list())

@app.route('/Finances/load/date-<date>')
def list_times(date):
	times, comments = fgzlib_time_list(date)
	return render_template("timelist.html", indices=range(len(times)), date=date, times=times, comments=comments)
		
@app.route('/Finances/summary')
def display_summary():
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	return render_template("summary.html", sys=sys.sys, indices=range(len(sys.sys.accounts)))

def make_curve(accnum):
	curve = sys.sys.accounts[accnum].get_curve()
	fig, ax = plt.subplots(figsize=(7,3))
	fig.patch.set_facecolor('black')
	ax.set_facecolor('black')
	for spine in ax.spines:
		ax.spines[spine].set_color('white')
	ax.tick_params(axis='x', colors='white')
	ax.tick_params(axis='y', colors='white')
	ax.yaxis.label.set_color('white')
	ax.xaxis.label.set_color('white')
	ax.step(np.arange(32), curve, where="pre", c='white', zorder=1)
	ax.set_xlim(xmin=0.5, xmax=30.5)
	ax.set_ylim(ymin=0)
	ax.set_xlabel("Date")
	ax.set_ylabel("Minimum Balance, "+unichr(163))
	ax.set_xticks(np.arange(16)*2 + 1)
	ax.xaxis.labelpad=0
	today = datetime.now().day
	ax.vlines(today, ymin=0, ymax=curve[today], colors="r", zorder=3)
	ax.text(today, curve[today], unichr(163)+"{}".format(curve[today]), color="r")
	plt.savefig("static/curve.png", dpi=160, 
			    facecolor=fig.get_facecolor(), edgecolor='none')
    
@app.route('/Finances/Account<int:accnum>')
def display_account(accnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	make_curve(accnum)
	return render_template("account.html", sys=sys.sys, acc=accnum, img=datetime.now().strftime('%S%f'))

@app.route('/Finances/Account<int:accnum>/Bills')
@app.route('/Finances/Account<int:accnum>/Bills_<order>')
def display_bills(accnum, order="date"):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	rangen = range(len(sys.sys.accounts[accnum].bills))
	
	if order == "name":
		indices = order_indices_by_item_name(sys.sys.accounts[accnum].bills)
	elif order == "amount":
		indices = order_indices_by_item_value(sys.sys.accounts[accnum].bills)
	elif order == "date":
		indices = order_indices_by_item_date(sys.sys.accounts[accnum].bills)
	
	return render_template("bills.html", sys=sys.sys, acc=accnum, indices=indices, range=rangen)

@app.route('/Finances/Account<int:accnum>/Incomes')
@app.route('/Finances/Account<int:accnum>/Incomes_<order>')
def display_incomes(accnum, order="date"):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	rangen = range(len(sys.sys.accounts[accnum].incomes))
	
	if order == "name":
		indices = order_indices_by_item_name(sys.sys.accounts[accnum].incomes)
	elif order == "amount":
		indices = order_indices_by_item_value(sys.sys.accounts[accnum].incomes)
	elif order == "date":
		indices = order_indices_by_item_date(sys.sys.accounts[accnum].incomes)
	
	return render_template("incomes.html", sys=sys.sys, acc=accnum, indices=indices, range=rangen)

@app.route('/Finances/Account<int:accnum>/Transfers')
def display_transfers(accnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	rootIndices = []
	for i in range(len(sys.sys.accounts[accnum].out_transfers())):
		for j in range(len(sys.sys.accounts[accnum].transfers)):
			if sys.sys.accounts[accnum].out_transfers()[i] is sys.sys.accounts[accnum].transfers[j]:
				rootIndices.append(j)
	return render_template("transfers.html", 
						   sys=sys.sys, 
						   acc=accnum,
						   transfersIN = sys.sys.accounts[accnum].in_transfers(),
						   transfersOUT = sys.sys.accounts[accnum].out_transfers(),
						   indicesIN=range(len(sys.sys.accounts[accnum].in_transfers())),
						   indicesOUT=range(len(sys.sys.accounts[accnum].out_transfers())),
						   rootIndices=rootIndices)

@app.route('/Finances/AddAccount')
def display_add_account_form():
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	return render_template("add_account.html")
	
@app.route('/Finances/AddAccount/submit', methods=['POST', 'GET'])
def add_account():
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		sys.sys.add_account(name=request.form["name"], owner=request.form["owner"])
		if sys.save:
			sys.sys.write_xml("Added account: '" + request.form["name"] +"'")
		return redirect(url_for("display_summary"))
	return redirect(url_for("display_add_account_form"))

@app.route('/Finances/EditAccount<int:accnum>')
def display_edit_account_form(accnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	return render_template("edit_account.html", sys=sys.sys, acc=accnum)

@app.route('/Finances/EditAccount<int:accnum>/submit', methods=['POST', 'GET'])
def edit_account(accnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		sys.sys.accounts[accnum].name = request.form["name"]
		sys.sys.accounts[accnum].owner = request.form["owner"]
		sys.sys.accounts[accnum].account_num = request.form["acc_num"]
		sys.sys.accounts[accnum].sort_code = request.form["sort_code"]
		if sys.save:
			sys.sys.write_xml("Edited account: '" + request.form["name"] +"'")
		return redirect(url_for("display_summary"))
	return redirect(url_for("display_edit_account_form", accnum=accnum))	

@app.route('/Finances/DeleteAccount<int:accnum>')	
def display_delete_account_form(accnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	return render_template("delete_account.html", acc=accnum, sys=sys.sys)
		
@app.route('/Finances/DeleteAccount<int:accnum>/submit', methods=['POST', 'GET'])	
def delete_account(accnum):	
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		name = sys.sys.accounts[accnum].name
		sys.sys.delete_account(accnum)
		if sys.save:
			sys.sys.write_xml("Deleted account: '" + name + "'")
	return redirect(url_for("display_summary"))
	
@app.route('/Finances/Account<int:accnum>/Add<item>')
def display_add_item_form(accnum, item):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	return render_template("add_edit.html", sys=sys.sys, acc=accnum, action="Add", item=item, indices=range(len(sys.sys.accounts)))
	
@app.route('/Finances/Account<int:accnum>/Add<item>/submit', methods=['POST', 'GET'])
def add_item(accnum, item):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		if item == "Income":
			sys.sys.accounts[accnum].add_income(name=request.form["name"],
												value=float(request.form["value"]),
												date=int(request.form["date"]))
			if sys.save:
				sys.sys.write_xml("Added income: '" + request.form["name"] + 
							  "' to: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_incomes", accnum=accnum))
		elif item == "Bill":
			sys.sys.accounts[accnum].add_bill(name=request.form["name"],
											  value=float(request.form["value"]),
											  date=int(request.form["date"]))
			if sys.save:
				sys.sys.write_xml("Added bill: '" + request.form["name"] + 
							  "' to: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_bills", accnum=accnum))
		elif item == "Transfer":
			sys.sys.add_transfer(sys.sys.accounts[accnum],
							     sys.sys.accounts[int(request.form["target"])],
							     name=request.form["name"],
							     value=float(request.form["value"]),
								 rule=request.form["rule"],
							     date=int(request.form["date"]))
			if sys.save:
				sys.sys.write_xml("Added transfer: '" + request.form["name"] + 
							  "' to: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_transfers", accnum=accnum))
	
@app.route('/Finances/Account<int:accnum>/Edit<item>-<int:itemnum>')
def display_edit_item_form(accnum, item, itemnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	print item
	print itemnum
	if item == "Income":
		edited_item = sys.sys.accounts[accnum].incomes[itemnum]
	elif item == "Bill":
		edited_item = sys.sys.accounts[accnum].bills[itemnum]
	elif item == "Transfer":
		edited_item = sys.sys.accounts[accnum].transfers[itemnum]
	return render_template("add_edit.html", sys=sys.sys, acc=accnum, action="Edit", item=item, indices=range(len(sys.sys.accounts)), item_num=itemnum, edited_item=edited_item)
	
@app.route('/Finances/Account<int:accnum>/Edit<item>-<int:itemnum>/submit', methods=['POST', 'GET'])
def edit_item(accnum, item, itemnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		if item == "Income":
			sys.sys.accounts[accnum].incomes[itemnum].name = request.form["name"]
			sys.sys.accounts[accnum].incomes[itemnum].value = float(request.form["value"])
			sys.sys.accounts[accnum].incomes[itemnum].date = int(request.form["date"])
			if sys.save:
				sys.sys.write_xml("Edited income: '" + request.form["name"] + 
							  "' of: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_incomes", accnum=accnum))
		if item == "Bill":
			sys.sys.accounts[accnum].bills[itemnum].name = request.form["name"]
			sys.sys.accounts[accnum].bills[itemnum].value = float(request.form["value"])
			sys.sys.accounts[accnum].bills[itemnum].date = int(request.form["date"])
			if sys.save:
				sys.sys.write_xml("Edited bill: '" + request.form["name"] + 
							  "' of: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_bills", accnum=accnum))
		if item == "Transfer":
			sys.sys.accounts[accnum].transfers[itemnum].name = request.form["name"]
			sys.sys.accounts[accnum].transfers[itemnum].value = float(request.form["value"])
			sys.sys.accounts[accnum].transfers[itemnum].date = int(request.form["date"])
			sys.sys.accounts[accnum].transfers[itemnum].set_rule(request.form["rule"])
			sys.sys.accounts[accnum].transfers[itemnum].target = sys.sys.accounts[int(request.form["target"])]
			if sys.save:
				sys.sys.write_xml("Edited transfer: '" + request.form["name"] + 
							  "' from: '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_transfers", accnum=accnum))
	
@app.route('/Finances/Account<int:accnum>/Delete<item>-<int:itemnum>')
def display_delete_item_form(accnum, item, itemnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if item == "Income":
		deleted_item = sys.sys.accounts[accnum].incomes[itemnum]
	elif item == "Bill":
		deleted_item = sys.sys.accounts[accnum].bills[itemnum]
	elif item == "Transfer":
		deleted_item = sys.sys.accounts[accnum].transfers[itemnum]
	return render_template("delete_item.html", sys=sys.sys, acc=accnum, item=item, item_num=itemnum, item_to_delete=deleted_item)

@app.route('/Finances/Account<int:accnum>/Delete<item>-<int:itemnum>/submit', methods=['POST', 'GET'])
def delete_item(accnum, item, itemnum):
	if sys.sys is None:
		return redirect(url_for("financesMain"))
	if request.method == "POST":
		if item == "Income":
			name = sys.sys.accounts[accnum].incomes[itemnum].name
			del(sys.sys.accounts[accnum].incomes[itemnum])
			if sys.save:
				sys.sys.write_xml("Deleted income: '" + name + "' from '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_incomes", accnum=accnum))
		elif item == "Bill":
			name = sys.sys.accounts[accnum].bills[itemnum].name
			del(sys.sys.accounts[accnum].bills[itemnum])
			if sys.save:
				sys.sys.write_xml("Deleted bill: '" + name + "' from '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_bills", accnum=accnum))
		elif item == "Transfer":
			trans = sys.sys.accounts[accnum].transfers[itemnum]
			name = trans.name
			trans.source.delete_transfer_by_reference(trans)
			trans.target.delete_transfer_by_reference(trans)
			sys.sys.transfers.remove(trans)
			if sys.save:
				sys.sys.write_xml("Deleted transfer: '" + name + "' from '" + sys.sys.accounts[accnum].name + "'")
			return redirect(url_for("display_transfers", accnum=accnum))
	
def order_indices_by_item_value(item_list):
	indices = []
	def insert_in_order(i, item):
		for j in range(len(indices)):
			if item.value > item_list[indices[j]].value:
				indices.insert(j, i)
				return
		indices.append(i)
		return
	for i, item in enumerate(item_list):
		insert_in_order(i, item)
	return indices
		
def order_indices_by_item_date(item_list):
	indices = []
	def insert_in_order(i, item):
		for j in range(len(indices)):
			if item.date > item_list[indices[j]].date:
				indices.insert(j, i)
				return
		indices.append(i)
		return
	for i, item in enumerate(item_list):
		insert_in_order(i, item)
	indices.reverse()
	return indices
		
def order_indices_by_item_name(item_list):
	indices = []
	def insert_in_order(i, item):
		for j in range(len(indices)):
			if item.name > item_list[indices[j]].name:
				indices.insert(j, i)
				return
		indices.append(i)
		return
	for i, item in enumerate(item_list):
		insert_in_order(i, item)
	indices.reverse()
	return indices
	
if __name__ == "__main__":
	app.run(host='0.0.0.0')
	#app.run()