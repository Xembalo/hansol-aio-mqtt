<?php
    require_once('../includes/mysql.inc.php');
    setlocale (LC_TIME, 'de_DE@euro', 'de_DE', 'de', 'ge', 'de_DE.utf8');
    
    //setting header to json
    header('Content-Type: application/json');


    $sql = "SELECT 
    round(avg(temperature),2) as temperature,
    DATE_FORMAT(if(from_unixtime(round(unix_timestamp(date)/(60*10))*(60*10)) > now() - interval 1 day, from_unixtime(round(unix_timestamp(date)/(60*10))*(60*10)), from_unixtime(round(unix_timestamp(date)/(60*10))*(60*10)) + interval 1 day), '%Y-%m-%dT%T')  as date, 
    round(avg(pv),2) as pv,
    round(avg(demand),2) as demand,
    round(avg(feedin),2) as feedin,
    round(avg(consumption),2) as consumption,
    round(avg(battery_percent),2) as battery_percent,
    if(from_unixtime(round(unix_timestamp(date)/(60*10))*(60*10)) > now() - interval 1 day, 0, 1) as day_before
FROM logs 
WHERE date >= now() - interval 2 day
group by from_unixtime(round(unix_timestamp(date)/(60*10))*(60*10))
ORDER BY logs.date";
    $statement = $pdo->query($sql, PDO::FETCH_ASSOC); 
    
    $data = array();
    foreach ($statement as $row) {
        $data[] = $row;
    }

    $statement->closeCursor();

    //now print the data
    print json_encode($data);

?>