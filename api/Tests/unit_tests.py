from api.inf349 import calculate_shipping_price, Order, Product, CreditCard, Transaction, ShippingInfo


class TestOrder():
    def test_shipping_price(self):
        assert calculate_shipping_price(20) == 5
        assert calculate_shipping_price(0) == 5
        assert calculate_shipping_price(500) == 10
        assert calculate_shipping_price(1555) == 10
        assert calculate_shipping_price(2000) == 25
        assert calculate_shipping_price(5000) == 25

    def test_create_order(self, client):
        # create order
        order = Order(id=1, email="test@gmail.com")
        assert order.id == 1
        assert order.email == "test@gmail.com"

    def test_create_order_string(self, client):
        # create order
        order = Order(id=1)
        assert str(order) == "1"


class TestProduct():

    def test_create_product(self, client):
        # create product
        product = Product(id=1, name="test", price=10)
        assert product.id == 1
        assert product.name == "test"
        assert product.price == 10

    def test_create_product_string(self, client):
        # create product
        product = Product(id=1)
        assert str(product) == "1"


class TestShippingInfo():

    def test_create_shipping_info(self, client):
        # create shipping info
        shipping_info = ShippingInfo(id=1, address="test", city="test", province="test", postal_code="test")
        assert shipping_info.id == 1
        assert shipping_info.address == "test"
        assert shipping_info.city == "test"
        assert shipping_info.province == "test"
        assert shipping_info.postal_code == "test"

    def test_create_shipping_info_string(self, client):
        # create shipping info
        shipping_info = ShippingInfo(id=1)
        assert str(shipping_info) == "1"


class TestTransaction():

    def test_create_transaction(self, client):
        # create transaction
        transaction = Transaction(
            id="gdfgdfgdfgbdfgjnfdsghjdfhudqsghqsfdnqskfbnj,kldsfghjsdnfbnjshsdfvbgsdgfbjsdgyuhfhnjsdfbjksdfgsdfhv ",
            success=True, amount_charged=10)
        assert transaction.id == "gdfgdfgdfgbdfgjnfdsghjdfhudqsghqsfdnqskfbnj,kldsfghjsdnfbnjshsdfvbgsdgfbjsdgyuhfhnjsdfbjksdfgsdfhv "
        assert transaction.success == True
        assert transaction.amount_charged == 10

    def test_create_transaction_string(self, client):
        # create transaction
        transaction = Transaction(id="hrtgghdf,gfd ")
        assert str(transaction) == "hrtgghdf,gfd "


class TestCreditCard():

    def test_create_credit_card(self, client):
        # create credit card
        credit_card = CreditCard(id=1, name="test", first_digits="7777",
                                                last_digits="7777",
                                                expiration_year="2023",
                                                expiration_month="12"
                                 )
        assert credit_card.name == "test"
        assert credit_card.first_digits == "7777"
        assert credit_card.last_digits == "7777"
        assert credit_card.expiration_year == "2023"
        assert credit_card.expiration_month == "12"


    def test_create_credit_card_string(self, client):
        # create credit card
        credit_card = CreditCard(id=1)
        assert str(credit_card) == "1"
