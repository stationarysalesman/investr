/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-market-volatility',
          function(data, textStatus, jqXHR)
          {
              console.log(data)
              var dates = data.dates.slice(data.dates.length - 90, data.dates.length)
              var vix = data.vix.slice(data.vix.length - 90, data.vix.length)
              var macd_26 = data.macd_26.slice(data.macd_26.length - 90, data.macd_26.length)
              var macd_12 = data.macd_12.slice(data.macd_12.length - 90, data.macd_12.length)
              var histogram = data.histogram.slice(data.histogram.length - 90, data.histogram.length)

              var ctx = document.getElementById('myChart')
              var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: dates,
                  datasets: [{
                    data: vix,
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#007bff',
                    borderWidth: 4,
                    pointBackgroundColor: '#007bff'
                  },
                    {
                    data: macd_26,
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#ffa500',
                    borderWidth: 4,
                    pointBackgroundColor: '#ffa500'

                    },
                    {
                    data: macd_12,
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#fbcc7a',
                    borderWidth: 4,
                    pointBackgroundColor: '#fbcc7a'

                    } 
                  ]
                },
                options: {
                  scales: {
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "VIX"
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
               var ctx2 = document.getElementById('myChart2')
              var myChart2 = new Chart(ctx2, {
                type: 'bar',
                data: {
                  labels: dates,
                  datasets: [{
                    data: histogram,
                    backgroundColor: '#007bff',
                    borderColor: '#007bff',
                    borderWidth: 1,
                  }]
                },
                options: {
                  scales: {
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "Histogram"
                        },
                    }],
                      xAxes: [{
                          barPercentage: 1.0,
                          categoryPercentage: 1.0,
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
          
          }
    ) // end getJSON

}())
