function make_graph(div_name){
    var n = 20; //num samples
    var random = d3.random.normal(0, .2);
    var data = d3.range(n).map(random);

    var margin = {top: 10, right: 10, bottom: 20, left: 40},
    width = 960 - margin.left - margin.right,
    height = 150 - margin.top - margin.bottom;

    var x = d3.scale.linear().domain([0, n - 1]).range([0, width]);
    var y = d3.scale.linear().domain([0, 1]).range([height, 0]);

    var line = d3.svg.line()
        .x(function(d, i) { return x(i); })
        .y(function(d, i) { return y(d); });

    var svg = d3.select("#"+div_name).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.svg.axis().scale(x).orient("bottom"));

    svg.append("g")
        .attr("class", "y axis")
        .call(d3.svg.axis().scale(y).orient("left"));

    var path = svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line);

    var last_data=0;
    {%if endpoint%}
    function get_data(){
        function s(data){
            //console.debug(data);
            last_data=data;}
        //console.debug('getting data from: {{endpoint}}');
        $.ajax({async:false,url:'{{endpoint}}', success:s});
        return last_data;
    }
    {%else%}
    console.debug('missing endpoint.. plotting random data for fun.')
    function get_data(){return random()}
    {%endif%}
    function tick() {

        // push a new data point onto the back
        data.push(get_data());

        // redraw the line, and slide it to the left
        path
            .attr("d", line)
            .attr("transform", null)
            .transition()
            .duration(500)
            .ease("linear")
            .attr("transform", "translate(" + x(-1) + ")")
            .each("end", tick);

        // pop the old data point off the front
        data.shift();

    }
    tick();
}