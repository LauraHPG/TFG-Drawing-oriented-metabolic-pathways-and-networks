function openTab(evt, tabName) {
    // Declare all variables
    var i, tabcontent, tablinks;
  
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  } 

  

console.log(inputGraph.nodes);
// create an array with nodes

var nodes = new vis.DataSet(
    // 
    inputGraph.nodes
);

// create an array with edges
var edges = new vis.DataSet(
    inputGraph.edges
    
);
// create a network
var container = document.getElementById('mynetwork');

// provide the data in the vis format
var data = {
    nodes: nodes,
    edges: edges
};

var options = {
nodes: {
    shape: 'box'
},
edges: {
    smooth: false
},
physics: false,
interaction: {
    // dragNodes: false,// do not allow dragging nodes
    // zoomView: false, // do not allow zooming
    // dragView: false  // do not allow dragging
}
};

// initialize your network!
var network = new vis.Network(container, data, options);

network.on("click", function (params) {
    console.log(params.nodes.length)
    if (params.nodes.length != 0) {

        var nodeIdHeader = document.getElementById("nodeId");
        nodeIdHeader.textContent = params.nodes[0];

    }
// deleteEdgeMode(params.nodes[0]);
// console.log(params)
});

function deleteEdgeMode(nodeId){
    network.deleteSelected();
}