from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///erp_mini.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ==========
# モデル定義
# ==========

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)

class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    location_code = db.Column(db.String(50), unique=True, nullable=False)
    location_name = db.Column(db.String(100), nullable=False)

class Inventory(db.Model):
    """
    棚番 × 品目 × ロット別在庫
    """
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), nullable=False)
    location_code = db.Column(db.String(50), nullable=False)
    lot_no = db.Column(db.String(100), nullable=False)
    manufactured_date = db.Column(db.String(8), nullable=False)  # YYYYMMDD
    use_by_date = db.Column(db.String(8), nullable=False)        # YYYYMMDD
    qty = db.Column(db.Integer, nullable=False, default=0)

class StockTransaction(db.Model):
    """
    在庫トランザクション（入庫・出荷・棚卸）
    """
    __tablename__ = "stock_transactions"
    id = db.Column(db.Integer, primary_key=True)
    tran_type = db.Column(db.String(10), nullable=False)  # IN / OUT / ADJ
    item_code = db.Column(db.String(50), nullable=False)
    location_code = db.Column(db.String(50), nullable=False)
    lot_no = db.Column(db.String(100), nullable=False)
    manufactured_date = db.Column(db.String(8), nullable=False)
    use_by_date = db.Column(db.String(8), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========
# 初期化
# ==========

@app.before_first_request
def init_db():
    db.create_all()
    # サンプルマスタ
    if not Item.query.first():
        db.session.add_all([
            Item(item_code="H001", item_name="黒生地"),
            Item(item_code="H002", item_name="白生地"),
        ])
    if not Location.query.first():
        db.session.add_all([
            Location(location_code="A-01", location_name="棚A-01"),
            Location(location_code="B-01", location_name="棚B-01"),
        ])
    db.session.commit()


# ==========
# ロット番号自動採番
# ==========

def generate_lot_no(item_code: str, manufactured_date_yyyymmdd: str) -> str:
    """
    LOT-{item_code}-{YYYYMMDD}-{seq:03d}
    """
    existing = (
        Inventory.query
        .filter_by(item_code=item_code, manufactured_date=manufactured_date_yyyymmdd)
        .all()
    )
    seq = len(existing) + 1
    lot_no = f"LOT-{item_code}-{manufactured_date_yyyymmdd}-{seq:03d}"
    return lot_no


# ==========
# テンプレート（簡易）
# ==========

layout = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>ERP-mini ロット管理入り</title>
  <style>
    body {{ font-family: sans-serif; margin: 20px; }}
    nav a {{ margin-right: 10px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 8px; font-size: 12px; }}
    th {{ background: #eee; }}
    .danger {{ background: #ffe0e0; }}
    .warn {{ background: #fff4cc; }}
  </style>
</head>
<body>
<nav>
  <a href="{{ url_for('index') }}">在庫一覧</a>
  <a href="{{ url_for('inbound') }}">入庫</a>
  <a href="{{ url_for('outbound') }}">出荷</a>
  <a href="{{ url_for('stocktake') }}">棚卸</a>
  <a href="{{ url_for('lot_view') }}">ロット別在庫</a>
</nav>
<hr>
{% block content %}{% endblock %}
</body>
</html>
"""

# ==========
# 画面
# ==========

@app.route("/")
def index():
    inventories = Inventory.query.order_by(
        Inventory.item_code, Inventory.location_code, Inventory.lot_no
    ).all()
    today = datetime.today().strftime("%Y%m%d")
    return render_template_string(
        layout + """
{% block content %}
<h2>在庫一覧（棚番 × 品目 × ロット）</h2>
<table>
  <tr>
    <th>品目コード</th>
    <th>棚番</th>
    <th>ロット番号</th>
    <th>製造日</th>
    <th>使用期限</th>
    <th>数量</th>
  </tr>
  {% for inv in inventories %}
    {% set cls = "" %}
    {% if inv.use_by_date < today %}
      {% set cls = "danger" %}
    {% elif inv.use_by_date <= (today[:4] + today[4:6] + "{:02d}".format(int(today[6:]) + 30 if int(today[6:]) < 70 else int(today[6:]))) %}
      {% set cls = "warn" %}
    {% endif %}
    <tr class="{{ cls }}">
      <td>{{ inv.item_code }}</td>
      <td>{{ inv.location_code }}</td>
      <td>{{ inv.lot_no }}</td>
      <td>{{ inv.manufactured_date }}</td>
      <td>{{ inv.use_by_date }}</td>
      <td style="text-align:right">{{ inv.qty }}</td>
    </tr>
  {% endfor %}
</table>
{% endblock %}
""",
        inventories=inventories,
        today=today,
    )


@app.route("/inbound", methods=["GET", "POST"])
def inbound():
    items = Item.query.all()
    locations = Location.query.all()

    if request.method == "POST":
        item_code = request.form.get("item_code")
        location_code = request.form.get("location_code")
        qty = int(request.form.get("qty") or 0)
        manufactured_date = request.form.get("manufactured_date")  # YYYY-MM-DD
        use_by_date = request.form.get("use_by_date")              # YYYY-MM-DD

        if qty <= 0:
            return redirect(url_for("inbound"))

        mfg_yyyymmdd = datetime.strptime(manufactured_date, "%Y-%m-%d").strftime("%Y%m%d")
        use_yyyymmdd = datetime.strptime(use_by_date, "%Y-%m-%d").strftime("%Y%m%d")

        lot_no = generate_lot_no(item_code, mfg_yyyymmdd)

        inv = Inventory.query.filter_by(
            item_code=item_code,
            location_code=location_code,
            lot_no=lot_no,
        ).first()
        if not inv:
            inv = Inventory(
                item_code=item_code,
                location_code=location_code,
                lot_no=lot_no,
                manufactured_date=mfg_yyyymmdd,
                use_by_date=use_yyyymmdd,
                qty=0,
            )
            db.session.add(inv)

        inv.qty += qty

        tran = StockTransaction(
            tran_type="IN",
            item_code=item_code,
            location_code=location_code,
            lot_no=lot_no,
            manufactured_date=mfg_yyyymmdd,
            use_by_date=use_yyyymmdd,
            qty=qty,
        )
        db.session.add(tran)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template_string(
        layout + """
{% block content %}
<h2>入庫（ロット自動採番）</h2>
<form method="post">
  <label>品目コード：</label>
  <select name="item_code">
    {% for i in items %}
      <option value="{{ i.item_code }}">{{ i.item_code }} - {{ i.item_name }}</option>
    {% endfor %}
  </select><br><br>

  <label>棚番：</label>
  <select name="location_code">
    {% for l in locations %}
      <option value="{{ l.location_code }}">{{ l.location_code }} - {{ l.location_name }}</option>
    {% endfor %}
  </select><br><br>

  <label>数量：</label>
  <input type="number" name="qty" min="1" value="1"><br><br>

  <label>製造日：</label>
  <input type="date" name="manufactured_date" required><br><br>

  <label>使用期限：</label>
  <input type="date" name="use_by_date" required><br><br>

  <button type="submit">入庫登録（ロット番号自動生成）</button>
</form>
{% endblock %}
""",
        items=items,
        locations=locations,
    )


@app.route("/outbound", methods=["GET", "POST"])
def outbound():
    inventories = Inventory.query.order_by(
        Inventory.item_code, Inventory.location_code, Inventory.lot_no
    ).all()

    if request.method == "POST":
        inv_id = int(request.form.get("inv_id"))
        qty = int(request.form.get("qty") or 0)

        inv = Inventory.query.get(inv_id)
        if not inv or qty <= 0:
            return redirect(url_for("outbound"))

        if qty > inv.qty:
            qty = inv.qty  # 在庫以上は出荷させない

        inv.qty -= qty

        tran = StockTransaction(
            tran_type="OUT",
            item_code=inv.item_code,
            location_code=inv.location_code,
            lot_no=inv.lot_no,
            manufactured_date=inv.manufactured_date,
            use_by_date=inv.use_by_date,
            qty=qty,
        )
        db.session.add(tran)

        if inv.qty == 0:
            db.session.delete(inv)

        db.session.commit()
        return redirect(url_for("index"))

    return render_template_string(
        layout + """
{% block content %}
<h2>出荷（ロット単位）</h2>
<form method="post">
  <table>
    <tr>
      <th>選択</th>
      <th>品目コード</th>
      <th>棚番</th>
      <th>ロット番号</th>
      <th>製造日</th>
      <th>使用期限</th>
      <th>在庫数量</th>
      <th>出荷数量</th>
    </tr>
    {% for inv in inventories %}
    <tr>
      <td><input type="radio" name="inv_id" value="{{ inv.id }}"></td>
      <td>{{ inv.item_code }}</td>
      <td>{{ inv.location_code }}</td>
      <td>{{ inv.lot_no }}</td>
      <td>{{ inv.manufactured_date }}</td>
      <td>{{ inv.use_by_date }}</td>
      <td style="text-align:right">{{ inv.qty }}</td>
      <td><input type="number" name="qty" min="1" max="{{ inv.qty }}"></td>
    </tr>
    {% endfor %}
  </table>
  <br>
  <button type="submit">出荷登録</button>
</form>
{% endblock %}
""",
        inventories=inventories,
    )


@app.route("/stocktake", methods=["GET", "POST"])
def stocktake():
    inventories = Inventory.query.order_by(
        Inventory.item_code, Inventory.location_code, Inventory.lot_no
    ).all()

    if request.method == "POST":
        for inv in inventories:
            field_name = f"qty_{inv.id}"
            new_qty_str = request.form.get(field_name)
            if new_qty_str is None:
                continue
            try:
                new_qty = int(new_qty_str)
            except ValueError:
                continue

            diff = new_qty - inv.qty
            if diff == 0:
                continue

            inv.qty = new_qty

            tran = StockTransaction(
                tran_type="ADJ",
                item_code=inv.item_code,
                location_code=inv.location_code,
                lot_no=inv.lot_no,
                manufactured_date=inv.manufactured_date,
                use_by_date=inv.use_by_date,
                qty=diff,
            )
            db.session.add(tran)

            if inv.qty == 0:
                db.session.delete(inv)

        db.session.commit()
        return redirect(url_for("index"))

    return render_template_string(
        layout + """
{% block content %}
<h2>棚卸（ロット別数量調整）</h2>
<form method="post">
  <table>
    <tr>
      <th>品目コード</th>
      <th>棚番</th>
      <th>ロット番号</th>
      <th>製造日</th>
      <th>使用期限</th>
      <th>現在数量</th>
      <th>棚卸数量</th>
    </tr>
    {% for inv in inventories %}
    <tr>
      <td>{{ inv.item_code }}</td>
      <td>{{ inv.location_code }}</td>
      <td>{{ inv.lot_no }}</td>
      <td>{{ inv.manufactured_date }}</td>
      <td>{{ inv.use_by_date }}</td>
      <td style="text-align:right">{{ inv.qty }}</td>
      <td><input type="number" name="qty_{{ inv.id }}" min="0" value="{{ inv.qty }}"></td>
    </tr>
    {% endfor %}
  </table>
  <br>
  <button type="submit">棚卸確定</button>
</form>
{% endblock %}
""",
        inventories=inventories,
    )


@app.route("/lots")
def lot_view():
    """
    ロット別在庫照会
    """
    inventories = Inventory.query.order_by(
        Inventory.item_code, Inventory.lot_no, Inventory.location_code
    ).all()
    today = datetime.today().strftime("%Y%m%d")
    return render_template_string(
        layout + """
{% block content %}
<h2>ロット別在庫照会</h2>
<table>
  <tr>
    <th>品目コード</th>
    <th>ロット番号</th>
    <th>製造日</th>
    <th>使用期限</th>
    <th>棚番</th>
    <th>数量</th>
  </tr>
  {% for inv in inventories %}
    {% set cls = "" %}
    {% if inv.use_by_date < today %}
      {% set cls = "danger" %}
    {% elif inv.use_by_date <= today %}
      {% set cls = "warn" %}
    {% endif %}
    <tr class="{{ cls }}">
      <td>{{ inv.item_code }}</td>
      <td>{{ inv.lot_no }}</td>
      <td>{{ inv.manufactured_date }}</td>
      <td>{{ inv.use_by_date }}</td>
      <td>{{ inv.location_code }}</td>
      <td style="text-align:right">{{ inv.qty }}</td>
    </tr>
  {% endfor %}
</table>
<p>※赤：使用期限超過、黄：期限接近（簡易判定）</p>
{% endblock %}
""",
        inventories=inventories,
        today=today,
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
