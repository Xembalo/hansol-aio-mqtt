<?php   
    require_once('mysql.inc.php');
    setlocale (LC_TIME, 'de_DE@euro', 'de_DE', 'de', 'ge', 'de_DE.utf8');
?>
<!-- Topbar -->
<nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">

<!-- Sidebar Toggle (Topbar) -->
<button id="sidebarToggleTop" class="btn btn-link d-md-none rounded-circle mr-3">
  <i class="fa fa-bars"></i>
</button>

<!-- Topbar Navbar -->
<ul class="navbar-nav ml-auto">

  <!-- Nav Item - Alerts -->
  <li class="nav-item dropdown no-arrow mx-1">
    <a class="nav-link dropdown-toggle" href="#" id="alertsDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      <i class="fas fa-bell fa-fw"></i>
      <!-- Counter - Alerts -->
      <?php
        $sql = "SELECT * FROM alerts WHERE is_read = 0 ORDER BY date DESC LIMIT 6";
        $statement = $pdo->query($sql); 
        if ($statement->rowCount() > 0 ) {
          ?>      <span class="badge badge-danger badge-counter"><?php echo $statement->rowCount(); ?></span><?php
        }
        ?>
    </a>
    <!-- Dropdown - Alerts -->
    <div class="dropdown-list dropdown-menu dropdown-menu-right shadow animated--grow-in" aria-labelledby="alertsDropdown">
      <h6 class="dropdown-header">
        Nachrichten
      </h6>
      <?php
        foreach ($statement as $row) {?>
      <a class="dropdown-item d-flex align-items-center" href="<?php echo $row["link"]; ?>">
        <div class="mr-3">
          <div class="icon-circle bg-primary">
            <i class="fas <?php echo $row["icon"]; ?> text-white"></i>
          </div>
        </div>
        <div>
          <div class="small text-gray-500"><?php echo strftime("%A, %d. %B %Y %H:%M", strtotime($row["date"]));?> Uhr</div>
          <span class="font-weight-bold"><?php echo $row["message"]; ?></span>
        </div>
      </a><?php            
        }
      ?>
      <a class="dropdown-item text-center small text-gray-500" href="#">Alle Nachrichten anzeigen</a>
    </div>
  </li>
</ul>

</nav>
<!-- End of Topbar -->