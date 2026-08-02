from flask import Flask, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# -------------------------
# 商品レシピ（★10個あたりの必要量）
# -------------------------
products = {
    "Y001": {"K001": 30, "K002": 20},
    "Y002": {"K001": 10, "K002": 40, "K003": 10},
    "Y003": {"K002": 20, "K003": 30, "K004": 10},
    "Y004": {"K001": 50, "K004": 20, "K005": 10},
    "Y005": {"K001": 10, "K002": 10, "K003": 10, "K004": 10, "K005": 10},
    "Y006": {"K001": 60, "K002": 20},
    "Y007": {"K001": 25, "K002": 25, "K003": 25},
    "Y008": {"K001": 35, "K002": 15, "K004": 20},
    "Y009": {"K001": 45, "K002": 5, "K003": 10, "K004": 10, "K005": 10},
    "Y010": {"K001": 30, "K002": 30, "K003": 30}
}

# -------------------------
# お客様マスタ
# -------------------------
customers = {
    "A社": {
        "code": "C001",
        "destinations": {
            "北海道": "北海道札幌市中央区北1条西2丁目",
            "東京": "東京都千代田区丸の内1丁目",
            "大阪": "大阪府大阪市北区梅田1丁目"
        }
    },
    "B社": {
        "code": "C002",
        "destinations": {
            "名古屋": "愛知県名古屋市中村区名駅1丁目",
            "岡山": "岡山県岡山市北区駅前町1丁目"
        }
    },
    "C社": {
        "code": "C003",
        "destinations": {
            "福岡": "福岡県福岡市博多区博多駅前1丁目",
            "熊本": "熊本県熊本市中央区手取本町"
        }
    },
    "D社": {
        "code": "C004",
        "destinations": {
            "仙台": "宮城県仙台市青葉区中央1丁目",
            "横浜": "神奈川県横浜市西区みなとみらい2丁目"
        }
    },
    "E社": {
        "code": "C005",
        "destinations": {
            "広島": "広島県広島市中区紙屋町1丁目",
            "高松": "香川県高松市番町1丁目"
        }
    },
    "F社": {
        "code": "C006",
        "destinations": {
            "京都": "京都府京都市下京区四条通",
            "神戸": "兵庫県神戸市中央区三宮町1丁目"
        }
    }
}

# -------------------------
# 在庫データ
# -------------------------
stock_Y = {code: 0 for code in products.keys()}

stock_K = {
    "K001": [100, 80, 55],
    "K002": [100, 60],
    "K003": [100],
    "K004": [90, 30],
    "K005": [100]
}

stock_H = {"H001": 100, "H002": 100, "H003": 100}

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


# ============================================================
# erp-mini メニュー（新規追加）
# ============================================================

@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/orders")
def orders_menu():
    return render_template("orders.html")

@app.route("/shipments")
def shipments_menu():
    return render_template("shipments.html")

@app.route("/receipts")
def receipts_menu():
    return render_template("receipts.html")

@app.route("/stocks")
def stocks_menu():
    return render_template("stocks.html")

@app.route("/inventory")
def inventory_menu():
    return render_template("inventory.html")

@app.route("/sales_menu")
def sales_menu():
    return render_template("sales.html")

@app.route("/costs")
def costs_menu():
    return render_template("costs.html")

@app.route("/masters")
def masters_menu():
    return render_template(
        "masters.html",
        items=items,
        customers=customers,
        locations=locations,
        bom=bom,
        prices=prices
    )

@app.route("/reports")
def reports_menu():
    return render_template("reports.html")


# ============================================================
# 既存機能（A-1方式の受注・出荷・在庫・売上）
# ============================================================

# -------------------------
# 在庫画面（既存）
# -------------------------
@app.route("/stock")
def stock():
    return render_template("stock.html", stock_Y=stock_Y, stock_K=stock_K, stock_H=stock_H)

# -------------------------
# 出荷（既存）
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
# 売上（既存）
# -------------------------
@app.route("/sales")
def sales():
    return render_template("sales.html", sales_data=sales_data)

# -------------------------
# 受注（既存）
# -------------------------
@app.route("/order", methods=["GET", "POST"])
def order():
    # （既存の長い処理はそのまま）
    # ここは省略せずに全部残す
    # ※あなたの元コードをそのまま維持
    # （長いので省略しませんが、ここに全部入っています）
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    # ※ここはあなたの元コードをそのまま貼り付けてあります
    # （省略しません）
    # ---------------------------------------------------------
    if request.method == "GET":
        return render_template(
            "order.html",
            products=products,
            customers=customers,
            details=[],
            customer=None,
            destination=None,
            delivery_date=None,
            shipping_method=None
        )

    action = request.form.get("action")

    input_user = request.form.get("input_user")
    customer = request.form.get("customer")
    destination = request.form.get("destination")
    delivery_date = request.form.get("delivery_date")
    shipping_method = request.form.get("shipping_method")

    shipping_address = ""
    if customer and destination:
        shipping_address = customers[customer]["destinations"][destination]

    details_raw = request.form.get("details_data")
    details = json.loads(details_raw) if details_raw else []

    product_code = request.form.get("product_code")
    quantity_raw = request.form.get("quantity")

    if action == "show_material":
        quantity = int(quantity_raw)
        manufacture_qty = ((quantity + 9) // 10) * 10
        lot_count = manufacture_qty // 10
        recipe = products[product_code]

        need = {}
        for k_code, base_amount in recipe.items():
            need[k_code] = base_amount * lot_count

        return render_template(
            "order.html",
            products=products,
            customers=customers,
            input_user=input_user,
            customer=customer,
            destination=destination,
            delivery_date=delivery_date,
            shipping_method=shipping_method,
            shipping_address=shipping_address,
            product_code=product_code,
            quantity=quantity,
            manufacture_qty=manufacture_qty,
            need=need,
            stock_K=stock_K,
            details=details
        )

    if action == "add_detail":
        quantity = int(quantity_raw)
        manufacture_qty = ((quantity + 9) // 10) * 10
        lot_count = manufacture_qty // 10
        recipe = products[product_code]

        need = {}
        roll_selection = {}

        for k_code, base_amount in recipe.items():
            need[k_code] = base_amount * lot_count
            roll_selection[k_code] = int(request.form.get(f"roll_{k_code}"))

        details.append({
            "product_code": product_code,
            "quantity": quantity,
            "manufacture_qty": manufacture_qty,
            "need": need,
            "roll_selection": roll_selection,
            "status": "未着手"
        })

        return render_template(
            "order.html",
            products=products,
            customers=customers,
            input_user=input_user,
            customer=customer,
            destination=destination,
            delivery_date=delivery_date,
            shipping_method=shipping_method,
            shipping_address=shipping_address,
            details=details
        )

    if action == "submit_order":
        order_no = next_order_no()

        for d in details:
            for k_code, need_amount in d["need"].items():
                selected_roll = d["roll_selection"][k_code]
                rolls = stock_K[k_code]

                idx = rolls.index(selected_roll)
                rolls[idx] -= need_amount
                if rolls[idx] <= 0:
                    rolls.pop(idx)

            surplus = d["manufacture_qty"] - d["quantity"]
            stock_Y[d["product_code"]] += surplus

        order_data = {
            "order_no": order_no,
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "input_user": input_user,
            "customer": customer,
            "customer_code": customers[customer]["code"],
            "destination": destination,
            "shipping_address": shipping_address,
            "delivery_date": delivery_date,
            "shipping_method": shipping_method,
            "details": details
        }

        orders.append(order_data)

        return f"受注 {order_no} を登録しました（明細数：{len(details)}）"

    return "不明な操作です"


# -------------------------
# 受注一覧（既存）
# -------------------------
@app.route("/order_list")
def order_list():
    return render_template("order_list.html", orders=orders)


# -------------------------
# Render起動
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
