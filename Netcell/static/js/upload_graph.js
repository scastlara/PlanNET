/**
* Handles graph input
**/
function handleFileSelect(evt) {
  var files = evt.target.files; // FileList object
  // files is a FileList of File objects. List some properties.
  var output = [];
  var file = files[0];
  var format = "";

  // Read file
  var reader = new FileReader();
  reader.onload = function(){
    var graphelements;
    textfile = reader.result;
    // Check format
    if (evt.target.id == "files-json") {
      try {
        graphelements = JSON.parse(textfile);
        addJsonToCy(graphelements);
      }
      catch (err) {
        displayError("Incorrect JSON file.");
        console.log(err);
      }
    } else if (evt.target.id == "files-tbl") {
      graphelements = tblToJsonTxt(textfile);
      addJsonToCy(graphelements);
    } else if (evt.target.id == "files-dot") {
      format = "dot";
      // dotToJson(textfile)
      // Add graph to cytoscape
    }

    // Close overlay
    $('[id="card-overlay"]').slideToggle(450);
    $('.close-overlay').slideToggle(450);

  };

  reader.readAsText(file);

}



/**
* Add JSON Graph to Cytoscape
**/
function addJsonToCy(graphelements) {
  try {
    cy.add(graphelements);
    cy.layout({'name': 'cose'});
  }
  catch(err) {
    displayError("Incorrect graph definition");
  }
}

/**
* Converts tbl graph string to JSON
**/
function tblToJsonTxt(text) {
  alert("WE'RE IN");
  var jsontext = "";
  var lines = text.split("\n");
  var nodes = [];
  var edges = [];
  for (var i = 0; i < lines.length; i++) {
    // Foreach line
    var cols = lines[i].split("\t");
    if (cols.length == 0 || ! cols[0]) {
      // Empty line
      continue;
    } else if (cols.length == 1) {
      // Node definition
      nodes.push({'data': {'id': cols[0], 'name': cols[0]}});
    } else if (cols.length == 2) {
      // Edge definition without probability
      nodes.push({'data': {'id': cols[0], 'name': cols[0]}});
      nodes.push({'data': {'id': cols[1], 'name': cols[1]}});
      edges.push({'data': {'source': cols[0], 'probability': 1, 'target': cols[1]}});
    } else if (cols.length == 3){
      // Edge definition with probability
      nodes.push({'data': {'id': cols[0], 'name': cols[0]}});
      nodes.push({'data': {'id': cols[1], 'name': cols[1]}});
      edges.push({'data': {'source': cols[0], 'probability': cols[2], 'target': cols[1]}});
    } else {
      // Error
      displayError("Incorrect tbl graph: More than 3 columns");

    }
  }
  graphelements = {'nodes': nodes, 'edges': edges};
  return graphelements;
}

/**
* Converts dot graph string to JSON
**/
function dotToJson(text) {

}


// Add listener for files
$(function(){
  document.querySelector("#files-json").addEventListener('change',handleFileSelect, false);
  document.querySelector("#files-tbl").addEventListener('change',handleFileSelect, false);
  document.querySelector("#files-dot").addEventListener('change',handleFileSelect, false);
});
