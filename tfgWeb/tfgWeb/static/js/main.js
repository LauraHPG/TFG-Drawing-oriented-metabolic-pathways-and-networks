console.log(inputGraph.nodes);
console.log()
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
// if (params.nodes[0] == 'C06186') {
//   console.log('click event on 2!');
// }
deleteEdgeMode(params.nodes[0]);
console.log(params)
});

function deleteEdgeMode(nodeId){
    network.deleteSelected();
}