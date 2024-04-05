import os
from flask import request, json
from app import app
from app.intrusion_detection import start_detection, ssh_brute_force_detection, port_scaning_detection, dns_tunneling_detection
from app.db import DBMethods

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/run_detection/<machine_id>/<int:timeout>')
def run_detection(machine_id, timeout):
    packets = start_detection(machine_id, timeout)
    
    # Primera versión del script 
    attempts = ssh_brute_force_detection(packets)
    open_ports = port_scaning_detection(packets)
    tcp_sources = dns_tunneling_detection(packets)
    

    return json.dumps({
        'ssh_brute_force': {
            'attempts': list(attempts.items())
        },
        'port_scaning': {
            'open_ports': list(open_ports.items())
        },
        'dns_tunneling': {
            'tcp_sources': list(tcp_sources.items())
        }
    }), 200, {'ContentType': 'application/json'}

@app.route('/add_machine/<name>', methods=['POST'])
def add_machine():
    name = request.form.get('name')
    if name:
        db = DBMethods(app)
        db.add_machine(name)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

@app.route('/get_all_machines')
def get_all_machines():
    db = DBMethods(app)
    machines = db.get_all_machines()
    return json.dumps(machines, default=set_default), 200, {'ContentType': 'application/json'}

@app.route('/delete_machine/<int:id>', methods=['DELETE'])
def delete_machine(id):
    db = DBMethods(app)
    machine = db.delete_machine(id)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
