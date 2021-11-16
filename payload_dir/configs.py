import os
from flask import Flask, g, request, jsonify, Response, escape
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + 'root' + ':' + os.getenv('db_root_password') + '@' + os.getenv('MYSQL_SERVICE_HOST') + ':' + os.getenv('MYSQL_SERVICE_PORT') + '/' + os.getenv('db_name')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Payload(db.Model):
    #__tablename__ = 'payload'
    ts = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    sent_from_ip = db.Column(db.String(20), nullable=True)
    priority = db.Column(db.Integer, nullable=True)

    def __init__(self, ts, sender, message, sent_from_ip, priority):
        self.ts = ts
        self.sender = sender
        self.message = message
        self.sent_from_ip = sent_from_ip
        self.priority = priority

    def __repr__(self):
        return f"Payload('{self.ts}', '{self.sender}', '{self.message}', '{self.sent_from_ip}', '{self.priority}')"

    @property
    def serialize(self):
      return {
        'ts': self.ts,
        'sender': self.sender,
        'message': self.message,
        'sent_from_ip': self.sent_from_ip,
        'priority': self.priority
      }


