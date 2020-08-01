
from flask import (Flask, render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)

app = Flask(__name__)


def build_request_body(price):
    """Method to create body with CAPTURE intent"""

    order = {
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "EUR",
                    "value": price,
                },

            }
        ]
    }
    return (order)


@app.route("/payment/<int:price>", methods=['GET'])
def payment(price):
    order = build_request_body(price)
    print(order)
    return render_template('pay-buttons.html', order=order)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
