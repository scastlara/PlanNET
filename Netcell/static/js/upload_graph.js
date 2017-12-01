// Add listener for files
document.querySelector("#files-json").addEventListener('change',handleFileSelect, false);
document.querySelector("#files-tbl").addEventListener('change',handleFileSelect, false);
document.querySelector("#files-dot").addEventListener('change',handleFileSelect, false);


/**
* Handles graph input
**/
function handleFileSelect(evt) {
  var files = evt.target.files; // FileList object
  // files is a FileList of File objects. List some properties.
  var output = [];
  var file = files[0];
  var format = "";
  console.log(evt);

  // Read file
  var reader = new FileReader();
  reader.onload = function(){
    textfile = reader.result;
    alert(textfile);
    // Check format
    if (evt.target.id == "files-json") {
      format = "json";
      // Check file is correct
      // Add graph to cytoscape
    } else if (evt.target.id == "files-tbl") {
      format = "tbl";
      // tblToJson(textfile)
      // Add graph to cytoscape
    } else if (evt.target.id == "files-dot") {
      format = "dot";
      // dotToJson(textfile)
      // Add graph to cytoscape
    }
    alert(format);
    //alert(textfile);

    // Close overlay
    $('[id="card-overlay"]').slideToggle(450);
    $('.close-overlay').slideToggle(450);

  };

  reader.readAsText(file);

}

/**
* Converts tbl graph string to JSON
**/
function tblToJson(text) {

}

/**
* Converts dot graph string to JSON
**/
function tblToJson(text) {

}
