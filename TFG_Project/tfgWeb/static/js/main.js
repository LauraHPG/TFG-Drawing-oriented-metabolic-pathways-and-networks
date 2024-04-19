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

document.addEventListener('DOMContentLoaded', function() {
	// Query the element
	const resizer = document.getElementById('dragMe');
	const leftSide = resizer.previousElementSibling;
	const rightSide = resizer.nextElementSibling;

	// The current position of mouse
	let x = 0;
	let y = 0;
	let leftWidth = 0;

	// Handle the mousedown event
	// that's triggered when user drags the resizer
	const mouseDownHandler = function(e) {
		// Get the current mouse position
		x = e.clientX;
		y = e.clientY;
		leftWidth = leftSide.getBoundingClientRect().width;

		// Attach the listeners to document
		document.addEventListener('mousemove', mouseMoveHandler);
		document.addEventListener('mouseup', mouseUpHandler);
	};

	const mouseMoveHandler = function(e) {
		// How far the mouse has been moved
		const dx = e.clientX - x;
		const dy = e.clientY - y;

		const newLeftWidth = ((leftWidth + dx) * 100) / resizer.parentNode.getBoundingClientRect().width;
		leftSide.style.width = newLeftWidth + '%';

		resizer.style.cursor = 'col-resize';
		document.body.style.cursor = 'col-resize';

		leftSide.style.userSelect = 'none';
		leftSide.style.pointerEvents = 'none';

		rightSide.style.userSelect = 'none';
		rightSide.style.pointerEvents = 'none';
	};

	const mouseUpHandler = function() {
		resizer.style.removeProperty('cursor');
		document.body.style.removeProperty('cursor');

		leftSide.style.removeProperty('user-select');
		leftSide.style.removeProperty('pointer-events');

		rightSide.style.removeProperty('user-select');
		rightSide.style.removeProperty('pointer-events');

		// Remove the handlers of mousemove and mouseup
		document.removeEventListener('mousemove', mouseMoveHandler);
		document.removeEventListener('mouseup', mouseUpHandler);
	};

	// Attach the handler
	resizer.addEventListener('mousedown', mouseDownHandler);
});


function deleteEdgeMode(nodeId) {
	network.deleteSelected();
}



/*
var clusterIndex = 0;
var clusters = [];
var lastClusterZoomLevel = 0;
var clusterFactor = 0.9;

// // create an array with nodes
// var nodes = [
//   { id: 1, label: "Node 1" },
//   { id: 2, label: "Node 2" },
//   { id: 3, label: "Node 3" },
//   { id: 4, label: "Node 4" },
//   { id: 5, label: "Node 5" },
//   { id: 6, label: "Node 6" },
//   { id: 7, label: "Node 7" },
//   { id: 8, label: "Node 8" },
//   { id: 9, label: "Node 9" },
//   { id: 10, label: "Node 10" },
// ];

// // create an array with edges
// var edges = [
//   { from: 1, to: 2 },
//   { from: 1, to: 3 },
//   { from: 10, to: 4 },
//   { from: 2, to: 5 },
//   { from: 6, to: 2 },
//   { from: 7, to: 5 },
//   { from: 8, to: 6 },
//   { from: 9, to: 7 },
//   { from: 10, to: 9 },
// ];

// create a network
// var container = document.getElementById("mynetwork");
// var data = {
//   nodes: nodes,
//   edges: edges,
// };
// var options = {
//   layout: { randomSeed: 8 },
//   physics: { adaptiveTimestep: false },
// };
// var network = new vis.Network(container, data, options);

// set the first initial zoom level
network.once("initRedraw", function () {
  if (lastClusterZoomLevel === 0) {
    lastClusterZoomLevel = network.getScale();
  }
});

// we use the zoom event for our clustering
network.on("zoom", function (params) {
  if (params.direction == "-") {
    if (params.scale < lastClusterZoomLevel * clusterFactor) {
      makeClusters(params.scale);
      lastClusterZoomLevel = params.scale;
    }
  } else {
    openClusters(params.scale);
  }
});

// if we click on a node, we want to open it up!
network.on("selectNode", function (params) {
  if (params.nodes.length == 1) {
    if (network.isCluster(params.nodes[0]) == true) {
      network.openCluster(params.nodes[0]);
    }
  }
});

// make the clusters
function makeClusters(scale) {
  var clusterOptionsByData = {
    processProperties: function (clusterOptions, childNodes) {
      clusterIndex = clusterIndex + 1;
      var childrenCount = 0;
      for (var i = 0; i < childNodes.length; i++) {
        childrenCount += childNodes[i].childrenCount || 1;
      }
      clusterOptions.childrenCount = childrenCount;
      clusterOptions.label = "# " + childrenCount + "";
      clusterOptions.font = { size: childrenCount * 5 + 30 };
      clusterOptions.id = "cluster:" + clusterIndex;
      clusters.push({ id: "cluster:" + clusterIndex, scale: scale });
      return clusterOptions;
    },
    clusterNodeProperties: {
      shape: "dot",
      font: { size: 500 },
    },
  };
  network.clusterOutliers(clusterOptionsByData);
  if (document.getElementById("stabilizeCheckbox").checked === true) {
    // since we use the scale as a unique identifier, we do NOT want to fit after the stabilization
    network.setOptions({ physics: { stabilization: { fit: false } } });
    network.stabilize();
  }
}

// open them back up!
function openClusters(scale) {
  var newClusters = [];
  var declustered = false;
  for (var i = 0; i < clusters.length; i++) {
    if (clusters[i].scale < scale) {
      network.openCluster(clusters[i].id);
      lastClusterZoomLevel = scale;
      declustered = true;
    } else {
      newClusters.push(clusters[i]);
    }
  }
  clusters = newClusters;
  if (
    declustered === true &&
    document.getElementById("stabilizeCheckbox").checked === true
  ) {
    // since we use the scale as a unique identifier, we do NOT want to fit after the stabilization
    network.setOptions({ physics: { stabilization: { fit: false } } });
    network.stabilize();
  }
}
*/