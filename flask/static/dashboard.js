/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-dashboard',
          function(data, textStatus, jqXHR)
          {
              var sp_dates = data.sp_dates
              var sp_prices = data.sp_prices
              var yields = data.yields
              var yield_date = data.yield_date
              var stonks = data.advancing_stonks
              var bill_rates = data.bill_rates
              var advancing_stonks = data.advancing_stonks
              console.log(data)
              var ctx = document.getElementById('myChart')
              var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: sp_dates,
                  datasets: [{
                    data: sp_prices,
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#007bff',
                    borderWidth: 4,
                    pointBackgroundColor: '#007bff'
                  }]
                },
                options: {
                  scales: {
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "S&P 500 Closing Price (USD)"
                        },
                      ticks: {
                        beginAtZero: false
                      }
                    }],
                      xAxes: [{
                          scaleLabel: {
                              display: true,
                              labelString: "Date"
                          }
                      }]
                  },
                  legend: {
                    display: false
                  }
                }
              }) //end chart
            // A few other metrics
            var sp_10yr3mo = document.getElementById('spread-10yr3mo');
            sp_10yr3mo.innerHTML = yields[9] - yields[2];
            var sp_30yr10yr = document.getElementById('spread-30yr10yr');
            sp_30yr10yr.innerHTML = yields[11] - yields[9];
            var x = bill_rates[0]
            var y = bill_rates.slice(1, bill_rates.length)
            var monotonic = true
            y.forEach(monotonicityCheck)
            var money_market = document.getElementById('money-market')
            money_market.innerHTML = (monotonic) ? "Normal" : "Abnormal"

            var note10yr = document.getElementById('note-10yr')
            note10yr.innerHTML = yields[9]
            var advancing_stonks_elem = document.getElementById('djia-stocks')
            advancing_stonks_elem.innerHTML = advancing_stonks


            function monotonicityCheck(value, index, array){
                if (value < x)
                    monotonic = false
                x = value
            }
          }
    ) // end getJSON

}())
