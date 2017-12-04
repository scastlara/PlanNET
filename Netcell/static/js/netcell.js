// cellnet.js : CellNet Main scripts

/**
*-----------------------------------------------------------------------------
* NETCELL CONTROLS
**/
/** Select Experiment
* Changes text of dropdown when select
* Shows appropiate controls
**/
$(".cn-experiment-dropdown li a").click(function(){
  $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
  alert("EXPERIMENT");
  $(".cn-exp-controls").show();
  $(".cn-experiment-upload-btn").hide();
});


/** Select CellType
* Changes text of dropdown when select
* Changes Visualization
**/
$(".cn-celltype-dropdown li a").click(function(){
  $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
  alert("CELLTYPE");
});


$( function() {
  $( "#dialog-error" ).dialog({
    autoOpen: false,
  });
});

/**
* Display Error dialog with message
**/
function displayError(message) {
  $( "#error-content" ).html(message);
  $( "#dialog-error" ).dialog("open");
}



/**
*-----------------------------------------------------------------------------
* UPLOAD GRAPH
**/
/**
* Upload graph overlay
**/
$("#cn-upload-graph").on("click", function(event){
  // Close previous overlays
  $('.card-overlay').hide(450);
  $('.close-overlay').hide(450);

  // Open overlay
  $('.card-overlay-netcell-uploadgraph').slideToggle(450);
  $('.close-overlay-uploadgraph').slideToggle(450);
  return false;
});


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
    $('.card-overlay-netcell-uploadgraph').slideToggle(450);
    $('.close-overlay-uploadgraph').slideToggle(450);

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

/**
* Add listener for files
**/
$(function(){
  document.querySelector("#files-json").addEventListener('change',handleFileSelect, false);
  document.querySelector("#files-tbl").addEventListener('change',handleFileSelect, false);
  document.querySelector("#files-dot").addEventListener('change',handleFileSelect, false);
});


/**
*-----------------------------------------------------------------------------
* UPLOAD EXPERIMENT
**/
$("#cn-upload-experiment").on("click", function(event){
  // Close previous overlays
  $('.card-overlay').hide(450);
  $('.close-overlay').hide(450);

  $('.card-overlay-netcell-uploadexperiment').slideToggle(450);
  $('.close-overlay-uploadexperiment').slideToggle(450);
  return false;
});
