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
        # 在庫確認ロジックをここに追加予定
        return f"{product} を {quantity} 個受注しました"
    return render_template("order.html")
