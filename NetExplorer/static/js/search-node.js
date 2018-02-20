
// --------------------------
// SEARCH NODE
    $("#search-netexplorer-btn").on("click", function(){
        var searchterm = $("#genename-graph").val();
        if (searchterm) {
            var selectorName = 'node[name @="' + searchterm + '"]';
            var selectorHomologs = 'node[homolog @="' + searchterm + '"]';

            var theElements = cy.elements(selectorName);
            if (theElements.length) {
                // Match by Name
                theElements.addClass('highlighted');
            } else {
                theElements = cy.elements(selectorHomologs);
                if (theElements.length) {
                    // Match by Homologs
                    theElements.addClass('highlighted');
                } else {
                    // No match
                    alert("NO MATCH!");
                }
            }
        }
    });

    $("#removesearch").on("click", function(){
        cy.nodes().removeClass('highlighted');
    });
