# 1. Import the PayPal SDK client that was created in `Set up Server-Side SDK`.
# from configuration_payments import PayPalClient
import sys
from paypalcheckoutsdk.orders import OrdersCreateRequest
from flask import (Flask, render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)

# 1. Import the PayPal SDK client created in `Set up Server-Side SDK` section.
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalhttp import HttpError
from paypalcheckoutsdk.orders import OrdersGetRequest


app = Flask(__name__)
# payments = Blueprint('payments', __name__)
# #https://developer.paypal.com/docs/checkout/reference/server-integration/setup-sdk/#install-the-sdk
# #https://developer.paypal.com/docs/checkout/reference/server-integration/set-up-transaction/#
# customizable e commerce website
# https://github.com/Jriles/CustomizableEcommerceWebsite


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


class CreateOrder(PayPalClient):

    # 2. Set up your server to receive a call from the client
    """ This is the sample function to create an order. It uses the
      JSON body returned by buildRequestBody() to create an order."""

    def create_order(self, debug=False):
        request = OrdersCreateRequest()
        # request.headers["Authorization"] = "A21AAHz4duLtmdJLhw6y9J_8C8uOZLfFWYRCUgdXiMIzoUive7_aiYyxAQFuVprxVeaCtPStMHmQYIXd - B5Sjq9ohhsy3v3sw"
        # request.headers['prefer'] = 'return=representation'
        request.prefer('return=representation')
        # 3. Call PayPal to set up a transaction
        request.request_body(self.build_request_body())
        response = self.client.execute(request)
        if debug:
            print('Status Code: ', response.status_code)
            print('Status: ', response.result.status)
            print('Order ID: ', response.result.id)
            print('Intent: ', response.result.intent)
            print('Links:')
            for link in response.result.links:
                print('\t{}: {}\tCall Type: {}'.format(
                    link.rel, link.href, link.method))
            print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                               response.result.purchase_units[0].amount.value))

        return response

        """Setting up the JSON request body for creating the order. Set the intent in the
    request body to "CAPTURE" for capture intent flow."""
    @staticmethod
    def build_request_body():
        """Method to create body with CAPTURE intent"""
        return \
            {
                "intent": "CAPTURE",
                "application_context": {
                    "user_action": "CONTINUE"
                },
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": "1.00",
                        },
                        "items": [
                            {
                                "name": "T-Shirt",
                                "unit_amount": {
                                    "currency_code": "EUR",
                                    "value": "1.00"
                                },
                                "quantity": "1",
                            }
                        ],
                    }
                ]
            }

class CaptureOrder(PayPalClient):

    # 2. Set up your server to receive a call from the client
    """this sample function performs payment capture on the order.
    Approved order ID should be passed as an argument to this function"""

    def capture_order(self, order_id, debug=False):
        """Method to capture order using order_id"""
        request = OrdersCaptureRequest(order_id)
        # 3. Call PayPal to capture an order
        response = self.client.execute(request)
        # 4. Save the capture ID to your database. Implement logic to save capture to your database for future reference.
        approved_order_id = response.result.id
        if debug:
            print('Status Code: ', response.status_code)
            print('Status: ', response.result.status)
            print('Order ID: ', response.result.id)
            print('Links: ')
            for link in response.result.links:
                print('\t{}: {}\tCall Type: {}'.format(
                    link.rel, link.href, link.method))
            print('Capture Ids: ')
            for purchase_unit in response.result.purchase_units:
                for capture in purchase_unit.payments.captures:
                    print('\t', capture.id)
            print("Buyer:")
            print("\tEmail Address: {}\n\tName: {}\n\tPhone Number: {}".format(response.result.payer.email_address,
                                                                               response.result.payer.name.given_name +
                                                                               " " + response.result.payer.name.surname,
                                                                               response.result.payer.phone.phone_number.national_number))
        return response

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


"""This driver function invokes the get_order function with
   order ID to retrieve sample order details. """
#   GetOrder().get_order('REPLACE-WITH-VALID-ORDER-ID')


@app.route("/create-paypal-transaction", methods=['POST'])
def create_paypal_transaction():
    response = CreateOrder().create_order(debug=True)
    approved_order_id = response.result.id
    print('got here')
    for link in response.result.links:
        if link.rel == 'approve':
            approve_order_link = link.href
    #         <class 'paypalhttp.http_response.Result'>
    #         approve: https://www.sandbox.paypal.com/checkoutnow?token=3MY95906MP2707106 Call Type: GET
    if approve_order_link is not None:
        if approve_order_link.find("http://") != 0 and approve_order_link.find("https://") != 0:
            approve_order_link = "http://" + approve_order_link
        return redirect(('approve_order_link'))


@app.route("/get-paypal-transaction", methods=['POST'])
def get_paypal_transaction(approved_order_id):
    # order_id = 'REPLACE-WITH-APPORVED-ORDER-ID'
    print(order_id)
    order_id = approved_order_id
    response = GetOrder().get_order(order_id)
    print('got here too')
    return response


@app.route("/capture-paypal-transaction", methods=['POST'])
def capture_paypal_transaction():
    # order_id = 'REPLACE-WITH-APPORVED-ORDER-ID'
    order_id = approved_order_id
    response = CaptureOrder().capture_order(order_id, debug=True)
    return response


@ app.route("/", methods=['GET'])
def payment():

    return render_template('pay-server-2.html')


if __name__ == "__main__":
    app.run(debug=True)
