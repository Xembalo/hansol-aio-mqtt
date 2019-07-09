<?php
    require_once('config.inc.php');
    
    $pdo = new PDO('mysql:host=' . $GLOBALS['host'] . ';port=' . $GLOBALS['port'] . ';dbname=' . $GLOBALS['dbname'], $GLOBALS['user'], $GLOBALS['password']);
    if (!$pdo) {
        die('<div class="alert alert-danger" style="margin:1%;">Could not connect to the database. Set Database Username and Password in the file "/how-to/data-from-database.php"</div>');
    }
    
?>

