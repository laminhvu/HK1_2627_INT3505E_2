import base64
import json


 
from flask import Flask, jsonify, request

import random
app = Flask(__name__)

random.seed(42)

STATUSES = ["pending", "paid", "shipped", "cancelled"]

ORDERS =[]

for i in range (1, 51):
    order = {
        "id" : i,
        "customer_id" :random.randint(1,10),
        "status" : random.choice(STATUSES),
        "total" : random.randint(1,100)

    }
    ORDERS.append(order)

FIELDS = ["id", "customer_id", "status", "total"]
SORTABLE = ["id", "total"]


def error400(message):
    return jsonify(error = message), 400




def encode_cursor(sort_field, direction, last_value, last_id, status, customer_id):
    data ={
        "sort" : sort_field,
        "direction" : direction,
        "value" : last_value,
        "id" : last_id,
        "status" : status,
        "customer_id" : customer_id
    }

    jsoncon = json.dumps(data)
    rawbyte = jsoncon.encode()
    token = base64.urlsafe_b64encode(rawbyte)


    return token.decode()

def decode_cursor(token):
    try:
        rawbyte = base64.urlsafe_b64decode(token)
        data = json.loads(rawbyte)
    except Exception:
        return None

    return data

def is_after(order, sort_field, last_value, last_id , direction):
    if order[sort_field] == last_value:
        if direction == "asc":
            return order["id"] > last_id
        else:
            return order["id"] < last_id

        
    else:
        if direction == "asc" :
            return order[sort_field] > last_value
        
        else:
            return order[sort_field] < last_value




@app.get("/orders")
def list_order():

    # lọc lỗi
    limit_text = request.args.get("limit" , "10")
    if not limit_text.isdigit():
        return error400("limit phai la so nguyen  ")


    limit_text = int(limit_text)
    if limit_text < 1 or limit_text > 100:
        return error400("limit phai trong khoang 1 toi 100")


    sort_text = request.args.get("sort", "id")
    if sort_text.startswith("-"):
        direction = "desc"
        sort_field = sort_text[1:]
    else: 
        direction = "asc"
        sort_field = sort_text

    if sort_field not in SORTABLE:
        return error400("sort chi ho tro id va total")





    status = request.args.get("status")
    if status is not None and status not in STATUSES:
        return error400("status khong hop le")


    customer_id = request.args.get("customer_id")
    if customer_id is not None:
        if not customer_id.isdigit():
            return error400("customer_id phai la so nguyen")
        customer_id = int(customer_id)

    fields_text = request.args.get("fields")
    fields = None
    if fields_text :
        fields = fields_text.split(",")
        for f in fields:
            if f not in FIELDS:
                return error400("field khong ton tai" + f)

    cursor_text = request.args.get("cursor")
    cursor = None
    if cursor_text:
        cursor = decode_cursor(cursor_text)
        if cursor is None: return error400("cursor khong hopj le")

        if (cursor["sort"] !=sort_field or cursor["direction"] != direction or cursor["status"] != status or cursor["customer_id"] != customer_id):
            return error400("cursor khong khop voi sort/ filter hien tai")


    # filter
    rows = []
    for order in ORDERS:
        if status is not  None and order["status"] != status:
            continue
        if customer_id is not None and order["customer_id"] !=customer_id:
            continue
        rows.append(order)

    #sort
    def sort_key(order):
        return (order[sort_field], order["id"])

    rows.sort(key = sort_key, reverse = (direction== "desc"))


    #cursor
    if cursor is not None:
        remaining = []
        for order in rows:
            if is_after(order, sort_field, cursor["value"], cursor["id"], direction):
                remaining.append(order)
        rows = remaining
    

    #limit
    page = rows[0:limit_text + 1]

    has_more = False
    if len(page) > limit_text:
        has_more = True
        page = page[0:limit_text]

    #next cursor
    next_cursor = None
    if has_more:
        last = page[-1]
        next_cursor = encode_cursor(sort_field, direction, last[sort_field], last["id"], status, customer_id)

    #spare fieldset
    if fields is not None :
        short_page = []
        for order in page:
            short_order = {}
            for f in fields :
                short_order[f] = order[f]
            short_page.append(short_order)
        page = short_page
    return jsonify({"data" : page, "next_cursor" : next_cursor , "has_more" : has_more})


if __name__ == "__main__":
    app.run(debug = True)


