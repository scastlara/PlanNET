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
  $(".exp-name-label").html($(this).text());
  $("#exp-name-label").show()
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


/**
* Listener for Experiment upload
**/
var cellexp   = "";
var cellclust = "";
var cellorder = "";
var sce       = "";
function handleExpUpload(evt) {
  var files = evt.target.files; // FileList object
  var file = files[0];
  var reader = new FileReader();
  console.log(files);
  reader.onload = function(){
    // Check format
    if (evt.target.id == "files-cellexp") {
      // Cell Expression File
      textfile = reader.result;
      cellexp = textfile;
      cellexp = cellexp.split("\n");
      cellorder = cellexp[0].split("\t"); // Save cell order in exp file
      // initialize expression array
      var expression = [];
      for (var i = 0; i < cellorder.length - 1; i++) {
        expression[i] = [];
      }
      for (var j = 1; j < cellexp.length; j++) {
        col = cellexp[j].split("\t");
        col = col.slice(1);
        for (var val = 0; val < col.length; val++) {
          expression[val].push(col[val]);
        }
      }

      cellexp = expression;
      console.log(expression);
      // Change green tick
      $("#files-cellexp-ok").show();
      $("#files-cellexp-notok").hide();
      $("#files-sce-ok").hide();
      if (! cellclust) {
        $("#files-cellclust-notok").show();
      } else {
        $('#uploadexperiment-send').removeClass("disabled");
      }
    } else if (evt.target.id == "files-cellclust") {
      // Cell Clustering
      textfile = reader.result;
      cellclust = textfile;
      // Change green tick
      $("#files-cellclust-ok").show();
      $("#files-cellclust-notok").hide();
      $("#files-sce-ok").hide();
      if (! cellexp) {
        $("#files-cellexp-notok").show();
      } else {
        $('#uploadexperiment-send').removeClass("disabled");
      }
    } else if (evt.target.id == "files-sce") {
      // SCE object
      sce = file;
      // Change green tick
    }

  };
  reader.readAsText(file);
}

/**
*  Compute tSNE and plot
**/
$('#uploadexperiment-send').on("click", function(){
  console.log(cellexp);
  // Change displayed name of experiment
  var exp_name = $('#exp-name').val();
  if (! exp_name) {
    exp_name = "Experiment #1";
  }
  $(".exp-name-label").html(exp_name);
  $('.card-overlay').hide();
  $('.close-overlay').hide();
  $("#exp-name-label").show();
  $(".cn-exp-controls").show();
  $(".cn-experiment-upload-btn").hide();
  /* Options for tSNE
  var opt = {};
  opt.epsilon = 10; // epsilon is learning rate (10 = default)
  opt.perplexity = 30; // roughly how many neighbors each point influences (30 = default)
  opt.dim = 2; // dimensionality of the embedding (2 = default)
  var tsne = new tsnejs.tSNE(opt); // create a tSNE instance
  */
  // Compute PCA of array through AJAX call
  $.ajax({
    type: "POST",
    url: "/pca",
    data: {
      'type'      : 'POST',
      'csrfmiddlewaretoken': csrf_token,
      'cellexp': cellexp
    },
    success: function(data) {
      console.log(data);
    }
  });

  /*tsne.initDataRaw(cellexp);
  for(var k = 0; k < 500; k++) {
    tsne.step(); // every time you call this, solution gets better
  }
  var Y = tsne.getSolution();
  console.log(Y);
  */

  //$(".cn-experiment-dropdown").val("Custom Experiment").change();
  //$(".cn-experiment-dropdown").addClass("disabled");
  //alert("YEP");
});

/**
* Add listener for Experiment files
**/
$(function(){
  document.querySelector("#files-cellexp").addEventListener('change',handleExpUpload, false);
  document.querySelector("#files-cellclust").addEventListener('change',handleExpUpload, false);
  document.querySelector("#files-sce").addEventListener('change',handleExpUpload, false);
});


/**
*-----------------------------------------------------------------------------
* ABOUT EXPERIMENT
**/
/**
* About Experiment
**/
$("#aboutexp-btn").on("click", function(event){
  // Close previous overlays
  $('.card-overlay').hide(450);
  $('.close-overlay').hide(450);

  // Open overlay
  $('.card-overlay-netcell-aboutexp').slideToggle(450);
  $('.close-overlay-aboutexp').slideToggle(450);
  return false;
});


/**
* Slider for ReducedDims and perplexity
**/
$('#reducedDims').slider();
$('#perplexity').slider();
