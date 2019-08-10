from flask import Flask
from flask import render_template
import sys
sys.path.append('src/')
from YieldCurve import GetTreasuryYields, GetTreasuryBillRates
application  = Flask(__name__)

@application.route("/")
def hello():
    return ";)"


@application.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@application.route("/get-yield-curve")
def get_yield_curve():
    return GetTreasuryYields() 

@application.route("/yield-curve")
def yield_curve():
    return render_template('yield-curve.html')

@application.route("/get-bill-rates")
def get_bill_rates():
    return GetTreasuryBillRates()

@application.route("/bill-rates")
def bill_rates():
    return render_template('bill-rates.html')



if __name__ == "__main__":
    application.run()

