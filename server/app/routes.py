import os
import json
from app import app
from app.intrusion_detection import start_detection, ssh_brute_force_detection, port_scaning_detection, dns_tunneling_detection

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
    })
