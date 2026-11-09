from flask import Blueprint, jsonify, request
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Product, Order, OrderItem
from ..errors import NotFound, OutOfStock, Unprocessable
from ..schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def _order_query():
    return select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.product))



@orders_bp.get("")
def list_orders():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("size", 20))))
    rows = db.session.execute(
        _order_query().order_by(Order.id)
        .offset((page - 1) * size).limit(size)
    ).scalars().all()
    total = db.session.scalar(select(db.func.count()).select_from(Order))
    return jsonify({
        "items": [OrderOut().dump(o) for o in rows],
        "page": page, "size": size, "total": total,
    }), 200



@orders_bp.get("/<int:id>")
def get_order(id):
    order = db.session.execute(
        _order_query().where(Order.id == id)).scalar_one_or_none()
    if order is None:
        raise NotFound(message=f"order {id} not found")
    return OrderOut().dump(order), 200



@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.json)
    items = body["items"]

    ids = [i["product_id"] for i in items]
    if len(set(ids)) != len(ids):
        raise Unprocessable(message="duplicate product_id in items")

    products = {
        p.id: p for p in db.session.execute(
            select(Product).where(Product.id.in_(ids),
                                  Product.archived.is_(False))
        ).scalars()
    }
    missing = sorted(set(ids) - set(products))
    if missing:
        raise Unprocessable(message=f"products not found: {missing}")

    order = Order(customer_name=body["customer_name"])
    db.session.add(order)
    db.session.flush()
    order_id = order.id

    for it in items:
        pid, qty = it["product_id"], it["qty"]
        res = db.session.execute(
            update(Product)
            .where(Product.id == pid,
                   Product.archived.is_(False),
                   Product.qty_in_stock >= qty)
            .values(qty_in_stock=Product.qty_in_stock - qty))
        if res.rowcount == 0:
            db.session.rollback()
            raise OutOfStock(message=f"insufficient stock for product {pid}")
        db.session.add(OrderItem(
            order_id=order_id, product_id=pid, qty=qty,
            unit_price_cents=products[pid].price_cents))

    db.session.commit()

    saved = db.session.execute(
        _order_query().where(Order.id == order_id)
        .execution_options(populate_existing=True)).scalar_one()
    return OrderOut().dump(saved), 201