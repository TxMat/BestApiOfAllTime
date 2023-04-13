import json
import os
import uuid

import peewee
import redis
import requests
from flask import Flask, request, redirect, url_for, jsonify
from flask_cors import CORS
from playhouse.shortcuts import dict_to_model, model_to_dict
from rq import Queue, Worker

import errors

app = Flask(__name__)
db = peewee.PostgresqlDatabase(
    os.environ.get('DB_NAME', 'inf349'),
    user=os.environ.get('DB_USER', 'user'),
    password=os.environ.get('DB_PASSWORD', 'pass'),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', 5432)
)

CORS(app, resources={r"/*": {"origins": "*"}})
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
conn = redis.from_url(redis_url)
# Créer une liste de queues à écouter
queues = [Queue('default', connection=conn)]


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Error(BaseModel):
    id = peewee.AutoField(primary_key=True, unique=True)
    code = peewee.CharField(null=False)
    name = peewee.CharField(null=False)


class Product(BaseModel):
    id = peewee.AutoField(primary_key=True, unique=True)
    name = peewee.CharField(null=False)
    type = peewee.CharField(null=False)
    description = peewee.CharField()
    image = peewee.CharField()
    height = peewee.IntegerField(null=False)
    weight = peewee.IntegerField(null=False)
    price = peewee.FloatField(null=False)
    in_stock = peewee.BooleanField(null=False, default=False)


# shipping info model
class ShippingInfo(BaseModel):
    id = peewee.AutoField(primary_key=True, unique=True)
    country = peewee.CharField(null=False)
    address = peewee.CharField(null=False)
    postal_code = peewee.CharField(null=False, constraints=[peewee.Check('length(postal_code) = 7')])
    city = peewee.CharField(null=False)
    province = peewee.CharField(null=False)


class Transaction(BaseModel):
    id = peewee.CharField(primary_key=True, unique=True)
    success = peewee.BooleanField(null=False, default=False)
    amount_charged = peewee.FloatField(null=False)
    error = peewee.ForeignKeyField(Error, backref='error', null=True)


class CreditCard(BaseModel):
    id = peewee.AutoField(primary_key=True, unique=True)
    name = peewee.CharField(null=False)
    first_digits = peewee.CharField(null=False)
    last_digits = peewee.CharField(null=False)
    expiration_month = peewee.IntegerField(null=False)
    expiration_year = peewee.IntegerField(null=False)


class Order(BaseModel):
    id = peewee.AutoField(primary_key=True, unique=True)
    shipping_info = peewee.ForeignKeyField(ShippingInfo, backref='shipping_info', null=True)
    email = peewee.CharField(null=True)
    paid = peewee.BooleanField(null=False, default=False)
    credit_card = peewee.ForeignKeyField(CreditCard, backref='credit_card', null=True)
    transaction = peewee.ForeignKeyField(Transaction, backref='transaction', null=True)
    pending = peewee.BooleanField(null=False, default=False)


# m2m table
class OrderProduct(BaseModel):
    order = peewee.ForeignKeyField(Order, backref='order')
    product = peewee.ForeignKeyField(Product, backref='product')
    quantity = peewee.IntegerField(null=False)


@app.route('/', methods=['GET'])
def display_products():
    populate_database(True)
    products = Product.select()
    return jsonify([model_to_dict(product) for product in products])


@app.route('/order', methods=['POST'])
def post_order():
    try:
        payload = request.json.get('product')
        return post_order_single_product(payload)
    except AttributeError:
        try:
            payload = request.json.get('products')
            return post_order_many_products(payload)

        except AttributeError:
            return errors.error_handler("order", "json-not-valid", "Le json n\'est pas au bon format"), 422


def check_product_before_order(product_id, quantity):
    # check if product exists
    product = Product.select().where(Product.id == product_id).first()
    if not product:
        return errors.error_handler("order", "product-does-not-exist", "Le produit n'existe pas"), 404

    # check if product is in stock
    if not product.in_stock:
        return errors.error_handler("products", "out-of-inventory", "Le produit demandé n'est pas en inventaire"), 422

    # check if quantity is valid
    if quantity < 1:
        return errors.error_handler("order", "invalid-quantity", "La quantité ne peut pas être inférieure à 1"), 422

    return None


def post_order_single_product(payload):
    product_id = payload.get('id')
    quantity = payload.get('quantity')
    if not product_id or not quantity:
        return errors.error_handler("products", "missing-fields",
                                    "La création d'une commande nécessite un produit et une quantité"), 422
    product_errors = check_product_before_order(product_id, quantity)
    if product_errors is not None:
        return product_errors

    # create order
    try:
        new_order = Order.create()
        OrderProduct.create(order_id=new_order.id, product_id=product_id, quantity=quantity)
    except peewee.IntegrityError as e:
        print(e)
        return errors.error_handler("order", "invalid-fields", "Les champs sont mal remplis"), 422

    # redirect to order/<id> page after creation
    return redirect(url_for('order_id_handler', order_id=new_order.id))


def post_order_many_products(payload):
    if not isinstance(payload, list):
        return errors.error_handler("order", "invalid-fields", "Les champs sont mal remplis"), 422

    products = list()
    for product in payload:
        product_id = product.get('id')
        quantity = product.get('quantity')

        if not product_id or not quantity:
            return errors.error_handler("products", "missing-fields",
                                        "La création d'une commande nécessite un produit et une quantité"), 422

        product_errors = check_product_before_order(product_id, quantity)
        if product_errors is not None:
            return product_errors

        products.append(product)

    try:
        new_order = Order.create()
        for product in products:
            OrderProduct.create(order_id=new_order.id, product_id=product.get("id"), quantity=product.get("quantity"))
    except peewee.IntegrityError as e:
        print(e)
        return errors.error_handler("order", "invalid-fields", "Les champs sont mal remplis"), 422
    return redirect(url_for('order_id_handler', order_id=new_order.id))


@app.route('/order/<int:order_id>', methods=['GET', 'PUT'])
def order_id_handler(order_id):
    def get_order():
        cached_order = conn.get(order_id)
        if cached_order:
            return json.loads(cached_order)

        # Check if order exists
        order = Order.select().where(Order.id == order_id).first()
        if not order:
            return errors.error_handler("order", "order-does-not-exist", "L'order n'existe pas"), 404

        # Get order info
        order_dict = model_to_dict(order)

        del order_dict["pending"]

        # Get product info from order.product_id
        order_products = OrderProduct.select().where(OrderProduct.order_id == order.id).execute()

        weight = 0
        total_price = 0
        order_dict["products"] = list()
        for order_product in order_products:
            # Add product info to order
            order_dict["products"].append({
                "id": order_product.product.id,
                "quantity": order_product.quantity
            })

            # Add total price to the total
            total_price += order_product.product.price * order_product.quantity

            # Shipping price is calculated from product weight and quantity and added to the total price
            weight += order_product.quantity * order_product.product.weight

        order_dict["total_price"] = total_price
        order_dict["shipping_price"] = calculate_shipping_price(weight)
        # Get shipping info from order.shipping_info_id
        shipping_info = {}
        if order.shipping_info:
            shipping_info = model_to_dict(ShippingInfo.select().where(ShippingInfo.id == order.shipping_info.id).get())
            # no need to send id to client
            del shipping_info["id"]

        order_dict["shipping_info"] = shipping_info

        # Get credit card from order.credit_card_id
        credit_card = {}
        if order.credit_card:
            credit_card = model_to_dict(CreditCard.select().where(CreditCard.id == order.credit_card.id).get())
            # no need to send id to client
            del credit_card["id"]

        order_dict["credit_card"] = credit_card

        # Get transaction from order.transaction_id
        transaction = {}
        if order.transaction:
            transaction = model_to_dict(Transaction.select().where(Transaction.id == order.transaction.id).get())
            if transaction["error"] is None:
                transaction["error"] = {}
            else:
                del transaction["error"]["id"]
                del transaction["id"]

        order_dict["transaction"] = transaction

        final_order_json = {"order": order_dict}
        if order.transaction and transaction["success"] is True:
            try:
                conn.set(order_id, json.dumps(final_order_json))
            except json.JSONDecodeError:
                return errors.error_handler("order", "unknown-error", "contactez l'administrateur du site"), 418  # :)
        return final_order_json

    def put_order():
        def update_shipping_order(data):
            if not all(key in data for key in ("shipping_information", "email")):
                raise ValueError
            shipping_info = data["shipping_information"]
            if not all(key in shipping_info for key in ("address", "city", "province", "postal_code", "country")):
                raise ValueError

                # Check if shipping info exists
            if order.shipping_info:
                # Update shipping info instance
                shipping_info_instance = ShippingInfo.select().where(ShippingInfo.id == order.shipping_info.id).get()
                shipping_info_instance.update(**shipping_info).execute()
            else:
                # Create new shipping info instance
                try:
                    shipping_info_instance = ShippingInfo.create(**shipping_info)
                    order.shipping_info = shipping_info_instance
                except peewee.IntegrityError:
                    return errors.error_handler("orders", "invalid-fields",
                                                "Les informations d'achat ne sont pas correctes"), 422

            # Update order email and save
            order.email = data["email"]
            try:
                order.save()
            except peewee.IntegrityError:
                return errors.error_handler("orders", "invalid-fields",
                                            "Les informations d'achat ne sont pas correctes"), 422

            return get_order()

        def update_credit_card(data):
            order.pending = True
            order.save()
            job = queues[0].enqueue_call(
                func=do_background_task, args=(data, order), result_ttl=5000
            )
            return "Created", 202

        # Check if order exists
        order = Order.select().where(Order.id == order_id).first()

        if not order:
            return errors.error_handler("order", "order-not-found", "L'order n'existe pas"), 404

        if order.pending:
            return errors.error_handler("order", "order-pending", "L'order est en cours de traitement"), 409

        try:
            # Check payload
            payload = request.json
            if "order" in payload:
                return update_shipping_order(payload["order"])
            elif "credit_card" in payload:
                return update_credit_card(payload["credit_card"])
            else:
                return errors.error_handler("order", "missing-fields", "Il manque des champs dans le json"), 422
        except (json.JSONDecodeError, ValueError):
            return errors.error_handler("order", "json-not-valid", "Le json n'est pas au bon format"), 422

    if request.method == 'GET':
        return get_order()
    elif request.method == 'PUT':
        return put_order()


def do_background_task(data, order):
    order_products = OrderProduct.select().where(OrderProduct.order_id == order.id).execute()

    amount_charged = 0
    weight = 0
    for order_product in order_products:
        amount_charged += order_product.product.price * order_product.quantity
        weight += order_product.product.weight * order_product.quantity

    def set_error(odr, name, code):

        error = Error.create(name=name, code=code)
        error.save()
        # check if transaction exists
        if odr.transaction:
            # delete old error
            old_error = None
            if odr.transaction.error:
                old_error = Error.select().where(Error.id == odr.transaction.error.id).get()
            odr.transaction.error = error.id
            odr.transaction.save()
            if old_error:
                old_error.delete_instance()
        else:
            odr.transaction = Transaction.create(id=uuid.uuid1(), success=False, error=error.id, amount_charged=amount_charged)
        odr.save()
        clear_order_lock()
        return

    def clear_order_lock():
        order.pending = False
        order.save()
        return

    if order.paid:
        return set_error(order, "already-paid", "La commande a déjà été payée")

    if not all(key in data for key in ("name", "number", "expiration_year", "cvv", "expiration_month")):
        return set_error(order, "missing-fields", "Il manque des champs dans le json")

    if order.email is None or order.shipping_info is None:
        return set_error(order, "missing-fields",
                         "Les informations du client sont nécessaire avant"
                         " d'appliquer une carte de crédit")

    if not (data["number"] == "4000 0000 0000 0002" or data["number"] == "4242 4242 4242 4242"):
        return set_error(order, "incorrect-number", "Le numéro de carte est invalide")

    if len(order_products) == 0:
        return set_error(order, "no-products", "Aucun produit dans la commande")

    pay_payload = {
        "credit_card": {**data},
        "amount_charged": amount_charged + calculate_shipping_price(
            weight),
    }

    # Send payment request
    response = requests.post("http://dimprojetu.uqac.ca/~jgnault/shops/pay/", json=pay_payload)

    if response.status_code == 200:
        # Create transaction
        transaction = Transaction.create(**response.json()["transaction"])
        order.transaction = transaction
        order.paid = True
        order.save()
    else:
        clear_order_lock()
        return set_error(order, response.json()["errors"]["credit_card"]["code"], response.json()["errors"]["credit_card"]["name"])

        # add credit card to order
    try:
        credit_card = CreditCard.create(name=data["name"], first_digits=data["number"][:4],
                                        last_digits=data["number"][-4:],
                                        expiration_year=data["expiration_year"],
                                        expiration_month=data["expiration_month"])
        order.credit_card = credit_card
        order.save()
        clear_order_lock()
    except peewee.IntegrityError:
        return set_error(order, "invalid-fields",
                         "Les informations de la carte de crédit ne sont pas correctes")


def calculate_shipping_price(weight):
    if weight < 500:
        return 5
    elif weight < 2000:
        return 10
    else:
        return 25


def populate_database(debug=False):
    # create products from url and add to database (only if database is empty)
    if Product.select().count() == 0:
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        products = json.loads(response.content)
        for product in products["products"]:
            # strip fields
            for key in product:
                if isinstance(product[key], str):
                    product[key] = product[key].strip('\x00')
            if debug:
                print("Adding product: " + product["name"])
            product = dict_to_model(Product, product)
            # loops through all the fields in the model and sets them to the values in the dict
            try:
                Product.create(**product.__dict__['__data__'])
            except peewee.IntegrityError as e:
                print("invalid product: " + product.name)
                print("Error: " + str(e))


@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct, Error])
    populate_database(True)


@app.cli.command("worker")
def worker_starter():
    db.connect()
    redis_url = os.environ.get('REDIS_URL')
    conn = redis.from_url(redis_url)
    # Créer une liste de queues à écouter
    queues = [Queue('default', connection=conn)]
    # Créer un worker pour traiter les tâches en attente
    worker = Worker(queues, connection=conn)
    # Démarrer le worker
    worker.work()


def delete_db():
    db.drop_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct, Error])
    db.close()


if __name__ == "__main__":
    init_db()
    app.run()
