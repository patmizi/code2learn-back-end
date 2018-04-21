from chalice import Chalice, Response, BadRequestError, UnauthorizedError
from pymongo import MongoClient
import uuid

app = Chalice(app_name='code2learn-back-end')
app.debug = True

def verify_userid(id, client):
    if len(id) <= 0 :
        raise ValueError('No ID was provided')
    try:
        res = client["users"].find_one({"_id": str(id)}, { "password": 0 })
        if '_id' in res:
            return res
        else:
            raise Exception('The id provided is invalid')
    except Exception as e:
        raise Exception("An error has occured when trying to verify the user: ", e.message)

def get_login_token(username, password, client):
    if len(username) <= 0 or len(password) <= 0 :
        raise ValueError('Invalid credentials were provided')
    try:
        return client["users"].find_one({"username": username, "password": password}, {"_id": 1})
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: ", e.message)

def get_filtered_events(filter, client):
    # TODO: Add filter
    try:
        events = []
        pointer = client["events"].find({}, {"attributes":0})
        for event in pointer:
            events.append(event)
        return events
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: " + e.message)

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
        # 400 Error Response
        return Response(body='No username was provided',
                        status_code=400,
                        headers={'Content-Type': 'text/plain'})
    matching_users = db_client["users"].find_one({ "username": body["username"] })
    if matching_users is not None:
        # 400 Error Response
        return Response(body='Username is already in use',
                        status_code=400,
                        headers={'Content-Type': 'text/plain'})
    body["_id"] = str(generate_uuid())
    db_client["users"].insert_one(body)
    return { "res": body }

@app.route('/verify-user', methods=['POST'])
def verify_user():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        token = get_login_token(body["username"], body["password"], db_client)
        return { "token": token["_id"] }
    except Exception as e:
        return BadRequestError(e)

@app.route('/get-events', methods=['POST'])
def get_events():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        events = get_filtered_events(body, db_client)
        # do some cool filtering here
        return events
    except Exception as e:
        return BadRequestError(e)


