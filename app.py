from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/orders")
def orders():
    return render_template("orders.html")

@app.route("/shipments")
def shipments():
    return render_template("shipments.html")

@app.route("/receipts")
def receipts():
    return render_template("receipts.html")

@app.route("/stocks")
def stocks():
    return render_template("stocks.html")

@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

@app.route("/sales")
def sales():
    return render_template("sales.html")

@app.route("/costs")
def costs():
    return render_template("costs.html")

@app.route("/masters")
def masters():
    return render_template("masters.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

if __name__ == "__main__":
    app.run(debug=True)
