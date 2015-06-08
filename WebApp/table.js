// Function to create a table
function tabulate(data, htmlid, columns) {
    var table = d3.select(htmlid).append("table"),
        thead = table.append("thead"),
        tbody = table.append("tbody");

    // append the header row
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
            .text(function (column) { return column.value; });

    // create a row for each object in the data
    var rows = tbody.selectAll("tr")
        .data(data)
        .enter()
        .append("tr");

    // create a cell in each row for each column
    var cells = rows.selectAll("td")
        .data(function (row) {
            return columns.map(function (column) {
                return {column: column.value, value: row[column.key]};
            });
        })
        .enter()
        .append("td")
        .html(function (d) { return d.value; })
        .attr("class",function (d) { return d.column; });
    return table;
}

// Call the database with query params, html id, and caption
function buildTable(php, query, htmlid, caption, headers) {
    d3.text(php)
        .header("Content-type", "application/x-www-form-urlencoded")
        .post(query, function (error, data) {
            if (error) { return console.warn(error); }
            var newTable = tabulate(JSON.parse(data), htmlid, headers);
            newTable.attr("border-spacing","10px")
                .append("caption").text(caption);
        });
}

// Set PHP paths
var users = "/listservstats/top_users.php",
    threads = "/listservstats/top_threads.php";

// Build top spammer tables
buildTable(users, "len=10&list='Spams'", "td#table3", "Fall '09 to Present",
           [{key:"alias",value:"Spammer"}, {key:"count(date)",value:"Spams"}]);
buildTable(users, "len=10&year=2015&list='Spams'", "td#table1", "2015 to date",
           [{key:"alias",value:"Spammer"}, {key:"count(date)",value:"Spams"}]);
buildTable(users, "len=10&year=2014&list='Spams'", "td#table2", "Last Year (2014)",
           [{key:"alias",value:"Spammer"}, {key:"count(date)",value:"Spams"}]);

// Build top thread tables
buildTable(threads, "len=5&list='Spams'", "td#table6", "Fall '09 to Present",
           [{key:"alias",value:"Spammer"}, {key:"subject",value:"Thread"},
            {key:"fdate",value:"Date"}, {key:"count",value:"Responses"}]);
buildTable(threads, "len=5&year=2015&list='Spams'", "td#table4", "2015 to date",
           [{key:"alias",value:"Spammer"}, {key:"subject",value:"Thread"},
            {key:"fdate",value:"Date"}, {key:"count",value:"Responses"}]);
buildTable(threads, "len=5&year=2014&list='Spams'", "td#table5", "Last Year (2014)",
           [{key:"alias",value:"Spammer"}, {key:"subject",value:"Thread"},
            {key:"fdate",value:"Date"}, {key:"count",value:"Responses"}]);