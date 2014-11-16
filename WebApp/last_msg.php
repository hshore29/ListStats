<?php
$db = new SQLite3("kdr_listserv.db");

$query = <<<SQL
SELECT subject, snippet FROM messages
JOIN id_lookup USING (sender)
WHERE netid = {$_POST['netid']}
ORDER BY date DESC LIMIT 1
SQL;

$statement = $db->prepare($query);

$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){
    $data[] = $row;
}

echo json_encode($data);
$db->close();
?>