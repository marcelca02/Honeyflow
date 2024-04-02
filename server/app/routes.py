from flask import Blueprint, render_template


routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/deploy_honeypot')
def deploy_honeypot():
    return render_template('deploy_honeypot.html')