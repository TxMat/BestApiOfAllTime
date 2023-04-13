def create_order(client):
    response = client.post('/order', json={
        'product': {
            'id': 1,
            'quantity': 10
        }
    })
    assert response.status_code == 302


def put_valid_shipping_info(client):
    response = client.put('/order/1', json={
        "order": {
            "email": "elon.musk@spacex.com",
            "shipping_information": {
                "country": "Senegal",
                "address": "Rue des potiers",
                "postal_code": "G7H 0S5",
                "city": "Chicoutimi",
                "province": "QC"
            }
        }
    })
    assert response.status_code == 200


def put_valid_credit_card(client):
    response = client.put('/order/1', json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2024,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 200


def check_order(client):
    response = client.get('/order/1')
    assert response.status_code == 200
    assert response.json["order"]["id"] == 1
    assert response.json["order"]["total_price"] == 281.0


class TestProducts:
    NB_PRODUCTS = 50

    # Test the GET /products endpoint

    def test_get_all_products(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert len(response.json) == self.NB_PRODUCTS


class TestOrders:
    # Test the POST /order endpoint

    def test_create_order(self, client):
        response = client.post('/order', json={
            'product': {
                'id': 1,
                'quantity': 10
            }
        })
        assert response.status_code == 302

    def test_create_order_invalid_product(self, client):
        response = client.post('/order', json={
            'product': {
                'id': 100,
                'quantity': 10
            }
        })
        assert response.status_code == 404

    def test_create_order_invalid_quantity(self, client):
        response = client.post('/order', json={
            'product': {
                'id': 1,
                'quantity': -1
            }
        })
        assert response.status_code == 422

    def test_create_order_invalid_product_and_quantity(self, client):
        response = client.post('/order', json={
            'product': {
                'id': 100,
                'quantity': -1
            }
        })
        assert response.status_code == 404

    def test_create_order_empty(self, client):
        response = client.post('/order', json={})
        assert response.status_code == 422

    def test_create_order_empty_product(self, client):
        response = client.post('/order', json={
            'product': {
            }
        })
        assert response.status_code == 422

    def test_create_order_invalid_json(self, client):
        response = client.post('/order', json='invalid')
        assert response.status_code == 422

    def test_create_order_invalid_json_keys(self, client):
        response = client.post('/order', json={
            'invalid': {
                'id': 1,
                'quantity': 10
            }
        })
        assert response.status_code == 422

    def test_create_order_invalid_json_keys_2(self, client):
        response = client.post('/order', json={
            'product': {
                'invalid': 1,
                'quantity': 10
            }
        })
        assert response.status_code == 422


class TestPutShippingInfoOrder:
    # Test the PUT /order/<id> endpoint

    def test_put_order_valid_shipping_info(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "email": "elon.musk@spacex.com",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7H 0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 200

    # def test_put_order_invalid_email(self, client):
    #     create_order(client)
    #     response = client.put('/order/1', json={
    #         "order": {
    #             "email": "elon.musk@spacex",
    #             "shipping_information": {
    #                 "country": "Senegal",
    #                 "address": "Rue des potiers",
    #                 "postal_code": "G7H 0S5",
    #                 "city": "Chicoutimi",
    #                 "province": "QC"
    #             }
    #         }
    #     })
    #     assert response.status_code == 422

    def test_put_order_invalid_shipping_info(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "email": "elon.ma@china.com",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 422

    def test_put_order_invalid_postal_code(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "email": "hugo.mora@etu.uqac.ca",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })

        assert response.status_code == 422

    def test_put_order_no_shipping_info(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "email": "hugo.mora@etu.uqac.ca",
                "shipping_information": {
                }
            }
        })

        assert response.status_code == 422

    def test_put_order_no_email(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })

        assert response.status_code == 422

    def test_put_order_no_shipping_info_and_email(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
            }
        })

        assert response.status_code == 422

    def test_put_order_invalid_json(self, client):
        create_order(client)
        response = client.put('/order/1', json='invalid')
        assert response.status_code == 422

    def test_put_order_invalid_json_keys(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "invalid": {
                "email": "hugo.mora@etu.uqac.ca",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 422

    def test_put_order_invalid_json_keys_2(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "invalid": {
                "email": "hugo.mora@etu.uqac.ca",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 422

    def test_put_order_invalid_json_keys_3(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "invalid": "hugo.mora@etu.uqac.ca",
                "shipping_information": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 422

    def test_put_order_invalid_json_keys_4(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "order": {
                "email": "hugo.mora@etu.uqac.ca",
                "invalid": {
                    "country": "Senegal",
                    "address": "Rue des potiers",
                    "postal_code": "G7HXD0S5",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        })
        assert response.status_code == 422

    # Credit card tests


class TestPutCreditCardOrder:
    def test_put_valid_credit_card(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 200

    def test_put_invalid_credit_card(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "4002 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_2(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "0",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_3(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "4000 0000 0000 0002",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 13
            }
        })
        assert response.status_code == 422

    def test_put_empty_credit_card_(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_json(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json='invalid')
        assert response.status_code == 422

    def test_put_no_shipping_info_credit_card(self, client):
        create_order(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_json_keys(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "invalid": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_json_keys_2(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "invalid": "John Doe",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_invalid_credit_card_json_keys_3(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "invalid": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    def test_put_missing_credit_card_json_keys(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        response = client.put('/order/1', json={
            "credit_card": {
                "name": "John Doe",
                "number": "4242 4242 4242 4242",
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422

    # Get order tests


class TestGetOrder:
    def test_get_order(self, client):
        create_order(client)
        put_valid_shipping_info(client)
        put_valid_credit_card(client)
        response = client.get('/order/1')
        assert response.status_code == 200
        check_order(client)
