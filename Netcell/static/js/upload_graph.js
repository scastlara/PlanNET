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

  // Check format
  if (evt.target.id == "files-json") {
    format = "json";
  } else if (evt.target.id == "files-tbl") {
    format = "tbl";
  } else if (evt.target.id == "files-dot") {
    format = "dot";
  }
  alert(format);
  var reader = new FileReader();
  reader.onload = function(){
    var text = reader.result;
    alert(text);
  };
  reader.readAsText(file);

  // Close overlay
  $('[id="card-overlay"]').slideToggle(450);
  $('.close-overlay').slideToggle(450);

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
