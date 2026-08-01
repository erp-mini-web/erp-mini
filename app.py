@app.route("/order", methods=["GET", "POST"])
def order():

    # GET → 初期表示
    if request.method == "GET":
        return render_template("order.html", products=products)

    selected_product = request.form.get("product")

    # 商品未選択 → 初期画面
    if not selected_product:
        return render_template("order.html", products=products)

    # ロール選択が POST に含まれているかどうかで判定
    has_roll_selection = any(
        f"roll_{k_code}" in request.form for k_code in stock_K.keys()
    )

    # ロール選択が無い → 商品コードを選んだだけ（ロール表示ステップ）
    if not has_roll_selection:
        recipe = products[selected_product]
        return render_template(
            "order.html",
            products=products,
            selected_product=selected_product,
            recipe=recipe,
            stock_K=stock_K
        )

    # ここから製造ステップ（ロール選択あり）
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
