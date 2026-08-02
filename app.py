from flask import Flask, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# ============================================================
# ① 品目マスタ（FG / SFG / RM）
# ============================================================
items = {
    # --- 製品（FG） ---
    "Y001": {"name": "製品Y001", "unit": "個", "type": "FG"},
    "Y002": {"name": "製品Y002", "unit": "個", "type": "FG"},
    "Y003": {"name": "製品Y003", "unit": "個", "type": "FG"},
    "Y004": {"name": "製品Y004", "unit": "個", "type": "FG"},
    "Y005": {"name": "製品Y005", "unit": "個", "type": "FG"},

    # --- 織物（SFG） ---
    "K001": {"name": "織物K001", "unit": "m", "type": "SFG"},
    "K002": {"name": "織物K002", "unit": "m", "type": "SFG"},
    "K003": {"name": "織物K003", "unit": "m", "type": "SFG"},
    "K004": {"name": "織物K004", "unit": "m", "type": "SFG"},
    "K005": {"name": "織物K005", "unit": "m", "type": "SFG"},

    # --- 撚糸（SFG） ---
    "H101": {"name": "撚糸H101", "unit": "m", "type": "SFG"},
    "H102": {"name": "撚糸H102", "unit": "m", "type": "SFG"},
    "H103": {"name": "撚糸H103", "unit": "m", "type": "SFG"},
    "H104": {"name": "撚糸H104", "unit": "m", "type": "SFG"},
    "H105": {"name": "撚糸H105", "unit": "m", "type": "SFG"},

    # --- 原糸（RM） ---
    "H001": {"name": "原糸H001", "unit": "m", "type": "RM"},
    "H002": {"name": "原糸H002", "unit": "m", "type": "RM"},
    "H003": {"name": "原糸H003", "unit": "m", "type": "RM"},
    "H004": {"name": "原糸H004", "unit": "m", "type": "RM"},
    "H005": {"name": "原糸H005", "unit": "m", "type": "RM"}
}

# ============================================================
# ② BOMマスタ（多段階）
# ============================================================
bom = {
    # --- 製品 → 織物（10個あたり） ---
    "Y001": {"K001": 10, "K002": 10},
    "Y002": {"K001": 30, "K002": 10},
    "Y003": {"K001": 10, "K003": 40},
    "Y004": {"K004": 30},
    "Y005": {"K005": 45},

    # --- 織物 → 撚糸（100mあたり） ---
    "K001": {"H101": 1000},
    "K002": {"H102": 1000},
    "K003": {"H103": 1000},
    "K004": {"H104": 1000},
    "K005": {"H105": 1000},

    # --- 撚糸 → 原糸（1000mあたり） ---
    "H101": {"H001": 2000, "H002": 1000},
    "H102": {"H001": 2000, "H002": 1000},
    "H103": {"H001": 1000, "H002": 1000, "H003": 1000},
    "H104": {"H003": 1000, "H004": 1000, "H005": 1000},
    "H105": {"H004": 2000, "H005": 1000}
}

# ============================================================
# ③ 得意先マスタ
# ============================================================
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

# ============================================================
# ④ 棚番マスタ（LH / LK / LY 全登録）
# ============================================================
locations = {
    # ============================
    # LH（原糸・撚糸系）
    # ============================

    "LH001": {"desc": "原糸置き場 001"},
    "LH002": {"desc": "原糸→撚糸設置１ 002"},
    "LH003": {"desc": "原糸→撚糸設置２ 003"},
    "LH004": {"desc": "撚糸置き場 004"},
    "LH005": {"desc": "撚糸→織物設置１ 005"},
    "LH006": {"desc": "撚糸→織物設置２ 006"},

    # LH501〜LH599（立体倉庫）
    **{f"LH{str(i).zfill(3)}": {"desc": f"立体倉庫 {str(i).zfill(3)}"} for i in range(501, 600)},


    # ============================
    # LK（織物系）
    # ============================

    "LK001": {"desc": "K1工場"},
    "LK002": {"desc": "K2工場"},

    # LK501〜LK599（K倉庫）
    **{f"LK{str(i).zfill(3)}": {"desc": f"K倉庫 {str(i).zfill(3)}"} for i in range(501, 600)},


    # ============================
    # LY（製品系）
    # ============================

    "LY001": {"desc": "湿式"},
    "LY002": {"desc": "乾式"},
    "LY003": {"desc": "乾式スリッター"},
    "LY004": {"desc": "乾式CP"},
    "LY005": {"desc": "乾式ベルト"},
    "LY006": {"desc": "乾式特殊"},
    "LY007": {"desc": "Y倉庫一次置き場"},
    "LY008": {"desc": "Y倉庫簡易加工場"},
    "LY009": {"desc": "Y倉庫搬入品置き場"},
    "LY010": {"desc": "Y倉庫出荷品置き場"},

    # LY501〜LY599（Y倉庫）
    **{f"LY{str(i).zfill(3)}": {"desc": f"Y倉庫 {str(i).zfill(3)}"} for i in range(501, 600)}
}


# ============================================================
# ⑤ 単価マスタ
# ============================================================
prices = {
    "H001": {"cost": 100, "price": 0},
    "H002": {"cost": 120, "price": 0},
    "H003": {"cost": 150, "price": 0},
    "H004": {"cost": 180, "price": 0},
    "H005": {"cost": 200, "price": 0},

    "H101": {"cost": 0, "price": 0},
    "H102": {"cost": 0, "price": 0},
    "H103": {"cost": 0, "price": 0},
    "H104": {"cost": 0, "price": 0},
    "H105": {"cost": 0, "price": 0},

    "K001": {"cost": 0, "price": 0},
    "K002": {"cost": 0, "price": 0},
    "K003": {"cost": 0, "price": 0},
    "K004": {"cost": 0, "price": 0},
    "K005": {"cost": 0, "price": 0},

    "Y001": {"cost": 0, "price": 3000},
    "Y002": {"cost": 0, "price": 3500},
    "Y003": {"cost": 0, "price": 3200},
    "Y004": {"cost": 0, "price": 3800},
    "Y005": {"cost": 0, "price": 4000}
}

# ============================================================
# 在庫データ（既存）
# ============================================================
stock_Y = {code: 0 for code in items if items[code]["type"] == "FG"}

stock_K = {
    "K001": [100, 80, 55],
    "K002": [100, 60],
    "K003": [100],
    "K004": [90, 30],
    "K005": [100]
}

stock_H = {"H001": 100, "H002": 100, "H003": 100}

sales_data = []

orders = []
order_counter = 1

def next_order_no():
    global order_counter
    order_no = f"T{order_counter:05d}"
    order_counter += 1
    return order_no


# ============================================================
# メニュー
# ============================================================
@app.route("/")
def menu():
    return render_template("menu.html")


# ============================================================
# マスタ管理（今回修正した部分）
# ============================================================
@app.route("/masters")
def masters_menu():
    return render_template(
        "masters.html",
        items=items,
        bom=bom,
        customers=customers,
        locations=locations,
        prices=prices
    )


# ============================================================
# 既存の画面（stock / shipment / sales / order）
# ============================================================
@app.route("/stock")
def stock():
    return render_template("stock.html", stock_Y=stock_Y, stock_K=stock_K, stock_H=stock_H)


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


# ============================================================
# 受注（既存ロジックそのまま）
# ============================================================
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "GET":
        return render_template(
            "order.html",
            products=bom,
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

    # --- 原材料表示 ---
    if action == "show_material":
        quantity = int(quantity_raw)

        manufacture_qty = ((quantity + 9) // 10) * 10
        lot_count = manufacture_qty // 10

        recipe = bom.get(product_code, {})

        need = {}
        for k_code, base_amount in recipe.items():
            need[k_code] = base_amount * lot_count

        return render_template(
            "order.html",
            products=bom,
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

    # --- 明細追加 ---
    if action == "add_detail":
        quantity = int(quantity_raw)

        manufacture_qty = ((quantity + 9) // 10) * 10
        lot_count = manufacture_qty // 10

        recipe = bom.get(product_code, {})

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
            products=bom,
            customers=customers,
            input_user=input_user,
            customer=customer,
            destination=destination,
            delivery_date=delivery_date,
            shipping_method=shipping_method,
            shipping_address=shipping_address,
            details=details
        )

    # --- 受注確定 ---
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


@app.route("/order_list")
def order_list():
    return render_template("order_list.html", orders=orders)


# ============================================================
# Render起動
# ============================================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
