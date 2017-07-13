// Script that contains function to filter pathways in Pathway Finder using a text
// based form.

$("#pathway-filter").submit(function(e){
    var symbols     = document.getElementById('pathway-filter-text').value;
    var symbol_list = symbols.split(",");
    var panels      =  document.getElementsByClassName("pathway-panel");
    var numshown    = 0;

    if (!symbols) {
        // Nothing to filter, show them all
        for (var k = 0; k < panels.length; k++) {
            panels[k].style.display = "block";
        }
        document.getElementById("numfiltered").textContent=panels.length;
        return false;
    }

    // Remove whitespace and make uppercase the user input
    symbol_list = symbol_list.map(function(x){ x = x.replace(/ /g,''); return x.toUpperCase(); });


    // Iterate through all the panels
    panel:
    for (var i = 0; i < panels.length; i++) {
        var graph    = panels[i].getAttribute('value');
        var graphobj = JSON.parse(graph);
        var needed   = {};

        // Initialize dictionary of needed symbols
        for (var sym in symbol_list) {
            needed[symbol_list[sym]] = 0;
        }

        nodes:
        for (var j = 0; j < graphobj.nodes.length; j++) {
            var id      = graphobj.nodes[j].data.id.toUpperCase();

            if (symbol_list.indexOf(id) > -1) {
                //Node id in the path
                needed[id] = 1;
            } else {
                //Node not in the path. Hide the div and go to next div.
                continue nodes;
            }
        }
        // Check if all the elements were found
        needed:
        for (var nsym in needed) {
            if (!needed[nsym]) {
                // One element needed not found in panel. Hide it and go to next.
                //alert(panels[i].getAttribute("id"));
                //panels[i].setAttribute('class', 'hidden');
                panels[i].style.display = 'none';
                continue panel;

            }
        }

        panels[i].style.display = "block";
        numshown += 1;
    }


    // Change number of elements displayed text
    document.getElementById("numfiltered").textContent=numshown;
    return false;
});
