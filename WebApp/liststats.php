<?
session_start();
if($_SESSION['isloggedin'] != true){
	header("Location: index.php?redir=".str_replace("/intraweb/","",$_SERVER["REQUEST_URI"]));
	exit;
}
require_once("resources/db.php");
include("resources/security.php");

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>list serve statistics | kdr intraweb</title>
<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
<link rel="stylesheet" href="styles/default.css" type="text/css" media="screen,projection" />
<link rel="stylesheet" href="listservstats/chart.css" type="text/css" />
</head>

<body>
<div id="container" >

<div id="header">
<div id="hleft">
<h1>intraweb</h1>
<h2>kdrcornell.com</h2>
</div>
<div id="hright">
<? include('includes/rnav.php'); ?>
</div>
</div>

<div id="navigation">
<? include('includes/nav.php'); ?>
</div>

<div id="content">
    <h2>List Serve Stats (Fall '09 - Present)</h2>
    <div id="date"></div>
    <table id="toplists">
        <tr><td id="table1"></td><td id="table2"></td><td id="table3"></td></tr>
    </table>
    <table id="toplists">
        <tr><td id="table4"></td></tr>
        <tr><td id="table6"></td></tr>
    </table>
    <div id="chart"></div>
    <div id="cloud"><h3>2014 - Present Spam Cloud</h3></div>
    <div>
        <h3>Your latest spam:</h3>
        <div id="title"></div>
        <div id="body"></div>
    </div>
    <script type="text/javascript" src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
    <script type="text/javascript" src="/listservstats/d3.layout.cloud.js"></script>
    <script type="text/javascript" src="/listservstats/colorbrewer.js"></script>
    <script type="text/javascript" src="/listservstats/table.js"></script>
    <script type="text/javascript" src="/listservstats/chart.js"></script>
    <script type="text/javascript" src="/listservstats/wordcloud.js"></script>
    <script type="text/javascript">
        d3.text("/listservstats/query.php")
            .header("content-type", "application/x-www-form-urlencoded")
            .post("query=SELECT strftime('%m/%d/%Y',date) AS fdate FROM messages ORDER BY date DESC LIMIT 1",
                  function (error, data) {
                      if (error) { return console.warn(error); }
                      console.log(data);
                      data = JSON.parse(data);
                      var text = "Last updated on: " + data[0]['fdate']
                      d3.select("div#date").text(text);
                  });
        d3.text("/listservstats/last_msg.php")
            .header("Content-type", "application/x-www-form-urlencoded")
            .post("netid='<?=$_SESSION['netid'];?>'", function (error, data) {
                if (error) { return console.warn(error); }
                data = JSON.parse(data);
                d3.select("div#title").append("strong").html(data[0]['subject']);
                d3.select("div#body").html(data[0]['snippet'] + "...");
            });
    </script>
</div>

<div id="footer">
<? include('includes/footer.php'); ?>
</div>

</div>
</body>
</html>