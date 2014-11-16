// Function to build wordcloud in d3 -- https://github.com/jasondavies/d3-cloud
function makeCloud(wordlist, htmlid) {
    var fill = d3.scale.category10(),
        fontSize = d3.scale.log().range([10, 100]).domain([ + wordlist[wordlist.length - 1].value || 1, + wordlist[0].value]),
        w = 300,
        h = 300;

    d3.layout.cloud()
      .timeInterval(1)
      .size([w, h])
      .words(wordlist)
      .rotate(function() { return ~~(Math.random() * 1.2) * 90; })
      .font("helvetica")
      .fontSize(function(d) { return fontSize( + d.value); })
      .padding(1)
      .spiral("archimedean")
      .on("end", draw)
      .start();

    function draw(words) {
        d3.select(htmlid).append("svg")
            .attr("width", w)
            .attr("height", h)
          .append("g")
            .attr("transform", "translate(" + w / 2 + ',' + h / 2 + ")")
          .selectAll("text")
            .data(words)
          .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", function(d) { d.font; })
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
              return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) { return d.key; });
  }
}

// Function to count words
var wordSeparators = /[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g,
    discard = /^(@|https?:|\/\/)/,
    stopWords = /^(i|me|my|myself|we|us|our|ours|ourselves|you|your|yours|yourself|yourselves|he|him|his|himself|she|her|hers|herself|it|its|itself|they|them|their|theirs|themselves|what|which|who|whom|whose|this|that|these|those|am|is|are|was|were|be|been|being|have|has|had|having|do|does|did|doing|will|would|should|can|could|ought|i'm|you're|he's|she's|it's|we're|they're|i've|you've|we've|they've|i'd|you'd|he'd|she'd|we'd|they'd|i'll|you'll|he'll|she'll|we'll|they'll|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|doesn't|don't|didn't|won't|wouldn't|shan't|shouldn't|can't|cannot|couldn't|mustn't|let's|that's|who's|what's|here's|there's|when's|where's|why's|how's|a|an|the|and|but|if|or|because|as|until|while|of|at|by|for|with|about|against|between|into|through|during|before|after|above|below|to|from|up|upon|down|in|out|on|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|say|says|said|shall)$/;
    
function parseText(text, max, maxLength, minLength) {
    tags = {};
    var cases = {};
    text.replace(/\s+/g, " ");
    text.split(wordSeparators).forEach(function(word) {
        if (stopWords.test(word.toLowerCase())) 
            return;
        word = word.toLowerCase().replace(/[^\w\s]|_/g, "");
        if (discard.test(word)) 
            return;
        if (word.length > maxLength)
            return;
        if (word.length < minLength)
            return;
        tags[word] = (tags[word] || 0) + 1;
    });
    tags = d3.entries(tags).sort(function(a, b) {
        return b.value - a.value;
    });
    return tags.slice(0, max = Math.min(tags.length, + max));
}

// Function to get data from SQLite, parse data, and pass to wordcloud
function buildCloud(php, htmlid) {
    d3.text(php)
        .header("Content-type", "application/x-www-form-urlencoded")
        .post('', function (error, data) {
            if (error) { return console.warn(error); }
            var text = [];
            JSON.parse(data).forEach(function(d) { text.push(d.text); });
            text = text.join(" ");
            wordlist = parseText(text, 200, 13, 3);
            console.log(wordlist);
            var cloud = makeCloud(wordlist, htmlid);
        });
}

// Drivers
buildCloud('/listservstats/text_data.php', 'div#cloud');