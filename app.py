from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        product = request.form.get("product")
        quantity = int(request.form.get("quantity"))
        return f"{product} を {quantity} 個受注しました"
    return render_template("order.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
