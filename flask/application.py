from flask import Flask
from flask import render_template

application  = Flask(__name__)

@application.route("/")
def hello():
    return ";)"


@application.route("/dashboard")
def yeet():
    return render_template('dashboard.html')

@application.route("/yield-curve")
def yeet2():
    return render_template('yield-curve.html')


if __name__ == "__main__":
    application.run()

