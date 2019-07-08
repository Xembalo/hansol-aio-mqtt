<?php
    require_once('../includes/mysql.inc.php');
    setlocale (LC_TIME, 'de_DE@euro', 'de_DE', 'de', 'ge', 'de_DE.utf8');
    
    //setting header to json
    header('Content-Type: application/json');


    $sql = "SELECT h.date, h.temperature, g.temperature as yesterday FROM logs h LEFT JOIN logs g ON h.date = DATE_ADD(g.date, INTERVAL 1 DAY) WHERE h.date >= DATE_SUB(NOW(),INTERVAL 2 HOUR) ORDER BY h.date";
    $statement = $pdo->query($sql, PDO::FETCH_ASSOC); 
    
    $data = array();
    foreach ($statement as $row) {
        $data[] = $row;
    }

    $statement->closeCursor();

    //now print the data
    print json_encode($data);

?>


