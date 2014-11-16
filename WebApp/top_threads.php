<?php
$db = new SQLite3("kdr_listserv.db");
    
$query = "SELECT alias, subject, strftime('%m/%d/%Y',date) AS fdate, count FROM messages JOIN (SELECT metaThread, count(*) AS count FROM messages GROUP BY metaThread) AS t ON t.metaThread = messages.id";

if (array_key_exists('list',$_POST)) {
    $query .= " WHERE listserv = " . $_POST['list'];
    if (array_key_exists('year',$_POST)) {
        $query .= " AND strftime('%Y',date)='" . $_POST['year'] . "'";
    }
} elseif (array_key_exists('year',$_POST)) {
    $query .= " WHERE strftime('%Y',date)='" . $_POST['year'] . "'";
}

$query .= " ORDER BY count DESC";

if (array_key_exists('len',$_POST)) { $query .= " LIMIT " . $_POST['len']; }

$statement = $db->prepare($query);

$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){
    $data[] = $row;
}

echo json_encode($data);
$db->close();
?>