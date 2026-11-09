from marshmallow import Schema, fields, validate


class OrderItemIn(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    customer_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=120))
    items = fields.List(
        fields.Nested(OrderItemIn), required=True,
        validate=validate.Length(min=1, max=100))


class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    sku = fields.Str(attribute="product.sku")
    name = fields.Str(attribute="product.name")
    qty = fields.Int()
    unit_price_cents = fields.Int()
    line_total_cents = fields.Method("get_line_total")

    def get_line_total(self, obj):
        return obj.qty * obj.unit_price_cents


class OrderOut(Schema):
    id = fields.Int()
    customer_name = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
    items = fields.List(fields.Nested(OrderItemOut))
    total_cents = fields.Method("get_total")

    def get_total(self, obj):
        return sum(i.qty * i.unit_price_cents for i in obj.items)