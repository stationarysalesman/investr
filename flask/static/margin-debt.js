/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-margin-debt',
          function(data, textStatus, jqXHR)
          {
              console.log(data)
              var ctx = document.getElementById('myChart')
              var myChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: data.dates,
                  datasets: [{
                    data: data.debts,
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
                            labelString: "Margin Debt ($ Millions)"
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
         
          }
    ) // end getJSON

}())
