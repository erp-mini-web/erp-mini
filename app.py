from flask import Flask, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# -------------------------
# 商品レシピ
# -------------------------
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

# -------------------------
# 在庫データ（ロール管理）
# -------------------------
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

# -------------------------
# 受注データ
# -------------------------
orders = []
order_counter = 1

def next_order_no():
    global order_counter
    order_no = f"T{order_counter:05d}"
    order_counter += 1
    return order_no


# -------------------------
# ロールを切る関数
# -------------------------
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


# -------------------------
# メニュー
# -------------------------
@app.route("/")
def menu():
    return render_template("menu.html")


# -------------------------
# 在庫画面
# -------------------------
@app.route("/stock")
def stock():
    return render_template("stock.html", stock_Y=stock_Y, stock_K=stock_K, stock_H=stock_H)


# -------------------------
# 購入
# -------------------------
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


# -------------------------
# 出荷
# -------------------------
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


# -------------------------
# 売上
# -------------------------
@app.route("/sales")
def sales():
    return render_template("sales.html", sales_data=sales_data)


# -------------------------
# 受注（A-1方式）
# -------------------------
@app.route("/order", methods=["GET", "POST"])
def order():

    # 初期表示
    if request.method == "GET":
        return render_template(
            "order.html",
            products=products,
            details=[]
        )

    action = request.form.get("action")

    # ヘッダー情報
    input_user = request.form.get("input_user")
    customer_code = request.form.get("customer_code")
    delivery_date = request.form.get("delivery_date")
    shipping_address = request.form.get("shipping_address")
    shipping_method = request.form.get("shipping_method")

    # 明細（フォームで保持）
    details_raw = request.form.get("details_data")
    details = json.loads(details_raw) if details_raw else []

    # 商品追加フォーム
    product_code = request.form.get("product_code")
    quantity_raw = request.form.get("quantity")

    # 原材料表示ステップ
    if action == "show_material":
        if not product_code or not quantity_raw:
            return "商品コードと数量を入力してください"

        quantity = int(quantity_raw)
        recipe = products[product_code]

        need = {}
        for k_code, base_amount in recipe.items():
            need[k_code] = base_amount * quantity + (5 if base_amount > 0 else 0)

        return render_template(
            "order.html",
            products=products,
            input_user=input_user,
            customer_code=customer_code,
            delivery_date=delivery_date,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            product_code=product_code,
            quantity=quantity,
            need=need,
            stock_K=stock_K,
            details=details
        )

    # 明細追加ステップ
    if action == "add_detail":
        quantity = int(quantity_raw)
        recipe = products[product_code]

        need = {}
        roll_selection = {}

        for k_code, base_amount in recipe.items():
            need[k_code] = base_amount * quantity + (5 if base_amount > 0 else 0)

            if need[k_code] > 0:
                roll_selection[k_code] = int(request.form.get(f"roll_{k_code}"))

        details.append({
            "product_code": product_code,
            "quantity": quantity,
            "need": need,
            "roll_selection": roll_selection,
            "status": "未着手"
        })

        return render_template(
            "order.html",
            products=products,
            input_user=input_user,
            customer_code=customer_code,
            delivery_date=delivery_date,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            details=details
        )

    # 受注確定ステップ
    if action == "submit_order":
        order_no = next_order_no()

        order_data = {
            "order_no": order_no,
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "input_user": input_user,
            "customer_code": customer_code,
            "delivery_date": delivery_date,
            "shipping_address": shipping_address,
            "shipping_method": shipping_method,
            "details": details
        }

        orders.append(order_data)

        return f"受注 {order_no} を登録しました（明細数：{len(details)}）"

    return "不明な操作です"


# -------------------------
# Render起動
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
