from chalice import Chalice, Response, BadRequestError, UnauthorizedError
from pymongo import MongoClient
import uuid

app = Chalice(app_name='code2learn-back-end')
app.debug = True

MAX_GROUP_LIMIT = 5

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

def create_group(group, event_id, client):
    person_ids = []
    person_data = []
    for person in group:
        if 'person-id' in person:
            person_ids.append(person['person-id'])
    # Find persondata for group members
    pointer = client["users"].find({"_id":{"$in":person_ids}}, {"username":0, "password":0})
    for person in pointer:
        person_data.append(person)
    # Find event data for event id
    event_data = client["events"].find_one({"_id":event_id})
    # Add an event group
    client["event_groups"].insert_one({
        "_id": str(generate_uuid()),
        "event": event_data,
        "members": person_data
    })
    # Remove data from queue
    client["lfg_queue"].remove({"event-id": event_id, "person-id": { "$in": person_ids }})

def join_lfg_queue(person_id, event_id, client):
    try:
        exists = client["lfg_queue"].find({"event-id": event_id, "person-id": person_id}).count()
        if exists > 0:
            raise Exception("User is already in queue")
        client["lfg_queue"].insert_one({ "event-id": event_id, "person-id": person_id })
        queue = []
        pointer = client["lfg_queue"].find({"event-id": event_id})
        for event in pointer:
            if 'event-id' in event:
                queue.append(event)
        if len(queue) >= MAX_GROUP_LIMIT:
            create_group(queue[:MAX_GROUP_LIMIT], event_id, client)
    except Exception as e:
        raise Exception("An error occured when trying to connect to the database: ", e.message)

def list_joined_groups(person_id, client):
    try:
        event_groups = []
        pointer = client["event_groups"].find({"members._id": person_id})
        for event in pointer:
            if 'event' in event:
                event_groups.append(event)
        return event_groups
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

@app.route('/event/group/join', methods=['POST'], cors=True)
def join_event_group():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        join_lfg_queue(body["person-id"], body["event-id"], db_client)
        return
    except Exception as e:
        return BadRequestError(e)

@app.route('/person/groups/list', methods=['POST'], cors=True)
def list_person_groups():
    body = app.current_request.json_body
    db_client = connect__mongodb()
    try:
        events = list_joined_groups(body["_id"], db_client)
        return events
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