import os
import json
from app import app
from intrusion-detection import start_detection

@app.route('/')
def hello():
    return "Hello, World!"

# @app.route('/start_detection/:<int:machine_id>/:<int:timeout>')
# def start_detection(machine_id, timeout):
#     packets = start_detection(machine_id, timeout)


    


