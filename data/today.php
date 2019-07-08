<?php
    require_once('../includes/mysql.inc.php');
    setlocale (LC_TIME, 'de_DE@euro', 'de_DE', 'de', 'ge', 'de_DE.utf8');
    
    //setting header to json
    header('Content-Type: application/json');


    $sql = "SELECT temperature, date, pv, demand, feedin, consumption, battery_percent FROM logs WHERE date >= curdate() ORDER BY date";
    $statement = $pdo->query($sql, PDO::FETCH_ASSOC); 
    
    $data = array();
    foreach ($statement as $row) {
        $data[] = $row;
    }

    $statement->closeCursor();

    //now print the data
    print json_encode($data);

?>