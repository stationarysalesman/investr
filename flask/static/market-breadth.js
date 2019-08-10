/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-market-breadth',
          function(data, textStatus, jqXHR)
          {
              console.log(data)
              var ctx = document.getElementById('myChart')
              var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: data.sorted_symbols,
                  datasets: [{
                    data: data.sorted_prices,
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
                            labelString: "Change from Previous Close (%)"
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
          
             // populate the table

            var tbody = document.getElementById('stonks-table');
            data.stonks.forEach(populateRow);


            function populateRow(value, index, array){
                var tr = document.createElement('TR');
                var td_sym = document.createElement('TD');
                td_sym.innerHTML = value.Symbol
                tr.appendChild(td_sym)
                var td_name = document.createElement('TD');
                td_name.innerHTML = value.Name
                tr.appendChild(td_name)
                var td_price = document.createElement('TD');
                td_price.innerHTML = value.Price
                tr.appendChild(td_price)
                var td_open = document.createElement('TD');
                td_open.innerHTML = value.OpeningPrice
                tr.appendChild(td_open)
                var td_change = document.createElement('TD');
                td_change.innerHTML = value.ChangeUSD
                tr.appendChild(td_change)
                var td_change_pct = document.createElement('TD');
                td_change_pct.innerHTML = value.ChangePCT
                tr.appendChild(td_change_pct)
                var td_prev_close= document.createElement('TD');
                td_prev_close.innerHTML = value.PreviousClose
                tr.appendChild(td_prev_close)
                var td_market_cap = document.createElement('TD');
                td_market_cap.innerHTML = value.MarketCap
                tr.appendChild(td_market_cap)
                tbody.appendChild(tr)
                
            } 
          }
    ) // end getJSON

}())
