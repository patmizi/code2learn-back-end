from chalice import Chalice, Response
from pymongo import MongoClient
import uuid

app = Chalice(app_name='code2learn-back-end')
app.debug = True

def generate_uuid():
    return uuid.uuid4()

def connect__mongodb(user="monkas-user", password="2~uNTmY@", address="ds031167.mlab.com",
                     port="31167", db_name="monkas-c2l"):
    #
    #   Function: Facilitates the connection and access to MongoDB.
    #

    #   Create a connection to a MongoDB instance.
    if user or password or address or db_name:

        #   If a defined database with its respective details are set, connect to it.
        connection = MongoClient(address, int(port))
        db = connection[db_name]
        db.authenticate(user, password)

    else:

        #   If there is no defined database, connect to the default database.
        client = MongoClient()
        db = client["monkas-c2l"]

    return db

@app.route('/add-user', methods=['POST'])
def add_user():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    if len(body["username"]) <= 0:
        return Response(body='No username was provided', status_code=400, headers={'Content-Type': 'text/plain'})
    matching_users = db_client["users"].find_one({ "username": body["username"] })
    if matching_users is not None:
        return Response(body='Username is already in use', status_code=400, headers={'Content-Type': 'text/plain'})
    body["_id"] = str(generate_uuid())
    db_client["users"].insert_one(body)
    return { "res": body }

@app.route('/get-events', methods=['POST'])
def get_events():
    return { "hello" : "world" }

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
