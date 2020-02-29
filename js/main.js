// Set leaflet map
var map = new L.map('map', {
          center: new L.LatLng(50,0),
          zoom: 3,
          layers: [
            new L.tileLayer('https://api.mapbox.com/styles/v1/katzbr/ck6gusg4j0jmw1iubdn4yrsn9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1Ijoia2F0emJyIiwiYSI6ImNqOHhmMnBucDIwZm4ycW8ya2d5cHF0cmsifQ.8rcjz0DyWs_ncWfOZ0VwKA')
          ]
    });

// Initialize the SVG layer
map._initPathRoot()

// Setup svg element to work with
var svg = d3.select("#map").select("svg"),
    linklayer = svg.append("g"),
    nodelayer = svg.append("g");

// Load data asynchronosuly
d3.json("assets/nodes.geojson", function(nodes) {
  d3.csv("assets/links.csv", function(links) {

    // Setup spatialsankey object
    var spatialsankey = d3.spatialsankey()
                            .lmap(map)
                            .nodes(nodes.features)
                            .links(links);

    var mouseover = function(d){
      // Get link data for this node
      var nodelinks = spatialsankey.links().filter(function(link){
        return link.source == d.id;
      });

      // Add data to link layer
      var beziers = linklayer.selectAll("path").data(nodelinks);
      link = spatialsankey.link(options);

      // Draw new links
      beziers.enter()
        .append("path")
        .attr("d", link)
        .attr('id', function(d){return d.id})
        .style("stroke-width", spatialsankey.link().width())
        .style("stroke", "#0080fe");

      // Remove old links
      beziers.exit().remove();

      // Hide inactive nodes
      var circleUnderMouse = this;
      circs.transition().style('opacity',function () {
          return (this === circleUnderMouse) ? 0.7 : 0;
      });
    };

    var mouseout = function(d) {
      // Remove links
      linklayer.selectAll("path").remove();
      // Show all nodes
      circs.transition().style('opacity', 0.7);
    };

    var click = function(d){
      // Remove links
      linklayer.selectAll("path").remove();
      // Get link data for this node
      var nodelinks = spatialsankey.links().filter(function(link){
        return link.source == d.id;
      });

      // Add data to link layer
      var beziers = linklayer.selectAll("path").data(nodelinks);
      link = spatialsankey.link(options);

      // Draw new links
      beziers.enter()
        .append("path")
        .attr("d", link)
        .attr('id', function(d){return d.id})
        .style("stroke-width", spatialsankey.link().width())
        .style("stroke", "#0080fe");

      // Remove old links
      beziers.exit().remove();

      // Hide inactive nodes
//      var circleUnderMouse = this;
//      circs.transition().style('opacity',function () {
//          return (this === circleUnderMouse) ? 0.7 : 0;
//      });
    };

    // Draw nodes
    var node = spatialsankey.node()
    var circs = nodelayer.selectAll("circle")
      .data(spatialsankey.nodes())
      .enter()
      .append("circle")
      .attr("cx", node.cx)
      .attr("cy", node.cy)
      .attr("r", node.r)
      .style("fill", node.fill)
      .style("fill", "yellow")
      .attr("opacity", 0.7)
      .on('mouseover', mouseover)
      .on('click', click)
      .on('mouseout', mouseout);

    // Adopt size of drawn objects after leaflet zoom reset
    var zoomend = function(){
        linklayer.selectAll("path").attr("d", spatialsankey.link());

        circs.attr("cx", node.cx)
             .attr("cy", node.cy);
    };

    map.on("zoomend", zoomend);
  });
});
var options = {'use_arcs': false, 'flip': false};
d3.selectAll("input").forEach(function(x){
  options[x.name] = parseFloat(x.value);
})

d3.selectAll("input").on("click", function(){
  options[this.name] = parseFloat(this.value);
});
