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

          <!-- Content Row -->

          <div class="row">

            <!-- Area Chart -->
            <div class="col-xl-8 col-lg-7">
              <div class="card shadow mb-4">
                <!-- Card Header - Dropdown -->
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                  <h6 class="m-0 font-weight-bold text-primary">Temperatur</h6>
                  <div class="dropdown no-arrow">
                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                    </a>
                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownMenuLink">
                      <div class="dropdown-header">Dropdown Header:</div>
                      <a class="dropdown-item" href="#">Action</a>
                      <a class="dropdown-item" href="#">Another action</a>
                      <div class="dropdown-divider"></div>
                      <a class="dropdown-item" href="#">Something else here</a>
                    </div>
                  </div>
                </div>
                <!-- Card Body -->
                <div class="card-body">
                  <div class="chart-area">
                    <canvas id="myAreaChart"></canvas>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pie Chart -->
            <div class="col-xl-4 col-lg-5">
              <div class="card shadow mb-4">
                <!-- Card Header - Dropdown -->
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                  <h6 class="m-0 font-weight-bold text-primary">Revenue Sources</h6>
                  <div class="dropdown no-arrow">
                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                    </a>
                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownMenuLink">
                      <div class="dropdown-header">Dropdown Header:</div>
                      <a class="dropdown-item" href="#">Action</a>
                      <a class="dropdown-item" href="#">Another action</a>
                      <div class="dropdown-divider"></div>
                      <a class="dropdown-item" href="#">Something else here</a>
                    </div>
                  </div>
                </div>
                <!-- Card Body -->
                <div class="card-body">
                  <div class="chart-pie pt-4 pb-2">
                    <canvas id="myBatLast"></canvas>
                  </div>
                  <div class="mt-4 text-center small">
                    <span class="mr-2">
                      <i class="fas fa-circle text-primary"></i> Direct
                    </span>
                    <span class="mr-2">
                      <i class="fas fa-circle text-success"></i> Social
                    </span>
                    <span class="mr-2">
                      <i class="fas fa-circle text-info"></i> Referral
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>


          <div class="row">

            <!-- Area Chart -->
            <div class="col-xl-8 col-lg-7">
              <div class="card shadow mb-4">
                <!-- Card Header - Dropdown -->
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                  <h6 class="m-0 font-weight-bold text-primary">Stromflüsse und Batterie</h6>
                  <div class="dropdown no-arrow">
                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                    </a>
                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownMenuLink">
                      <div class="dropdown-header">Dropdown Header:</div>
                      <a class="dropdown-item" href="#">Action</a>
                      <a class="dropdown-item" href="#">Another action</a>
                      <div class="dropdown-divider"></div>
                      <a class="dropdown-item" href="#">Something else here</a>
                    </div>
                  </div>
                </div>
                <!-- Card Body -->
                <div class="card-body">
                  <div class="chart-area">
                    <canvas id="myPowerChart"></canvas>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pie Chart -->
            <div class="col-xl-4 col-lg-5">
              <div class="card shadow mb-4">
                <!-- Card Header - Dropdown -->
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                  <h6 class="m-0 font-weight-bold text-primary">Revenue Sources</h6>
                  <div class="dropdown no-arrow">
                    <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                    </a>
                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownMenuLink">
                      <div class="dropdown-header">Dropdown Header:</div>
                      <a class="dropdown-item" href="#">Action</a>
                      <a class="dropdown-item" href="#">Another action</a>
                      <div class="dropdown-divider"></div>
                      <a class="dropdown-item" href="#">Something else here</a>
                    </div>
                  </div>
                </div>
                <!-- Card Body -->
                <div class="card-body">
                  <div class="chart-pie pt-4 pb-2">
                    <canvas id="myPieChart"></canvas>
                  </div>
                  <div class="mt-4 text-center small">
                    <span class="mr-2">
                      <i class="fas fa-circle text-primary"></i> Direct
                    </span>
                    <span class="mr-2">
                      <i class="fas fa-circle text-success"></i> Social
                    </span>
                    <span class="mr-2">
                      <i class="fas fa-circle text-info"></i> Referral
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Content Row -->
          <div class="row">

            <!-- Content Column -->
            <div class="col-lg-6 mb-4">

              <!-- Project Card Example -->
              <div class="card shadow mb-4">
                <div class="card-header py-3">
                  <h6 class="m-0 font-weight-bold text-primary">Projects</h6>
                </div>
                <div class="card-body">
                  <h4 class="small font-weight-bold">Server Migration <span class="float-right">20%</span></h4>
                  <div class="progress mb-4">
                    <div class="progress-bar bg-danger" role="progressbar" style="width: 20%" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <h4 class="small font-weight-bold">Sales Tracking <span class="float-right">40%</span></h4>
                  <div class="progress mb-4">
                    <div class="progress-bar bg-warning" role="progressbar" style="width: 40%" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <h4 class="small font-weight-bold">Customer Database <span class="float-right">60%</span></h4>
                  <div class="progress mb-4">
                    <div class="progress-bar" role="progressbar" style="width: 60%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <h4 class="small font-weight-bold">Payout Details <span class="float-right">80%</span></h4>
                  <div class="progress mb-4">
                    <div class="progress-bar bg-info" role="progressbar" style="width: 80%" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <h4 class="small font-weight-bold">Account Setup <span class="float-right">Complete!</span></h4>
                  <div class="progress">
                    <div class="progress-bar bg-success" role="progressbar" style="width: 100%" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </div>
              </div>

              <!-- Color System -->
              <div class="row">
                <div class="col-lg-6 mb-4">
                  <div class="card bg-primary text-white shadow">
                    <div class="card-body">
                      Primary
                      <div class="text-white-50 small">#4e73df</div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6 mb-4">
                  <div class="card bg-success text-white shadow">
                    <div class="card-body">
                      Success
                      <div class="text-white-50 small">#1cc88a</div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6 mb-4">
                  <div class="card bg-info text-white shadow">
                    <div class="card-body">
                      Info
                      <div class="text-white-50 small">#36b9cc</div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6 mb-4">
                  <div class="card bg-warning text-white shadow">
                    <div class="card-body">
                      Warning
                      <div class="text-white-50 small">#f6c23e</div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6 mb-4">
                  <div class="card bg-danger text-white shadow">
                    <div class="card-body">
                      Danger
                      <div class="text-white-50 small">#e74a3b</div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-6 mb-4">
                  <div class="card bg-secondary text-white shadow">
                    <div class="card-body">
                      Secondary
                      <div class="text-white-50 small">#858796</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <div class="col-lg-6 mb-4">

              <!-- Illustrations -->
              <div class="card shadow mb-4">
                <div class="card-header py-3">
                  <h6 class="m-0 font-weight-bold text-primary">Illustrations</h6>
                </div>
                <div class="card-body">
                  <div class="text-center">
                    <img class="img-fluid px-3 px-sm-4 mt-3 mb-4" style="width: 25rem;" src="img/undraw_posting_photo.svg" alt="">
                  </div>
                  <p>Add some quality, svg illustrations to your project courtesy of <a target="_blank" rel="nofollow" href="https://undraw.co/">unDraw</a>, a constantly updated collection of beautiful svg images that you can use completely free and without attribution!</p>
                  <a target="_blank" rel="nofollow" href="https://undraw.co/">Browse Illustrations on unDraw &rarr;</a>
                </div>
              </div>

              <!-- Approach -->
              <div class="card shadow mb-4">
                <div class="card-header py-3">
                  <h6 class="m-0 font-weight-bold text-primary">Development Approach</h6>
                </div>
                <div class="card-body">
                  <p>SB Admin 2 makes extensive use of Bootstrap 4 utility classes in order to reduce CSS bloat and poor page performance. Custom CSS classes are used to create custom components and custom utility classes.</p>
                  <p class="mb-0">Before working with this theme, you should become familiar with the Bootstrap framework, especially the utility classes.</p>
                </div>
              </div>

            </div>
          </div>

        </div>
        <!-- /.container-fluid -->

      </div>
      <!-- End of Main Content -->

      <!-- Footer -->
      <footer class="sticky-footer bg-white">
        <div class="container my-auto">
          <div class="copyright text-center my-auto">
            <span>Copyright &copy; Your Website 2019</span>
          </div>
        </div>
      </footer>
      <!-- End of Footer -->

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
  <script src="vendor/chart.js/Chart.bundle.min.js"></script>

  <!-- Page level custom scripts -->
  
 <!-- <script src="js/demo/chart-pie-demo.js"></script>-->


  <script>
    // Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


$(document).ready(function(){
  $.ajax({
    url: "data/today.php",
    method: "GET",
    success: function(data) {
      
      var minute = [];
      var demand = [];
      var feedin = [];
      var pv = [];
      var consumption = [];
      var temperature = [];
      var battery = [];

      for(var i in data) {
        minute.push(data[i].date);
        demand.push(data[i].demand);
        feedin.push(data[i].feedin);
        pv.push(data[i].pv);
        consumption.push(data[i].consumption);
        temperature.push(data[i].temperature);
        battery.push(data[i].battery_percent);
      }


// Area Chart Example
      var ctx = document.getElementById("myAreaChart");
      var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: minute,
          datasets: [{
            label: "Temperatur",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(78, 115, 223, 1)",
            pointRadius: 0,
            data: temperature
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
            xAxes: [{
                type: "time",
                time: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    unit: 'minute',
                    displayFormats: {
                      minute: 'H:mm'
                    }
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                }
            }],
            yAxes: [{
              gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              }
            }]
          },
          legend: {
            display: false
          }
        }
      });


      // Area Chart Example
      var ctx = document.getElementById("myPowerChart");
      var myLineChart = new Chart(ctx, {
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
            yAxisID: 'kw'
          },{
            label: "PV",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "yellow",
            borderWidth: 1,
            pointRadius: 0,
            data: pv,
            yAxisID: 'kw'
          },{
            label: "Einspeisung",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "blue",
            borderWidth: 1,
            pointRadius: 0,
            data: feedin,
            yAxisID: 'kw'
          },{
            label: "Verbrauch",
            lineTension: 0.1,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "orange",
            borderWidth: 1,
            pointRadius: 0,
            data: consumption,
            yAxisID: 'kw'
          },{
            label: "Batterie",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "lime",
            borderWidth: 1,
            pointRadius: 0,
            data: battery,
            yAxisID: 'per'
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
            xAxes: [{
                type: "time",
                time: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    unit: 'minute',
                    displayFormats: {
                      minute: 'H:mm'
                    }
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                }
            }],
            yAxes: [{
              id: 'kw',
              position: 'left',
              gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              }
            },{
              id: 'per',
              position: 'right',
              gridLines: {
                color: "rgb(234, 0, 244)",
                zeroLineColor: "rgb(234, 0, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              }
            }]
          },
          legend: {
            display: true
          }
        }
      });
    }
  });
});


$(document).ready(function(){
  $.ajax({
    url: "data/bat.php",
    method: "GET",
    success: function(data) {
      
      var minute = [];
      var temperature = [];
      var yesterday = [];

      for(var i in data) {
        minute.push(data[i].date);
        temperature.push(data[i].temperature);
        yesterday.push(data[i].yesterday);
      }


// Area Chart Example
      var ctx = document.getElementById("myBatLast");
      var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: minute,
          datasets: [{
            label: "Temperatur",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(78, 115, 223, 1)",
            pointRadius: 0,
            data: temperature
          },{
            label: "Gestern",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(115, 115, 115, 1)",
            pointRadius: 0,
            data: yesterday
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
            xAxes: [{
                type: "time",
                time: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    unit: 'minute',
                    displayFormats: {
                      minute: 'H:mm'
                    }
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                }
            }],
            yAxes: [{
              gridLines: {
                color: "rgb(234, 236, 244)",
                zeroLineColor: "rgb(234, 236, 244)",
                drawBorder: false,
                borderDash: [2],
                zeroLineBorderDash: [2]
              }
            }]
          },
          legend: {
            display: false
          }
        }
      });
    }
  });
});
</script>

</body>

</html>
