/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-bill-rates',
          function(data, textStatus, jqXHR)
          {
              console.log(data)
              var ctx = document.getElementById('myChart')
              var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: [
                    '1 month',
                    '2 month',
                    '3 month',
                    '6 month',
                    '1 year'
                  ],
                  datasets: [{
                    data: data.billrates,
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
                            labelString: "Interest (%)"
                        },
                      ticks: {
                        beginAtZero: false
                      }
                    }],
                      xAxes: [{
                          scaleLabel: {
                              display: true,
                              labelString: "Time to Maturity"
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
