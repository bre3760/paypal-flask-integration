from flask import (Flask, render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)
from paypalcheckoutsdk.orders import OrdersGetRequest


app = Flask(__name__)


class PayPalClient:
    def __init__(self):
        # self.client_id = "PAYPAL-SANDBOX-CLIENT-ID"
        # self.client_secret = "PAYPAL-SANDBOX-CLIENT-SECRET"
        self.client_id = "ASOGZarWLQCk0OALjWJ3HGPH5plLupgIyaxnUp_xxkMYbmaOxPeDxrk0rv53PfpbUfYExKmjFf3g2DWC"
        self.client_secret = "EGWz0AZJ1eMN27ITD-fog89er03zf7uGoSvFpomVsC4n2gJkF8f9Vme84_KXE6HsBRss3SmnEs4G-Zgr"

        """Set up and return PayPal Python SDK environment with PayPal access credentials.
           This sample uses SandboxEnvironment. In production, use LiveEnvironment."""

        self.environment = SandboxEnvironment(
            client_id=self.client_id, client_secret=self.client_secret)

        """ Returns PayPal HTTP client instance with environment that has access
            credentials context. Use this instance to invoke PayPal APIs, provided the
            credentials have access. """
        self.client = PayPalHttpClient(self.environment)

    def object_to_json(self, json_data):
        """
        Function to print all json data in an organized readable manner
        """
        result = {}
        if sys.version_info[0] < 3:
            itr = json_data.__dict__.iteritems()
        else:
            itr = json_data.__dict__.items()
        for key, value in itr:
            # Skip internal attributes.
            if key.startswith("__"):
                continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
                self.object_to_json(value) if not self.is_primittive(value) else\
                value
        return result

    def array_to_json_array(self, json_array):
        result = []
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if not self.is_primittive(item)
                              else self.array_to_json_array(item) if isinstance(item, list) else item)
        return result

    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)


class GetOrder(PayPalClient):

    # 2. Set up your server to receive a call from the client
    """You can use this function to retrieve an order by passing order ID as an argument"""

    def get_order(self, order_id):
        """Method to get order"""
        request = OrdersGetRequest(order_id)
        # 3. Call PayPal to get the transaction
        response = self.client.execute(request)
        # 4. Save the transaction in your database. Implement logic to save transaction to your database for future reference.
        print('Status Code: ', response.status_code)
        print('Status: ', response.result.status)
        print('Order ID: ', response.result.id)
        print('Intent: ', response.result.intent)
        print('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(
                link.rel, link.href, link.method))
        print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                           response.result.purchase_units[0].amount.value))


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


@app.route("/getDetails/<orderID>/capture")
def getparams(orderID):
    oorr = GetOrder.get_order(orderID)
    print('got here', oorr.result.id)
    return oorr.result.id


@app.route("/payment/<int:price>", methods=['GET'])
def payment(price):
    order = build_request_body(price)
    print(order)
    return render_template('half.html', order=order)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
