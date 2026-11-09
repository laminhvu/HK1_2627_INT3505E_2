from flask import Blueprint, abort, jsonify, request
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Product
from ..errors import Conflict
from ..schemas import ProductOut, ProductIn, ProductPatch, ReserveIn



products_bp = Blueprint(
    "products", __name__, url_prefix="/api/v1/products")



@products_bp.get("")
def list_products():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("size", 20))))
    base = db.select(Product).where(Product.archived.is_(False))
    rows = db.session.execute(base.order_by(Product.id)
                              .offset((page - 1) * size).limit(size)
    ).scalars().all()
    return jsonify({
        "items": [ProductOut().dump(p) for p in rows],
        "page": page, "size": size,
        "total": db.session.scalar(db.select(db.func.count())
                                   .select_from(Product)
                                   .where(Product.archived.is_(False))),
    }), 200







@products_bp.post("")
def create_product():
    body = ProductIn().load(request.json)
    p = Product(**body)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("sku already exists")
    return ProductOut().dump(p), 201



@products_bp.patch("/<int:id>")
def patch_product(id):
    body = ProductPatch().load(request.json, partial=True)
    p = db.get_or_404(Product, id)
    if p.archived:
        abort(404)
    for k, v in body.items():
        setattr(p, k, v)
    db.session.commit()
    return ProductOut().dump(p), 200


@products_bp.delete("/<int:id>")
def delete_product(id):
    p = db.get_or_404(Product, id)
    if p.archived:
        abort(404)
    p.archived = True
    db.session.commit()
    return "", 204

@products_bp.get("/<int:id>")
def get_product(id):
    p = db.get_or_404(Product, id)
    if p.archived:
        abort(404)
    return ProductOut().dump(p), 200


@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    body = ReserveIn().load(request.json)
    qty = body["qty"]
    p = db.get_or_404(Product, id)
    if p.archived:
        abort(404)

    result = db.session.execute(
        update(Product)
        .where(Product.id == id,
               Product.archived.is_(False),
               Product.qty_in_stock >= qty)
        .values(qty_in_stock=Product.qty_in_stock - qty)
    )


    if result.rowcount == 0:
        db.session.rollback()
        raise Conflict("insufficient stock")

    
    db.session.commit()

    db.session.refresh(p)
    return ProductOut().dump(p), 200
