from flask import Flask, render_template, request, redirect
import json
from datetime import datetime

app = Flask(__name__)

# ============================================================
# ① 品目マスタ（FG / SFG / RM）
# ============================================================
items = {
    "Y001": {"name": "製品Y001", "unit": "個", "type": "FG"},
    "Y002": {"name": "製品Y002", "unit": "個", "type": "FG"},
    "Y003": {"name": "製品Y003", "unit": "個", "type": "FG"},
    "Y004": {"name": "製品Y004", "unit": "個", "type": "FG"},
    "Y005": {"name": "製品Y005", "unit": "個", "type": "FG"},

    "K001": {"name": "織物K001", "unit": "m", "type": "SFG"},
    "K002": {"name": "織物K002", "unit": "m", "type": "SFG"},
    "K003": {"name": "織物K003", "unit": "m", "type": "SFG"},
    "K004": {"name": "織物K004", "unit": "m", "type": "SFG"},
    "K005": {"name": "織物K005", "unit": "m", "type": "SFG"},

    "H101": {"name": "撚糸H101", "unit": "m", "type": "SFG"},
    "H102": {"name": "撚糸H102", "unit": "m", "type": "SFG"},
    "H103": {"name": "撚糸H103", "unit": "m", "type": "SFG"},
    "H104": {"name": "撚糸H104", "unit": "m", "type": "SFG"},
    "H105": {"name": "撚糸H105", "unit": "m", "type": "SFG"},

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
    "Y001": {"K001": 10, "K002": 10},
    "Y002": {"K001": 30, "K002": 10},
    "Y003": {"K001": 10, "K003": 40},
    "Y004": {"K004": 30},
    "Y005": {"K005": 45},

    "K001": {"H101": 1000},
    "K002": {"H102": 1000},
    "K003": {"H103": 1000},
    "K004": {"H104": 1000},
    "K005": {"H105": 1000},

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
    }
}

# ============================================================
# ④ 棚番マスタ（LH / LK / LY）
# ============================================================
locations = {
    "LH001": {"desc": "原糸置き場 001"},
    "LH002": {"desc": "原糸→撚糸設置１ 002"},
    "LH003": {"desc": "原糸→撚糸設置２ 003"},
    "LH004": {"desc": "撚糸置き場 004"},
    "LH005": {"desc": "撚糸→織物設置１ 005"},
    "LH006": {"desc": "撚糸→織物設置２ 006"},
    "LH009": {"desc": "H搬入品置き場"},
    "LH010": {"desc": "H出荷品置き場"},
    **{f"LH{str(i).zfill(3)}": {"desc": f"立体倉庫 {str(i).zfill(3)}"} for i in range(501, 600)},

    "LK001": {"desc": "K1工場"},
    "LK002": {"desc": "K2工場"},
    "LK009": {"desc": "K搬入品置き場"},
    "LK010": {"desc": "K出荷品置き場"},
    **{f"LK{str(i).zfill(3)}": {"desc": f"K倉庫 {str(i).zfill(3)}"} for i in range(501, 600)},

    "LY001": {"desc": "湿式"},
    "LY002": {"desc": "乾式"},
    "LY003": {"desc": "乾式スリッター"},
    "LY004": {"desc": "乾式CP"},
    "LY005": {"desc": "乾式ベルト"},
    "LY006": {"desc": "乾式特殊"},
    "LY007": {"desc": "Y倉庫一次置き場"},
    "LY008": {"desc": "Y倉庫簡易加工場"},
    "LY009": {"desc": "Y搬入品置き場"},
    "LY010": {"desc": "Y出荷品置き場"},
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
# ⑥ 在庫構造（棚番 × ロット × 数量 × 受注番号）
# ============================================================
stock_H = {code: {} for code in items if items[code]["type"] == "RM"}
stock_K = {code: {} for code in items if items[code]["type"] == "SFG"}
stock_Y = {code: {} for code in items if items[code]["type"] == "FG"}

sales_data = []
orders = []
order_counter = 1

# ★ここだけ新方式に置き換える（lot_counter は1回だけ）
lot_counter = {}  # { item_code: { date: seq } }

def next_order_no():
    global order_counter
    order_no = f"T{order_counter:05d}"
    order_counter += 1
    return order_no

def next_lot_no(item_code):
    today = datetime.now().strftime("%Y%m%d")

    if item_code not in lot_counter:
        lot_counter[item_code] = {}

    if today not in lot_counter[item_code]:
        lot_counter[item_code][today] = 1

    seq = lot_counter[item_code][today]
    lot_counter[item_code][today] += 1

    return f"LOT-{item_code}-{today}-{seq:03d}"

# ============================================================
# メニュー
# ============================================================
@app.route("/")
def menu():
    return render_template("menu.html")

# ============================================================
# マスタ管理
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
# 入庫管理（棚番選択＋ロット自動採番）
# ============================================================
@app.route("/receipts", methods=["GET", "POST"])
def receipts():
    if request.method == "GET":
        return render_template(
            "receipts.html",
            purchases=purchases,
            suppliers=suppliers,
            items=items,
            locations=locations
        )

    po_no = request.form.get("po_no")
    location_code = request.form.get("location_code")
    qty = int(request.form.get("qty"))

    # 発注情報を取得
    po = next(p for p in purchases if p["po_no"] == po_no)
    item_code = po["item_code"]

    # ロット番号採番
    lot_no = next_lot_no(item_code)

    # 品目タイプで H/K/Y を振り分け
    item_type = items[item_code]["type"]
    if item_type == "RM":
        stock = stock_H
    elif item_type == "SFG":
        stock = stock_K
    else:
        stock = stock_Y

    # 棚番にロット配列が無ければ作る
    if location_code not in stock[item_code]:
        stock[item_code][location_code] = []

    # ロット追加
    stock[item_code][location_code].append({
        "lot": lot_no,
        "qty": qty,
        "order_no": po.get("order_no")
    })

    # 発注残を減らす
    po["qty"] -= qty

    return f"{item_code} を {location_code} に {qty} 入庫しました（ロット: {lot_no}）"

# ============================================================
# 在庫一覧（棚番 × ロット × 数量 × 受注番号）
# ============================================================
@app.route("/stocks")
def stocks():
    return render_template(
        "stocks.html",
        stock_H=stock_H,
        stock_K=stock_K,
        stock_Y=stock_Y,
        locations=locations,
        items=items
    )
# ============================================================
# 出荷管理（棚番からピッキング）
# ============================================================
@app.route("/shipping", methods=["GET", "POST"])
def shipping():
    merged_stock = {**stock_H, **stock_K, **stock_Y}

    if request.method == "GET":
        return render_template(
            "shipping.html",
            items=items,
            stock=merged_stock,
            locations=locations,
            selected_item=None,
            selected_location=None
        )

    action = request.form.get("action")
    item_code = request.form.get("item_code")
    location_code = request.form.get("location_code")

    if not action:
        return render_template(
            "shipping.html",
            items=items,
            stock=merged_stock,
            locations=locations,
            selected_item=item_code,
            selected_location=location_code
        )

    lot_no = request.form.get("lot_no")
    qty = int(request.form.get("qty"))

    item_type = items[item_code]["type"]
    if item_type == "RM":
        stock = stock_H
    elif item_type == "SFG":
        stock = stock_K
    else:
        stock = stock_Y

    lots = stock[item_code][location_code]

    for lot in lots:
        if lot["lot"] == lot_no:
            if lot["qty"] < qty:
                return f"出荷数量がロット在庫を超えています（在庫: {lot['qty']}）"

            lot["qty"] -= qty

            if lot["qty"] == 0:
                lots.remove(lot)

            sales_data.append({
                "item_code": item_code,
                "lot": lot_no,
                "qty": qty,
                "location": location_code,
                "order_no": lot["order_no"],
                "date": datetime.now().strftime("%Y-%m-%d")
            })

            return f"{item_code} / ロット {lot_no} を {location_code} から {qty} 出荷しました"

    return "ロットが見つかりません"

# ============================================================
# 製造実績（棚番に入庫）
# ============================================================
@app.route("/production", methods=["GET", "POST"])
def production():
    if request.method == "GET":
        return render_template(
            "production.html",
            orders=orders,
            items=items,
            locations=locations
        )

    order_no = request.form.get("order_no")
    item_code = request.form.get("item_code")
    qty = int(request.form.get("qty"))
    location_code = request.form.get("location_code")

    lot_no = next_lot_no(item_code)

    item_type = items[item_code]["type"]
    if item_type == "RM":
        stock = stock_H
    elif item_type == "SFG":
        stock = stock_K
    else:
        stock = stock_Y

    if location_code not in stock[item_code]:
        stock[item_code][location_code] = []

    stock[item_code][location_code].append({
        "lot": lot_no,
        "qty": qty,
        "order_no": order_no
    })

    return f"製造実績を登録しました：{item_code} / {qty} / ロット {lot_no} / 棚番 {location_code} / 受注 {order_no}"

# ============================================================
# 製造実績一覧（NEW）
# ============================================================
@app.route("/production_list")
def production_list():
    production_records = []

    # H系
    for item_code, shelves in stock_H.items():
        for loc, lots in shelves.items():
            for lot in lots:
                production_records.append({
                    "item_code": item_code,
                    "item_name": items[item_code]["name"],
                    "location": loc,
                    "lot": lot["lot"],
                    "qty": lot["qty"],
                    "order_no": lot["order_no"]
                })

    # K系
    for item_code, shelves in stock_K.items():
        for loc, lots in shelves.items():
            for lot in lots:
                production_records.append({
                    "item_code": item_code,
                    "item_name": items[item_code]["name"],
                    "location": loc,
                    "lot": lot["lot"],
                    "qty": lot["qty"],
                    "order_no": lot["order_no"]
                })

    # Y系
    for item_code, shelves in stock_Y.items():
        for loc, lots in shelves.items():
            for lot in lots:
                production_records.append({
                    "item_code": item_code,
                    "item_name": items[item_code]["name"],
                    "location": loc,
                    "lot": lot["lot"],
                    "qty": lot["qty"],
                    "order_no": lot["order_no"]
                })

    return render_template("production_list.html", production_records=production_records)

# ============================================================
# 受注登録（NEW）
# ============================================================
@app.route("/orders", methods=["GET", "POST"])
def orders_menu():
    if request.method == "GET":
        return render_template(
            "orders.html",
            customers=customers,
            items=items,
            selected_customer=list(customers.keys())[0]
        )

    customer = request.form.get("customer")
    destination = request.form.get("destination")
    item_code = request.form.get("item_code")
    qty = int(request.form.get("qty"))
    due = request.form.get("due")

    order_no = next_order_no()

    orders.append({
        "order_no": order_no,
        "customer": customer,
        "destination": destination,
        "item_code": item_code,
        "qty": qty,
        "due": due
    })

    return redirect("/")

# ============================================================
# 受注一覧（NEW）
# ============================================================
@app.route("/orders_list")
def orders_list():
    return render_template(
        "orders_list.html",
        orders=orders,
        items=items
    )

# ============================================================
# 購買対象品目（NEW）
# ============================================================
purchase_items = ["H001", "H002", "H003", "H004", "H005",
                  "A4", "A3", "RING1", "RING2"]

# ============================================================
# 仕入先マスタ（NEW）
# ============================================================
suppliers = {
    "SUP001": {"name": "A商事", "items": ["H001", "H002", "H003"]},
    "SUP002": {"name": "B物産", "items": ["H004", "H005"]},
    "SUP003": {"name": "C紙業", "items": ["A4", "A3"]},
    "SUP004": {"name": "Dリング工業", "items": ["RING1", "RING2"]},
}

# ============================================================
# 発注登録（NEW）
# ============================================================
purchases = []

def next_po_no():
    return f"P{len(purchases)+1:05d}"

@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    if request.method == "GET":
        return render_template(
            "purchase.html",
            suppliers=suppliers,
            items=items,
            purchase_items=purchase_items
        )

    supplier = request.form.get("supplier")
    item_code = request.form.get("item_code")
    qty = int(request.form.get("qty"))
    due = request.form.get("due")

    po_no = next_po_no()

    purchases.append({
        "po_no": po_no,
        "supplier": supplier,
        "item_code": item_code,
        "qty": qty,
        "due": due
    })

    return redirect("/")

# ============================================================
# 棚卸（棚番別棚卸入力）
# ============================================================
@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    merged_stock = {**stock_H, **stock_K, **stock_Y}

    if request.method == "GET":
        return render_template(
            "inventory.html",
            locations=locations,
            items=items,
            stock=merged_stock,
            selected_location=None,
            selected_item=None
        )

    action = request.form.get("action")
    location_code = request.form.get("location_code")
    item_code = request.form.get("item_code")

    # 画面再表示（棚番・品目選択時）
    if not action:
        return render_template(
            "inventory.html",
            locations=locations,
            items=items,
            stock=merged_stock,
            selected_location=location_code,
            selected_item=item_code
        )

    # 棚卸登録処理
    lot_no = request.form.get("lot_no")
    actual_qty = int(request.form.get("actual_qty"))

    item_type = items[item_code]["type"]
    if item_type == "RM":
        stock = stock_H
    elif item_type == "SFG":
        stock = stock_K
    else:
        stock = stock_Y

    lots = stock[item_code][location_code]

    for lot in lots:
        if lot["lot"] == lot_no:

            before_qty = lot["qty"]
            diff_qty = actual_qty - before_qty

            inventory_diff.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "item_code": item_code,
                "item_name": items[item_code]["name"],
                "location": location_code,
                "lot": lot_no,
                "before": before_qty,
                "after": actual_qty,
                "diff": diff_qty
            })

            lot["qty"] = actual_qty
            return f"棚卸完了：{item_code} / ロット {lot_no} / 棚番 {location_code} を {actual_qty} に更新しました"

    return "ロットが見つかりません"

# ============================================================
# Render起動
# ============================================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
