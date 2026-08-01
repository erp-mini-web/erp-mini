from flask import Flask, render_template, request

app = Flask(__name__)

# 商品レシピ
products = {
    "Y001": {"K001": 30, "K002": 20, "K003": 0,  "K004": 0,  "K005": 0},
    "Y002": {"K001": 10, "K002": 40, "K003": 10, "K004": 0,  "K005": 0},
    "Y003": {"K001": 0,  "K002": 20, "K003": 30, "K004": 10, "K005": 0},
    "Y004": {"K001": 50, "K002": 0,  "K003": 0,  "K004": 20, "K005": 10},
    "Y005": {"K001": 10, "K002": 10, "K003": 10, "K004": 10, "K005": 10},
    "Y006": {"K001": 60, "K002": 20, "K003": 0,  "K004": 0,  "K005": 0},
    "Y007": {"K001": 25, "K002": 25, "K003": 25, "K004": 0,  "K005": 0},
    "Y008": {"K001": 35, "K002": 15, "K003": 0,  "K004": 20, "K005": 0},
    "Y009": {"K001": 45, "K002": 5,  "K003": 10, "K004": 10, "K005": 10},
    "Y010": {"K001": 30, "K002": 30, "K003": 30, "K004": 0,  "K005": 0}
}

# 在庫
stock_Y = {code: 0 for code in products.keys()}

stock_K = {
    "K001": [100, 80, 55],
    "K002": [100, 60],
    "K003": [100],
    "K004": [90, 30],
    "K005": [100]
}

stock_H = {
    "H001": 100,
    "H002": 100,
    "H003": 100
}

sales_data = []


def cut_roll(rolls, selected_length, need):
    if selected_length not in rolls:
        return False

    idx = rolls.index(selected_length)

    if rolls[idx] >= need:
        rolls[idx] -= need
        if rolls[idx] == 0:
            rolls.pop(idx)
        return True

    return False


@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/stock")
def stock():
    return render_template("stock.html", stock_Y=stock_Y, stock_K=stock_K, stock_H=stock_H)


@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    if request.method == "POST":
        material = request.form.get("material")
        quantity = int(request.form.get("quantity"))

        if material in stock_H:
            stock_H[material] += quantity
            return f"{material} を {quantity} 追加しました"

        return "不明な原材料コードです"

    return render_template("purchase.html")


@app.route("/shipment", methods=["GET", "POST"])
def shipment():
    if request.method == "POST":
        product = request.form.get("product")
        quantity = int(request.form.get("quantity"))

        if stock_Y.get(product, 0) >= quantity:
            stock_Y[product] -= quantity
            sales_data.append({"product": product, "quantity": quantity})
            return f"{product} を {quantity} 出荷しました"

        return f"{product} の在庫が不足しています"

    return render_template("shipment.html", stock_Y=stock_Y)


@app.route("/sales")
def sales():
    return render_template("sales.html", sales_data=sales_data)


@app.route("/order", methods=["GET", "POST"])
def order():

    # 初期表示
    if request.method == "GET":
        return render_template("order.html", products=products)

    selected_product = request.form.get("product")

    # 商品未選択 → 初期画面
    if not selected_product:
        return render_template("order.html", products=products)

    # 「ロール表示ステップ」か「製造ステップ」かを判定
    # roll_K*** が1つも無ければ「ロール表示ステップ」
    has_roll_selection = any(
        f"roll_{k_code}" in request.form for k_code in stock_K.keys()
    )

    # ロール表示ステップ（商品コードを選んだだけ or 商品コードを変更しただけ）
    if not has_roll_selection:
        recipe = products[selected_product]
        return render_template(
            "order.html",
            products=products,
            selected_product=selected_product,
            recipe=recipe,
            stock_K=stock_K
        )

    # ここから製造ステップ（ロールも選ばれていて、受注するが押された）
    quantity = int(request.form.get("quantity"))
    recipe = products[selected_product]

    # 必要量（切りしろ +5m）
    need = {}
    for k_code, base_amount in recipe.items():
        need[k_code] = base_amount * quantity + (5 if base_amount > 0 else 0)

    # 選ばれたロールを使って切る
    for k_code, amount in need.items():
        if amount == 0:
            continue

        selected_length = int(request.form.get(f"roll_{k_code}"))

        if not cut_roll(stock_K[k_code], selected_length, amount):
            return f"{k_code} の {selected_length}m ロールでは {amount}m 切れません"

    stock_Y[selected_product] += quantity
    return f"{selected_product} を {quantity} 製造しました（選択したロールから切り出し）"


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
