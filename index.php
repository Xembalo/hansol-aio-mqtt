<?php
  include("includes/nav.inc.php");
?>

    <!-- Content Wrapper -->
    <div id="content-wrapper" class="d-flex flex-column">

      <!-- Main Content -->
      <div id="content">

        <?php
          include("includes/topbar.inc.php");

          $sql = "SELECT * FROM logs ORDER BY date DESC LIMIT 1";
          $row = $pdo->query($sql)->fetch(); 
        ?>

        <!-- Begin Page Content -->
        <div class="container-fluid">

          <!-- Page Heading -->
          <div class="d-sm-flex align-items-center justify-content-between mb-4">
            <h1 class="h3 mb-0 text-gray-800">Dashboard</h1>
            <div class="d-none d-sm-inline-block">Daten von <?php echo strftime("%A, %d. %B %Y %H:%M", strtotime($row["date"]));?> Uhr</div>
            <a href="javascript:window.location.reload(true)" class="d-none d-sm-inline-block btn btn-sm btn-primary shadow-sm"><i class="fas fa-sync alt fa-sm text-white-50"></i> Aktualisieren</a>
            
          </div>


          <!-- Content Row -->
          <div class="row">

            <!-- Temperature -->
            <?php
              switch(true) {
                case ($row["temperature"] < 30):
                  $icon = "thermometer-empty";
                  $color = "teal";
                  break;
                case ($row["temperature"] < 34):
                  $icon = "thermometer-quarter";
                  $color = "teal";
                  break;
                case ($row["temperature"] < 38):
                  $icon = "thermometer-half";
                  $color = "yellow";
                  break;
                case ($row["temperature"] < 42):
                  $icon = "thermometer-three-quarters";
                  $color = "orange";
                  break;
                default:
                  $icon = "thermometer-full";
                  $color = "red";
              }
              ?>

            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-<?php echo $color; ?> shadow h-100 py-2">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Temperatur</div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $row["temperature"]; ?>°C</div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-<?php echo $icon; ?> fa-3x text-<?php echo $color; ?>"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Batterie -->
            <?php
              switch(true) {
                case ($row["battery_percent"] <= 10):
                  $icon = "battery-empty";
                  $color = "red";
                  break;
                case ($row["battery_percent"] <= 45):
                  $icon = "battery-quarter";
                  $color = "red";
                  break;
                case ($row["battery_percent"] <= 65):
                  $icon = "battery-half";
                  $color = "orange";
                  
                  break;
                case ($row["battery_percent"] < 90):
                  $icon = "battery-three-quarters";
                  $color = "yellow";
                  break;
                default:
                  $icon = "battery-full";
                  $color = "teal";
              }
              ?>


            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-<?php echo $color; ?> shadow h-100 py-2">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Akkuladung</div>
                      <div class="row no-gutters align-items-center">
                        <div class="col-auto">
                          <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800"><?php echo $row["battery_percent"]; ?>%</div>
                        </div>
                        <div class="col">
                          <div class="progress progress-sm mr-2">
                            <div class="progress-bar bg-info progress-bar-striped progress-bar-animated" role="progressbar" style="width: <?php echo $row["battery_percent"]; ?>%" aria-valuenow="<?php echo $row["battery_percent"]; ?>" aria-valuemin="0" aria-valuemax="100"></div>
                          </div>
                        </div>
                      </div>                      
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-<?php echo $icon; ?> fa-3x text-<?php echo $color; ?>"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Photovoltaik -->
            <div class="col-xl-2 col-md-6 mb-4">
              <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Solarstrom</div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $row["pv"]; ?> kW</div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-solar-panel fa-2x text-gray-300"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Stromverbrauch -->
            <div class="col-xl-2 col-md-6 mb-4">
              <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Verbrauch</div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $row["consumption"]; ?> kW</div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-cog fa-2x text-gray-300"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Netz -->
            <div class="col-xl-2 col-md-6 mb-4">
              <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Netz</div>
                      <div class="h6 mb-0 font-weight-bold text-gray-800"><?php echo $row["demand"]; ?> kW</div> Abnahme
                      <div class="h6 mb-0 font-weight-bold text-gray-800"><?php echo $row["feedin"]; ?> kW</div> Einspeisung
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-bolt fa-2x text-gray-300"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-xl-12 col-lg-7">
              <div class="card shadow mb-4">
                <div class="card-header py-3">
                  <h6 class="m-0 font-weight-bold text-primary">Stromflüsse und Batterie</h6>
                </div>
                <div class="card-body">
                  <div class="chart-area">
                    <canvas id="PowerChart"></canvas>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-xl-12 col-lg-7">
              <div class="card shadow mb-4">
                <div class="card-header py-3">
                  <h6 class="m-0 font-weight-bold text-primary">Temperatur</h6>
                </div>
                <div class="card-body">
                  <div class="chart-area">
                    <canvas id="BatteryChart"></canvas>
                  </div>
                </div>
              </div>
            </div>
          </div>
    

        </div>
        <!-- /.container-fluid -->

      </div>
      <!-- End of Main Content -->


    </div>
    <!-- End of Content Wrapper -->

  </div>
  <!-- End of Page Wrapper -->

  <!-- Scroll to Top Button-->
  <a class="scroll-to-top rounded" href="#page-top">
    <i class="fas fa-angle-up"></i>
  </a>

  <!-- Bootstrap core JavaScript-->
  <script src="vendor/jquery/jquery.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

  <!-- Core plugin JavaScript-->
  <script src="vendor/jquery-easing/jquery.easing.min.js"></script>

  <!-- Custom scripts for all pages-->
  <script src="js/sb-admin-2.min.js"></script>

  <!-- Page level plugins -->

  <script src="vendor/chart.js/chart.js"></script>
  <script src="vendor/chart.js/luxon.js"></script>
  <script src="vendor/chart.js/chartjs-adapter-date-luxon.js"></script>

  <script>

let width, height, gradient;
function getTemperatureGradient(ctx, chartArea) {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  console.log (chartArea.bottom);
  console.log (chartArea.top);
  console.log (chartHeight);
  
  if (gradient === null || width !== chartWidth || height !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    width = chartWidth;
    height = chartHeight;
    gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, "#17a2b8");
    gradient.addColorStop(0.5, "#ffc107");
    gradient.addColorStop(1, "#dc3545");
  }

  return gradient;
}



$(document).ready(function(){
  $.ajax({
    url: "data/last_24hrs.php",
    method: "GET",
    success: function(data) {
      var minute = [];
      var demand = [];
      var feedin = [];
      var pv = [];
      var consumption = [];
      var temperature = [];
      var battery = [];
      var demand_bf = [];
      var feedin_bf = [];
      var pv_bf = [];
      var consumption_bf = [];
      var temperature_bf = [];
      var battery_bf = [];      
      //luxon.Settings.defaultZone = "Europe/Berlin";
      for(var i in data) {
        if (data[i].day_before == 0) {
          minute.push(luxon.DateTime.fromISO(data[i].date));
          demand.push(data[i].demand);
          feedin.push(data[i].feedin);
          pv.push(data[i].pv);
          consumption.push(data[i].consumption);
          temperature.push(data[i].temperature);
          battery.push(data[i].battery_percent);
        } else {
          demand_bf.push(data[i].demand);
          feedin_bf.push(data[i].feedin);
          pv_bf.push(data[i].pv);
          consumption_bf.push(data[i].consumption);
          temperature_bf.push(data[i].temperature);
          battery_bf.push(data[i].battery_percent);
        }
      }
 
      const ctx = document.getElementById('BatteryChart');
      const myChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: minute,
            datasets: [
              {
                label: "Temperatur",
                data: temperature,
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                pointRadius: 0,
                yAxisID: 'y',
                borderColor: "#fd7e14"
                /*borderColor: function(context) {
                  const chart = context.chart;
                  const {ctx, chartArea} = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return null;
                  }
                  return getTemperatureGradient(ctx, chartArea);
                }*/
              },{
                label: "Temperatur Vortag",
                data: temperature_bf,
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                pointRadius: 0,
                yAxisID: 'y',
                borderWidth: 1,
                borderColor: "rgba(32, 201, 151, 0.7)"
              }
            ]
          },
          options: {
            zone: "Europe/Berlin",
            responsive: true,
            interaction: {
              mode: 'index',
              intersect: false,
            },
            plugins: {
              legend: {
                display: false
              }
            },
            stacked: false,
            scales: {
              x: {
                type: 'time',
                time: {
                  // Luxon format string
                  tooltipFormat: 'DD T'
                },
                title: {
                  display: true,
                  text: 'Date'
                }
              },              
              y: {
                gridLines: {
                  color: "rgb(234, 236, 244)",
                  zeroLineColor: "rgb(234, 236, 244)",
                  drawBorder: false,
                  borderDash: [2],
                  zeroLineBorderDash: [2]
                },
                title: {
                  display: true,
                  text: '°C'
                }
              }
            }
          },
        }
      );

      const ctp = document.getElementById('PowerChart');
      var myLineChart = new Chart(ctp, {
        type: 'line',
        data: {
          labels: minute,
          datasets: [{
            label: "Abruf",
            lineTension: 1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "red",
            borderWidth: 1,
            pointRadius: 0,
            data: demand,
            yAxisID: 'y'
          },{
            label: "PV",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "yellow",
            borderWidth: 1,
            pointRadius: 0,
            data: pv,
            yAxisID: 'y'
          },{
            label: "Einspeisung",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "blue",
            borderWidth: 1,
            pointRadius: 0,
            data: feedin,
            yAxisID: 'y'
          },{
            label: "Verbrauch",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "orange",
            borderWidth: 1,
            pointRadius: 0,
            data: consumption,
            yAxisID: 'y'
          },{
            label: "Batterie",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "lime",
            borderWidth: 1,
            pointRadius: 0,
            data: battery,
            yAxisID: 'y1'
          }]
        },
        options: {
          maintainAspectRatio: false,
          layout: {
            padding: {
              left: 10,
              right: 25,
              top: 25,
              bottom: 0
            }
          },
          scales: {
            x: {
              type: 'time',
              time: {
                // Luxon format string
                tooltipFormat: 'DD T'
              },
              title: {
                display: true,
                text: 'Date'
              }
            },
            y: {
              id: 'kw',
              position: 'left',
              gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              },
              title: {
                display: true,
                text: 'kW'
              }
            },
            y1: {
              id: 'per',
              position: 'right',
              gridLines: {
                color: "rgb(234, 0, 244)",
                zeroLineColor: "rgb(234, 0, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              },
              title: {
                display: true,
                text: '%'
              }
            }
          },
          legend: {
            display: true
          }
        }
      });
    }
  });
});

</script>

</body>

</html>
