import json, os, socket
from datetime import datetime
from .configs import db, Payload, app
from flask import Flask, g, request, jsonify, Response, escape

db.create_all()
db.session.commit()

@app.route("/")
def hello():
    #db.drop_all()
    #db.session.commit()
    return "Add some payloads"

@app.route('/payloads', methods=['GET'])
def get_payloads():
    payload_entries = Payload.query.all()
    print(payload_entries)
    return jsonify(payload=[i.serialize for i in payload_entries])

@app.route('/payloads', methods=['POST'])
def insert_payload():
    data_json = request.get_json()
    post_data = json.dumps(data_json)

    if validate_payload(post_data) == True:
      #payloads.insert(0,post_data)
      ts_db = int(data_json['ts'])
      message_db = str(data_json['message'])
      payload = Payload(ts=ts_db, 
			sender=data_json['sender'],
			message=message_db,
			sent_from_ip=data_json['sent-from-ip'],
			priority=data_json['priority'])
      db.session.add(payload)
      db.session.commit()
      return "Success"
    else:
      response = Response(json.dumps({
         'error': 'invalid payload'
      }), status=400, mimetype='application/json')
      return response

""" Validation part """

payload_string = '''
{
        "ts": "1530228282",
        "sender": "testy-test-service",
        "message": {
        "foo": "bar",
        "baz": "bang",
        "car": "wash"
        },
        "sent-from-ip": "1.2.3.4",
        "priority": 2
}
'''
data = json.loads(payload_string)
formated_data = json.dumps(data, indent=2)

print("given payload\n")
print(formated_data)

def validate_ts(some_ts):
  ts = datetime.fromtimestamp(int(some_ts))
  try:
    datetime.strptime(str(ts), '%Y-%m-%d %H:%M:%S')
    return True
  except ValueError as e:
    print("Invalid ts format, couldn't convert to YYYY-MM-DD HH:MM:SS")
    return False

def validate_sender(some_sender):
  try:
    if isinstance(some_sender, str) == False:
      raise ValueError("sender not string")
    else:
      return True
  except ValueError as e:
    print("Field sender is not a string")
    return False

def validate_json_msg(str_message):
  json_message = json.dumps(str_message, indent=2)
  try:
    json_object = json.loads(json_message)
    if len(json_object.keys()) == 0:
      raise ValueError("Message has no content")
    else:
      return True
  except ValueError as e:
    print("Field message can't be empty")
    return False

def validate_ip(addr):
  try:
    socket.inet_aton(addr)
    return True
  except IOError as e:
    print("Invalid IPv4 address", addr)
    return False

def validate_payload(payload_str):
  verifier = True
  payload = json.loads(payload_str)
  payload_accepted_fields = ['ts', 'sender', 'message', 'sent-from-ip', 'priority']

  for payload_key in payload.keys():
    try:
      if payload_key not in payload_accepted_fields:
        raise ValueError("Unrecognized field", payload_key)
    except ValueError as e:
      print("Invalid field given:", payload_key)
      verifier = False

  if 'ts' not in payload:
    raise ValueError("Missing ts field")
  else:
    valid_ts = payload['ts']
    verifier = validate_ts(valid_ts) and verifier

  if 'sender' not in payload:
    raise ValueError("Missing sender field")
  else:
    valid_sender = payload['sender']
    verifier = validate_sender(valid_sender) and verifier

  if 'message' not in payload:
    raise ValueError("Missing message field")
  else:
    valid_message = payload['message']
    verifier = validate_json_msg(valid_message) and verifier 

  if 'sent-from-ip' in payload:
    valid_ip = payload['sent-from-ip']
    verifier = validate_ip(valid_ip) and verifier

  return verifier

