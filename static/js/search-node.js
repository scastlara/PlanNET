
// --------------------------
// SEARCH NODE
$("#search-netexplorer-btn").on("click", function(){
    var searchterm = $("#genename-graph").val();
    var terms = searchterm.split(",").map(function(x){ return x.toUpperCase()});
    if (terms.length) {
        cy.nodes().filter(function(eidx, ele) {
            if (terms.indexOf(ele.data("name").toUpperCase()) !== -1) {
                return true;
            } else if (terms.indexOf(ele.data("homolog").toUpperCase()) !== -1 ) {
                return true;
            } else {
                return false;
            }
        }).addClass("highlighted");
    }
});

$("#removesearch").on("click", function(){
    cy.nodes().removeClass('highlighted');
});
