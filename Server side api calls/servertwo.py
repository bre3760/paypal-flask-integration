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
        req = OrdersCreateRequest()  # creates order request object
        req.prefer('return=representation')
        # 3. Call PayPal to set up a transaction
        req.headers["Authorization"] = "Bearer A21AAGx9kBGmT1OfCBmvmfY1i7Jh1ABija4gfEaCrTd1hRt6B-eid-MjsraKo1nOyLbeeuZp6yF8Dl6Z7-dgHL8PWWxTVrrZA"
        req.request_body(self.build_request_body())
        response = self.client.execute(req)
        # when in debug shows the response to the creation of the order
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
                    "user_action": "CONTINUE",
                    "redirect_urls": {
                        "return_url": url_for('done', _external=True),
                        "cancel_url": url_for('cancel', _external=True)
                    },
                },
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "EUR",
                            "value": "1.00",
                        },

                    }
                ]
            }

class CaptureOrder(PayPalClient):

    # 2. Set up your server to receive a call from the client
    """this sample function performs payment capture on the order.
    Approved order ID should be passed as an argument to this function"""

    def capture_order(self, order_id, debug=False):
        """Method to capture order using order_id"""
        req = OrdersCaptureRequest(order_id)
        # 3. Call PayPal to capture an order
        response = self.client.execute(req)
        # 4. Save the capture ID to your database. Implement logic to save capture to your database for future reference.
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


@app.route("/checkout/api/paypal/order/create/", methods=['POST'])
def create_paypal_transaction():
    response = CreateOrder().create_order(debug=True)
    print('got here')
    orderID = response.result.id
    for link in response.result.links:
        if link.rel == 'approve':
            approve_order_link = str(link.href)
            # <class 'paypalhttp.http_response.Result'>
            # approve: https://www.sandbox.paypal.com/checkoutnow?token=3MY95906MP2707106 Call Type: GET
    # if approve_order_link is not None:
    #     if approve_order_link.find("http://") != 0 and approve_order_link.find("https://") != 0:
    #         approve_order_link = "http://" + approve_order_link
    #     return redirect(approve_order_link)
    return orderID


@app.route("/checkout/api/paypal/order/<orderID>/capture/", methods=['POST'])
def capture_paypal_transaction(orderID):
    response = CaptureOrder().capture_order(orderID, debug=True)
    print('got here too')
    return response


@ app.route("/", methods=['GET'])
def payment():
    return render_template('pay-server-2.html')


@ app.route("/done", methods=['GET'])
def done():
    return render_template('done.html')


@ app.route("/cancel", methods=['GET'])
def cancel():
    return render_template('cancel.html')


if __name__ == "__main__":
    app.run(debug=True)


# {
#   "PayPal-Request-Id": "platform-1596267212538",
#   "Content-Type": "application/json",
#   "cache-control": "no-cache",
#   "Authorization": "Bearer A21*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​*​Xmtg"
# }
# {
#   "intent": "CAPTURE",
#   "purchase_units": [
#     {
#       "reference_id": "PU1",
#       "description": "Camera Shop",
#       "invoice_id": "INV-CameraShop-1596267211787",
#       "custom_id": "CUST-CameraShop",
#       "amount": {
#         "currency_code": "USD",
#         "value": 350,
#         "breakdown": {
#           "item_total": {
#             "currency_code": "USD",
#             "value": 300
#           },
#           "shipping": {
#             "currency_code": "USD",
#             "value": 20
#           },
#           "tax_total": {
#             "currency_code": "USD",
#             "value": 30
#           }
#         }
#       },
#       "items": [
#         {
#           "name": "DSLR Camera",
#           "description": "Black Camera - Digital SLR",
#           "sku": "sku01",
#           "unit_amount": {
#             "currency_code": "USD",
#             "value": 300
#           },
#           "quantity": "1",
#           "category": "PHYSICAL_GOODS"
#         }
#       ],
#       "shipping": {
#         "address": {
#           "address_line_1": "2211 North Street",
#           "address_line_2": "",
#           "admin_area_2": "San Jose",
#           "admin_area_1": "CA",
#           "postal_code": "95123",
#           "country_code": "US"
#         }
#       }
#     }
#   ],
#   "application_context": {
#     "shipping_preference": "SET_PROVIDED_ADDRESS",
#     "user_action": "PAY_NOW"
#   }
# }
