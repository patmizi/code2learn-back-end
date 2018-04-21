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

def get_events(client, event_ids=[]):
    try:
        print(event_ids)
        events = []
        if len(event_ids) <= 0:
            pointer = client["events"].find({}, {"attributes": 0})
        else:
            pointer = client["events"].find({"_id": {"$in":event_ids}}, {"attributes": 0})
        for event in pointer:
            events.append(event)
        return events
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: " + e.message)

def get_event(id, client):
    try:
        return client["events"].find_one({"_id":id}, {"attributes": 0})
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: ", e.message)

def get_saved_events(id, client):
    try:
        events = []
        person = client["users"].find_one({"_id": id})
        if 'events' not in person:
            return []
        for event in person["events"]:
            if event not in events:
                events.append(event["event-id"])
        return get_events(client, events)
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: ", e.message)

def add_saved_event(id, to_add, client):
    try:
        events = get_saved_events(id, client)
        for event in events:
            if event["event-id"] == to_add["event-id"]:
                return events
        client["users"].update_one({
            '_id':id
        }, {
            '$inc':{
                "events": to_add
            }
        },
            upsert=True
        )
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: ", e.message)

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



@app.route('/user/add', methods=['POST'], cors=True)
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

@app.route('/user/verify', methods=['POST'], cors=True)
def verify_user():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        token = get_login_token(body["username"], body["password"], db_client)
        return { "token": token["_id"] }
    except Exception as e:
        return BadRequestError(e)

@app.route('/event/list', methods=['GET', 'POST'], cors=True)
def get_all_events():
    request = app.current_request
    db_client = connect__mongodb()
    try:
        events = get_events(db_client)
        if request.method == "POST":
            # filter for a suggested list
            print("filter")
        return events
    except Exception as e:
        return BadRequestError(e)

@app.route('/event/get/{id}', cors=True)
def get_event_by_id(id):
    db_client = connect__mongodb()
    try:
        event = get_event(id, db_client)
        return event
    except Exception as e:
        return BadRequestError(e)

@app.route('/person/events/get', methods=['POST'], cors=True)
def get_events_saved():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        events = get_saved_events(body["_id"], db_client)
        return events
    except Exception as e:
        return BadRequestError(e)

@app.route('/person/events/save', methods=['POST'], cors=True)
def save_event():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        add_saved_event(body["_id"], body["event"], db_client)
        return get_saved_events(body["_id"], db_client)
    except Exception as e:
        return BadRequestError(e)