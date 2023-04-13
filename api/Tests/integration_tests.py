from api.inf349 import db, Order, Product, ShippingInfo, Transaction, CreditCard, OrderProduct, populate_database


def init_db():
    db.connect()
    db.drop_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct])
    db.create_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct])
    populate_database()


class TestOrder():
    def test_the_ultimate_test(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert len(response.json) == 50

        response = client.post('/order', json={
            'product': {
                'id': 1,
                'quantity': 10
            }
        })
        assert response.status_code == 302

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

        response = client.put('/order/1', json={
            "credit_card": {
                "name": "Eddy Malou",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 200

        assert response.status_code == 200

        response = client.put('/order/1', json={
            "credit_card": {
                "name": "Eddy Malou",
                "number": "4242 4242 4242 4242",
                "expiration_year": 2024,
                "cvv": "123",
                "expiration_month": 9
            }
        })
        assert response.status_code == 422




