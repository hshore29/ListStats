var margin = {top: 40, right: 40, bottom: 30, left: 50},
    width = 500 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse;

var x = d3.time.scale()
    .range([0,width]);
var y = d3.scale.linear()
    .range([height,0]);
var color = d3.scale.category10()
    .domain(["Spams", "Events", "Bros"]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .ticks(d3.time.months,6);

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.count); });

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// load data
d3.json("timeseries.php", function (error, json) {
    if (error) { return console.warn(error); }
    json.forEach(function(d) {
        d.Date = parseDate(d.Date);
    });
    
    var lists = color.domain().map(function(name) {
        return {
            name: name,
            values: json.map(function(d) {
                return {date: d.Date, count: +d[name] || 0};
            })
        };
    });
    
    x.domain(d3.extent(json, function(d){return d.Date;}));
    y.domain([0,d3.max(lists, function(c){return d3.max(c.values,function(v){return v.count;});})]);
    
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text("Listserv Volume")
    
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Emails per Month");
    
    var serv = svg.selectAll(".serv")
        .data(lists)
        .enter().append("g")
        .attr("class","serv");
    
    serv.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", function(d) { return color(d.name); });
    
    serv.append("text")
        .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.count+10) + ")"; })
        .attr("x", 3)
        .attr("dy", ".35em")
        .text(function(d) { return d.name; });
});