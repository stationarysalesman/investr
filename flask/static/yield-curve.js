/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  $.getJSON('get-yield-curve',
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
                    '1 year',
                    '2 year',
                    '3 year',
                    '5 year',
                    '7 year',
                    '10 year',
                    '20 year',
                    '30 year'
                  ],
                  datasets: [{
                    data: data.yields,
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
                            labelString: "Yield (%)"
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
            // A few other metrics
            var sp_10yr30yr = document.getElementById('spread-10yr3mo');
            sp_10yr30yr.innerHTML = data.yields[9] - data.yields[2];
            var sp_30yr10yr = document.getElementById('spread-30yr20yr');
            sp_30yr10yr.innerHTML = data.yields[11] - data.yields[9];


          }
    ) // end getJSON

}())
