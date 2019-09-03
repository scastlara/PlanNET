$( document ).ready(function(){

    function handleAutoSelectExperiment(expName) {

        new Promise((resolve, reject) => { // (*)
            $("#planexp-summary-toc").show();
            $('#planexp-summary-toc').css('display', 'inline-block');
            $("#planexp-dge-table-container").hide();
            $("#planexp-dge-table-container-toc").hide();
            $("#planexp-gene-expression").hide();
            $("#planexp-gene-expression-toc").hide();
            $("#planexp-gene-coexpression").hide();
            $('#planexp-gene-coexpression-toc').hide();
            $("#planexp-tsne").hide();
            $("#planexp-tsne-toc").hide();
            $("#planexp-markers").hide();
            $("#planexp-markers-toc").hide();
            $("#planexp-network").hide();
            $("#planexp-network-toc").hide();
            $("#tsne-plot-gene").html("");
            $("#tsne-plot-condition").html("");
            $('#planexp-links-toc').hide();
            $('#planexp-links').hide();
            $("#planexp-sample-counter").hide();
            try {
                cy.nodes().remove();
            } catch {
                // nothing to do
            }

            $('#select-experiment').val(expName);
            $('#select-experiment').selectpicker('refresh');
        });
        
    }

    function autoSelectDataset(dataset) {

        
        return new Promise((resolve, reject) => {
            console.log("Getting dataset");
            console.log($("#planexp-dge-ctype").val());
            // Empty DGE table + Gene Plot and Deselect Conditions
            $("#planexp-dge-table").html("");
            $('#planexp-dge-c1').selectpicker('val', '');
            $('#planexp-dge-c2').selectpicker('val', '');
            $("#expression-plot").html("");
            $("#coexpression-plot").html("");
            $("#tsne-plot-gene").html("");
            $("#tsne-plot-condition").html("");
            $("#volcano-plot").html("");
            $("#plot-genenotfound").hide();
            $("#planexp-goea-condition").html("");
            $("#planexp-goea-condition").selectpicker("refresh");
            $("#goea-results").html("");

            // Change DGE table ConditionType select
            showConditionTypes("dge-table-condition-selects", $("#planexp-dge-ctype").val());
            
            // Change Network ConditionType select
            showConditionTypes("network-condition-selects", $("#network-ctype").val());

            // Change Sample counter
            showConditionTypes("counter-condition-selects", $("#counter-ctype").val());

            // Get regulatory links if they exist
            // only if Single Cell
            if (currentExpType == expType['Single-Cell']) {
                $('#planexp-links').show(250);
                $('#planexp-links-toc').show(250);
            // getRegulatoryLinksTable('#planexp-links', '#planexp-links-toc', '#planexp-links-table-container');
            } else {
                $('#planexp-links-toc').hide();
                $('#planexp-links').hide();
            }

            // Show the necessary cards
            $("#planexp-dge-table-container").show(250);
            $("#planexp-gene-expression").show(250);
            $("#planexp-dge-table-container-toc").show(250);
            $('#planexp-dge-table-container-toc').css('display', 'inline-block');
            $("#planexp-gene-expression-toc").show(250);
            $('#planexp-gene-expression-toc').css('display', 'inline-block');
            $("#planexp-gene-coexpression").show(250);
            $('#planexp-gene-coexpression-toc').css('display', 'inline-block');
            $("#planexp-sample-counter").show(250);
            $("#planexp-sample-counter-toc").show(250);


            $("#planexp-network-toc").show(250);
            if (currentExpType == expType['Single-Cell']) {
                $("#planexp-tsne").show(250);
                $("#planexp-tsne-toc").show(250);
                $('#planexp-tsne-toc').css('display', 'inline-block');
                $("#planexp-markers").show(250);
                $("#planexp-markers-toc").show(250);
                $('#planexp-markers-toc').css('display', 'inline-block');

                // Add Sample to dropdown in GeneExpressionPlot

                $("#gene-expression-ctype").append(ctypeRow("Samples"));
                $("#gene-expression-ctype").selectpicker("refresh");

            } else {
                $("#gene-expression-expressed-container").hide();
            };

            $("#gene-expression-expressed").removeAttr("checked");

            $('#select-dataset').val(dataset);
            $('#select-dataset').selectpicker('refresh');
            console.log("Dataset done");
            
        })
            
       
    }

    function autoAddCytoscape(graphelements) {
        return new Promise((resolve, reject) => {
            try {

                $("#planexp-network").show(250, function(){
                    // Initialize cytoscape now that the container div is visible
                    initCytoscape(graphelements);
                    $.scrollTo("#planexp-network", 500);
                });

            } catch (err) {
                console.log(err)
            }
        });
    }


    function autoSelectAll() {
        experimentSummary(window.autoExperiment, $("#planexp-summary"))
            .then(getDatasets(window.autoExperiment, $("#select-dataset")))
            .then(fillConditions(window.autoExperiment, $("select.condition-select")))
            .then(fillCtypes(window.autoExperiment, $("select.ctype-select")))
            .then(handleAutoSelectExperiment(window.autoExperiment))
            .then(function(){ autoSelectDataset(window.autoDataset); })
            .then(function(){ autoAddCytoscape(window.autoGraph)})
            
    }

    autoSelectAll();


});