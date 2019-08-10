from flask import Flask
from flask import render_template
from flask_caching import Cache
import sys
sys.path.append('src/')
from FundamentalAnalysis import GetTreasuryYields, GetTreasuryBillRates, GetFederalFundsRates, \
        GetCorporateBondSpread
from TechnicalAnalysis import GetDJIAStonks


config = {
        "DEBUG": True,
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 1800 
        }

application  = Flask(__name__)
application.config.from_mapping(config)
cache = Cache(application)

@application.route("/")
def hello():
    return ";)"


@application.route("/dashboard")
@cache.cached(timeout=1800)
def dashboard():
    return render_template('dashboard.html')

@application.route("/get-yield-curve")
def get_yield_curve():
    return GetTreasuryYields() 

@application.route("/yield-curve")
@cache.cached(timeout=1800)
def yield_curve():
    return render_template('yield-curve.html')

@application.route("/get-bill-rates")
def get_bill_rates():
    return GetTreasuryBillRates()

@application.route("/bill-rates")
@cache.cached(timeout=1800)
def bill_rates():
    return render_template('bill-rates.html')

@application.route("/get-federal-funds")
def get_federal_funds():
    return GetFederalFundsRates()

@application.route("/federal-funds")
@cache.cached(timeout=1800)
def federal_funds():
    return render_template('federal-funds.html')

@application.route("/get-corporate-bonds")
def get_corporate_bonds():
    return GetCorporateBondSpread()

@application.route("/corporate-bonds")
@cache.cached(timeout=1800)
def corporate_bonds():
    return render_template('corporate-bonds.html')

@application.route("/get-market-breadth")
def get_market_breadth():
    return GetDJIAStonks()

@application.route("/market-breadth")
@cache.cached(timeout=1800)
def market_breadth():
    return render_template('market-breadth.html')





if __name__ == "__main__":
    application.run()

