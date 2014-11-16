<?php
$db = new SQLite3("kdr_listserv.db");

$query = <<<SQL
SELECT s.Date,s.Month,s.Spams,e.Events,b.Bros FROM
(SELECT max(date(date)) AS 'Date', strftime('%Y-%m',date) AS 'Month', count(subject) AS 'Spams'
FROM messages WHERE listserv='Spams' GROUP BY strftime('%Y-%m',date) ORDER BY Month) AS s
LEFT JOIN
(SELECT max(date(date)) AS 'Date', strftime('%Y-%m',date) AS 'Month', count(subject) AS 'Events'
FROM messages WHERE listserv='Events' GROUP BY strftime('%Y-%m',date)) AS e USING (Month)
LEFT JOIN
(SELECT max(date(date)) AS 'Date', strftime('%Y-%m',date) AS 'Month', count(subject) AS 'Bros'
FROM messages WHERE listserv='Bros' GROUP BY strftime('%Y-%m',date)) AS b USING (Month)
SQL;

$statement = $db->prepare($query);

$results = $statement->execute();
while($row = $results->fetchArray(SQLITE3_ASSOC) ){
    $data[] = $row;
}

echo json_encode($data);
$db->close();
?>