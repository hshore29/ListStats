<?php
$db = new SQLite3("kdr_listserv.db");
    
$query = "SELECT alias,count(date) FROM messages JOIN id_lookup USING (sender)";

if (array_key_exists('list',$_POST)) {
    $query .= " WHERE listserv = " . $_POST['list'];
    if (array_key_exists('year',$_POST)) {
        $query .= " AND strftime('%Y',date)='" . $_POST['year'] . "'";
    }
} elseif (array_key_exists('year',$_POST)) {
    $query .= " WHERE strftime('%Y',date)='" . $_POST['year'] . "'";
}

$query .= " GROUP BY netid ORDER BY count(date) DESC";

if (array_key_exists('len',$_POST)) { $query .= " LIMIT " . $_POST['len']; }

$statement = $db->prepare($query);

$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){
    $data[] = $row;
}

echo json_encode($data);
$db->close();
?>