from flask import Flask, render_template, request

app = Flask(__name__)

# -------------------------
# 在庫データ（まずはメモリで持つ）
# -------------------------

# 完成品 Y
stock_Y = {
    "Y001": 0,
    "Y002": 5,
    "Y003": 10,
    # 必要なら Y030 まで追加
}

# 中間材 K
stock_K = {
    "K001": 3,
    "K002": 0
}

# 原材料 H
stock_H = {
    "H001": 10,
    "H002": 0,
    "H003": 5
}

# -------------------------
# メニュー画面
# -------------------------
@app.route("/")
def menu():
    return render_template("menu.html")

# -------------------------
# 在庫画面
# -------------------------
@app.route("/stock")
def stock():
    return render_template(
        "stock.html",
        stock_Y=stock_Y,
        stock_K=stock_K,
        stock_H=stock_H
    )

# -------------------------
# 購入画面
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
# 出荷画面（まだロジックなし）
# -------------------------
@app.route("/shipment")
def shipment():
    return render_template("shipment.html")

# -------------------------
# 売上画面（まだロジックなし）
# -------------------------
@app.route("/sales")
def sales():
    return render_template("sales.html")

# -------------------------
# 受注画面
# -------------------------
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        product = request.form.get("product")
        quantity = int(request.form.get("quantity"))

        # ① 完成品Yの在庫確認
        if stock_Y.get(product, 0) >= quantity:
            stock_Y[product] -= quantity
            return f"{product} を {quantity} 個出荷できます（Y在庫から）"

        # ② 中間材Kの在庫確認（仮に1:1で必要とする）
        need_K1 = quantity
        need_K2 = quantity

        if stock_K["K001"] >= need_K1 and stock_K["K002"] >= need_K2:
            stock_K["K001"] -= need_K1
            stock_K["K002"] -= need_K2
            return f"{product} を {quantity} 個製造できます（K在庫から）"

        # ③ 原材料Hの在庫確認（仮に1:1で必要とする）
        need_H1 = quantity
        need_H2 = quantity
        need_H3 = quantity

        lack = []
        if stock_H["H001"] < need_H1:
            lack.append("H001")
        if stock_H["H002"] < need_H2:
            lack.append("H002")
        if stock_H["H003"] < need_H3:
            lack.append("H003")

        # 足りない原材料がある場合 → 購入が必要
        if lack:
            return f"{product} を作るために {', '.join(lack)} を購入する必要があります"

        # 原材料がある場合 → 消費して製造
        stock_H["H001"] -= need_H1
        stock_H["H002"] -= need_H2
        stock_H["H003"] -= need_H3

        return f"{product} を {quantity} 個製造できます（H在庫から）"

    return render_template("order.html")

# -------------------------
# Render用の起動設定
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
