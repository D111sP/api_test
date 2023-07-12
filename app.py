from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifications.db'
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    operator_code = db.Column(db.String(10))
    tag = db.Column(db.String(50))
    timezone = db.Column(db.String(50))

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(500))
    filter_operator = db.Column(db.String(10))
    filter_value = db.Column(db.String(50))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

@app.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    new_client = Client(phone_number=data['phone_number'],
                        operator_code=data['operator_code'],
                        tag=data['tag'],
                        timezone=data['timezone'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify(message='Client created successfully')

@app.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify(message='Client not found'), 404

    data = request.get_json()
    client.phone_number = data['phone_number']
    client.operator_code = data['operator_code']
    client.tag = data['tag']
    client.timezone = data['timezone']

    db.session.commit()
    return jsonify(message='Client updated successfully')

@app.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify(message='Client not found'), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify(message='Client deleted successfully')

@app.route('/deliveries', methods=['POST'])
def create_delivery():
    data = request.get_json()
    new_delivery = Delivery(start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
                            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
                            message=data['message'],
                            filter_operator=data['filter_operator'],
                            filter_value=data['filter_value'])
    db.session.add(new_delivery)
    db.session.commit()

    if new_delivery.start_time <= datetime.utcnow() <= new_delivery.end_time:
        send_messages(new_delivery)

    return jsonify(message='Delivery created successfully')

@app.route('/statistics', methods=['GET'])
def get_statistics():
    deliveries = Delivery.query.all()
    statistics = []

    for delivery in deliveries:
        total_messages = Message.query.filter_by(delivery_id=delivery.id).count()
        sent_messages = Message.query.filter_by(delivery_id=delivery.id, status='Sent').count()
        failed_messages = Message.query.filter_by(delivery_id=delivery.id, status='Failed').count()

        statistics.append({
            'delivery_id': delivery.id,
            'total_messages': total_messages,
            'sent_messages': sent_messages,
            'failed_messages': failed_messages
        })

    return jsonify(statistics)

def send_messages(delivery):
    clients = Client.query.filter_by(operator_code=delivery.filter_operator,
                                     tag=delivery.filter_value).all()

    for client in clients:
        try:
            # Отправка сообщения клиенту через внешний сервис
            response = requests.post('https://probe.fbrq.cloud/send', json={
                'client_id': client.id,
                'message': delivery.message
            })

            if response.status_code == 200:
                status = 'Sent'
            else:
                status = 'Failed'
        except requests.exceptions.RequestException:
            status = 'Failed'

        message = Message(status=status,
                          delivery_id=delivery.id,
                          client_id=client.id)
        db.session.add(message)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
