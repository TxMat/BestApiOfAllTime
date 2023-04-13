# conftest file for pytest to set up the test environment
# we use the flask test client to make requests to the app
# we initialize flask and peewee

import pytest

from api.inf349 import app, db, Order, Product, ShippingInfo, Transaction, CreditCard, OrderProduct, populate_database


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    # init db
    db.connect()
    db.create_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct])
    populate_database()
    yield client
    # teardown db
    db.drop_tables([Product, ShippingInfo, Transaction, CreditCard, Order, OrderProduct])
    db.close()


@pytest.fixture
def runner():
    return client.test_cli_runner()
