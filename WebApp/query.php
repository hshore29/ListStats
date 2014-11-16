<?php
$db = new SQLite3("kdr_listserv.db");
$statement = $db->prepare($_POST['query']);
$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){ $data[] = $row; }
echo json_encode($data);
$db->close();
?>