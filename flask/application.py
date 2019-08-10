from flask import Flask
from flask import render_template
import sys
sys.path.append('src/')
from FundamentalAnalysis import GetTreasuryYields, GetTreasuryBillRates, GetFederalFundsRates, \
        GetCorporateBondSpread
from TechnicalAnalysis import GetDJIAStonks, GetVixMACD, GetMarginDebt


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

@application.route("/get-federal-funds")
def get_federal_funds():
    return GetFederalFundsRates()

@application.route("/federal-funds")
def federal_funds():
    return render_template('federal-funds.html')

@application.route("/get-corporate-bonds")
def get_corporate_bonds():
    return GetCorporateBondSpread()

@application.route("/corporate-bonds")
def corporate_bonds():
    return render_template('corporate-bonds.html')

@application.route("/get-market-breadth")
def get_market_breadth():
    return GetDJIAStonks()

@application.route("/market-breadth")
def market_breadth():
    return render_template('market-breadth.html')

@application.route("/get-market-volatility")
def get_market_volatility():
    return GetVixMACD()

@application.route("/market-volatility")
def market_volatility():
    return render_template('market-volatility.html')

@application.route("/get-margin-debt")
def get_margin_debt():
    return GetMarginDebt()

@application.route("/margin-debt")
def margin_debt():
    return render_template('margin-debt.html')








if __name__ == "__main__":
    application.run()

