from flask import Flask

app = Flask(__name__)


if __name__ == '__main__':

    from routes import routes
    app.register_blueprint(routes, url_prefix='/')


    app.run(debug=True)
