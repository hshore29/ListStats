<?php
$db = new SQLite3("kdr_listserv.db");

$query = <<<SQL
SELECT text FROM text
JOIN messages USING (id)
WHERE listserv = 'Spams' AND date > '2014-05-21'
SQL;

$statement = $db->prepare($query);

$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){
    $data[] = $row;
}

echo json_encode($data);
$db->close();
?>