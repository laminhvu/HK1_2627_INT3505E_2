from flask import Flask, jsonify
app = Flask(__name__)
ORDERS = {
    "1": {"status": "pending"},
    "2": {"status": "shipped"},
    "3": {"status": "delivered"},
    "4": {"status": "processing"}
}
@app.route("/orders/<order_id>" , methods= ["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return {"error" : "not found"}, 404
    if order["status"] in ("shipped", "delivered"):
        return {"error" : "cannot delete"}, 409
    ORDERS.pop(order_id, None)
    return "", 204
@app.route("/orders", methods=["GET"])
def get_orders():
    return ORDERS
if __name__ == "__main__":
    app.run(host="127.0.0.1", port = 5000 , debug = True)
