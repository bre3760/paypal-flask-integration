
from flask import (Flask, render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)

app = Flask(__name__)


def build_request_body():
    """Method to create body with CAPTURE intent"""

    order = {
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "EUR",
                    "value": "1.69",
                },

            }
        ]
    }
    return jsonify(order)


@app.route("/", methods=['GET'])
def payment():
    order = build_request_body()
    return render_template('pay-buttons.html')


if __name__ == "__main__":
    app.run(debug=True)
