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
function addCellTypeListener() {
  $(".cn-celltype-dropdown li a").click(function(){
    $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    alert("CELLTYPE");
  });
}


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
var cellexp    = "";
var cellclust  = "";
var cellconditions = "";
var celllabels = "";
var genelabels = "";
var formData   = "";
var sce        = "";
var cond_names = [];

function handleExpUpload(evt) {
  var files = evt.target.files; // FileList object
  var file = files[0];
  var reader = new FileReader();
  reader.onload = function(){
    // Check format
    if (evt.target.id == "files-cellexp") {
      // Cell Expression File
      textfile = reader.result;
      cellexp = textfile;
      cellexp = cellexp.split("\n");
      celllabels = cellexp[0].split("\t"); // Save cell order in exp file
      if (! celllabels[0]) {
        celllabels = celllabels.slice(1); /// Remove first blank element
      }
      // initialize expression array
      var expression = [];
      for (var i = 0; i < celllabels.length; i++) {
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
      // Change green tick
      $("#files-cellexp-ok").show();
      $("#files-cellexp-notok").hide();
      $("#files-sce-ok").hide();
      if (! cellconditions) {
        $("#files-cellclust-notok").show();
      } else {
        $('#uploadexperiment-send').removeClass("disabled");
      }
    } else if (evt.target.id == "files-cellclust") {
      // Cell Clustering
      textfile = reader.result;
      cellconditions = textfile;
      cellconditions = cellconditions.split("\n");
      var clusters = [];
      var conditions = []
      for (var cl = 0; cl < cellconditions.length; cl++) {
        var clusterlist = cellconditions[cl].split(/[ \t]+/);
          // We can have more conditions/batches
          // Can store up to 3 conditions
          // Must do a warning
        conditions.push(clusterlist.slice(1));
      }
      cellconditions = conditions;
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


      formData = new FormData();
      formData.append('scefile', file);
      formData.append('csrfmiddlewaretoken', csrf_token);
      // Change green tick
      $("#files-sce-ok").show();
      $('#uploadexperiment-send').removeClass("disabled");
    }

  };
  reader.readAsText(file);
}




/*
 * Show and hides the necessary divs when an experiment is uploaded or deleted
 */
function handleDivsExperiment(show, exp_name) {
  if (show) {
    $('.dropdown-toggle').dropdown();
    $(".exp-name-label").html(exp_name);
    $('.card-overlay').hide();
    $('.close-overlay').hide();
    $("#exp-label-container").show();
    $(".cn-exp-controls").show();
    $(".cn-experiment-upload-btn").hide();
    $("#search-cell").show();
  } else {
    $("#exp-label-container").hide();
    $(".cn-exp-controls").hide();
    $(".cn-experiment-upload-btn").show();
    $("#search-cell").hide();
    $(".upload-tick").hide();
  }
}




/**
*  Upload experiment
**/
$('#uploadexperiment-send').on("click", function(){
  if (! $(this).hasClass("disabled") ) {
    // Change displayed name of experiment
    var exp_name = $('#exp-name').val();
    if (! exp_name) {
      exp_name = "Experiment #1";
    }




    /*
     * Adds the ColorBy options to the dropdown of AboutExperiment
     */
    function addColorByOpts () {
      for (var condidx = 0; condidx < cellconditions[0].length; condidx++) {
        var opthtml = "";
        opthtml = '<li><a href="#">' + cond_names[condidx] + '</a></li>'
        $('#cn-colorby-dropdown').append(opthtml);
      }
    }


    /*
     * Adds cluster options to dropdown
     */
    function addConditionOpts () {
      var allconditions = [];
      for (var i = 0; i < cellconditions.length; i++) {
        for (var cidx = 0; cidx < cellconditions[i].length; cidx++) {
          if (allconditions.length <= cidx) {
            allconditions.push([]);
          }
          allconditions[cidx].push(cellconditions[i][cidx]);
        }
      }

      for (cond in allconditions) {
        var selector = ".cn-condition-dropdown-container" + cond;
        console.log(selector);
        $(selector).show();
        allconditions[cond] = new Set(allconditions[cond].sort());
        allconditions[cond] = Array.from(allconditions[cond]);
        $(".condition-name" + cond).html(cond_names[cond]);
      }

      for (var clustidx = 0; clustidx < allconditions.length; clustidx++) {
        var opthtml = "";
        for (cond in allconditions[clustidx]) {
          opthtml = '<li><a href="#">' + allconditions[clustidx][cond] + '</a></li>'
          var dropselector = "#dropdown-ul-condition" + clustidx;
          $(dropselector).append(opthtml);
        }

      }
        addCellTypeListener();
    }

    // Check if upload experiment was done via TSV files or RDS
    // Prioritize RDS
    if (formData) {
      alert("we have a file");
      if (!$('#cluster-name').val()) {
        cond_names.push("clusters");
      } else {
        cond_names.push($('#cluster-name').val());
      }

      if ($('#cond1-name').val()) {
        cond_names.push($('#cond1-name').val());
      }

      if ($('#cond2-name').val()) {
        cond_names.push($('#cond2-name').val());
      }
      formData.append('conditions_names', cond_names);

      $.ajax({
          url : '/upload_sce',
          type : 'POST',
          data : formData,
          processData: false,  // tell jQuery not to process the data
          contentType: false,  // tell jQuery not to set contentType
          beforeSend: function() {
            $('#loading').show();
          },
          success : function(data) {
            if (data.error) {
              displayError(data.error);
            } else {
              cellexp = data.cellexp;
              cellconditions = data.cellconditions;
              celllabels = data.celllabels;
              genelabels = data.genelabels;
              addColorByOpts();
              addConditionOpts();
              addColorBy();
              handleDivsExperiment(true, exp_name);
            }
            $("#loading").hide();
          },
          error: function(result) {
            displayError("Can't read RDS file.");
            $("#loading").hide();
          }
      });
    } else {
      cond_names.push("clusters");
      for (var icond = 0; icond < cellconditions[0].length; icond++) {
        var icond_name = icond + 1;
        cond_names.push("Condition_" + icond_name);
      }
      addColorByOpts();
      addConditionOpts();
      addColorBy();
      handleDivsExperiment(true, exp_name);
    }
  }

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
* Delete EXPERIMENT
**/
$("#delete-exp").on("click", function() {
  alert("Delete");
  handleDivsExperiment(false);
  cellexp    = "";
  cellclust  = "";
  cellconditions = "";
  celllabels = "";
  genelabels = "";
  formData   = "";
  sce        = "";
  cond_names = [];

})

/**
*-----------------------------------------------------------------------------
* ABOUT EXPERIMENT
**/

/**
* Creates array of traces depending on "group" categorical variable
**/
function changeTraces(xpoints, ypoints, celllabels, groups, condIdx) {
  var traces = [];
  var categories = [];
  for (var i = 0; i < groups.length; i += 1) {
    if (categories.indexOf(groups[i][condIdx]) === -1) {
      if (groups[i][condIdx] == -1) {
        // Skip clusters named "-1"
        continue;
      }
      traces.push({
        x: [],
        y: [],
        mode: 'markers',
        name: groups[i][condIdx],
        text: []
      });
      categories.push(groups[i][condIdx]);
    } else {
      traces[categories.indexOf(groups[i][condIdx])].x.push(xpoints[i]);
      traces[categories.indexOf(groups[i][condIdx])].y.push(ypoints[i]);
      traces[categories.indexOf(groups[i][condIdx])].text.push(celllabels[i]);
    }
  }
  traces.sort(function(a,b) {
    return a.name - b.name;
  })
  return traces;
}

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

/*
 * Add Controls for Dropdown ColorBy
 */
var colorby = 0; // index of colorby=condIdx
function addColorBy () {
   $(".cn-colorby-dropdown li a").click(function(){
     $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
     $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
     colorby = cond_names.indexOf($(this).text())
   });
}


/**
* Slider for ReducedDims and perplexity
**/
$('#reducedDims').slider();
$('#reducedDims').slider('setValue', 25);
$('#perplexity').slider();
$('#perplexity').slider('setValue', 10);

/**
* Plot button send
**/
$("#plot-btn").on("click", function(){

  /**
  * Color plot by Cluster or Condition
  **/
  function plotByClust(xCoords, yCoords, celllabels, cellconditions) {
    condIdx = colorby;
    var traces = changeTraces(xCoords, yCoords, celllabels, cellconditions, condIdx);
    Plotly.newPlot('tsne-plot', traces);
    $(".colored-by .colored-by-text").html(cond_names[colorby]);
    $(".colored-by").show();
  }

  /**
  * Color plot by gene expression
  **/
  function plotByGene(xCoords, yCoords, celllabels, selGene) {
    var colorDim = [];
    var geneIdx = genelabels.indexOf(selGene);
    if (geneIdx == -1) {
      displayError("Can't find Gene.");
      return;
    }

    for (var cellidx = 0; cellidx < cellexp.length; cellidx++) {
      colorDim.push(cellexp[cellidx][geneIdx]);
    }
    var trace = {
        x: xCoords,
        y: yCoords,
        mode: 'markers',
        marker: {
          size: 5,
          color: colorDim
        },
        text: celllabels
    }
    Plotly.newPlot('tsne-plot', [trace]);
    $(".colored-by .colored-by-text").html(selGene);
    $(".colored-by").show();
  }


  var reducedDims = $('#reducedDims').val();
  var perplexity  = $('#perplexity').val();
  if (! reducedDims) {
    reducedDims = 25; // Default
  }
  if (! perplexity) {
    perplexity = 10; // Default
  }
  // Compute PCA of array through AJAX call
  //jObject = JSON.stringify(cellexp);
  $.ajax({
    type: "POST",
    url: "/pca",
    data: {
      'type'      : 'POST',
      'csrfmiddlewaretoken': csrf_token,
      'cellexp[]': cellexp,
      'reducedDims': reducedDims,
      'perplexity' : perplexity

    },
    success: function(data) {
      var xCoords = JSON.parse(data.x);
      var yCoords = JSON.parse(data.y);

      // Must add check for gene
      var selGene = $("#genename").val();

      if (! selGene) {
        plotByClust(xCoords, yCoords, celllabels, cellconditions);
      } else {
        plotByGene(xCoords, yCoords, celllabels, selGene);
      }

    },
    error: function(data) {
      displayError("Can't plot SC experiment.")
    }
  });
});
