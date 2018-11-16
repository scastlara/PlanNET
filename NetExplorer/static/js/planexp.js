/* PlanExp */


/**
 * experimentSummary
 *   Summary:
 *     Performs AJAX query to /experiment_summary, 
 *     retrieving the HTML code of the summary and
 *     putting it on the targetDiv (as well as making it
 *     visible).
 *   Arguments:
 *     - Experiment name string
 *     - jQuery object of div to put the summary
 *     - jQuery object of DataSet Select to fill with available datasets
 *   Returns:
 *     - Nothing
 */
experimentSummary = function(expName, targetDiv) {
    
    $.ajax({
        type: "GET",
        url: "/experiment_summary",
        data: {
            'experiment'    : expName,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            targetDiv.html(data);
            targetDiv.hide();
            targetDiv.show(250);
        },
        error: function(data) {
            console.log(data.responseText);
        }
    });
    
}


/**
 * fillConditions
 *   Summary:
 *     Performs AJAX query to /experiment_conditions,
 *     retrieving the conditions for a given experiment
 *     and filling all the Selects elements with those
 *     conditions.
 *   Arguments:
 *     - Experiment name string
 *     - jQuery object of select objects to fill.
 *   Returns:
 *     - Nothing
 */
fillConditions = function(expName, conditionSelects) {

    conditionRow = function(conditionName) {
        return "<option class='condition-option' value='" + 
                conditionName + 
                "'>" + 
                conditionName + 
                "</option>";
    }

    $.ajax({
        type: "GET",
        url: "/experiment_conditions",
        data: {
            'experiment'    : expName,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            conditionSelects.html(""); // clean previous HTML
            for (const condition in data) {
                conditionName = data[condition].fields.name;
                conditionSelects.append(conditionRow(conditionName));
            }
            conditionSelects.selectpicker('refresh');
        },
        error: function(data) {
            console.log(data.responseText);
        }
    })
}


/**
 * experimentDGETable
 *   Summary:
 *     Performs AJAX query to /experiment_dge_table, 
 *     retrieving the HTML code of the differential
 *     expression table and puting it in targetDiv.
 *   Arguments:
 *     - Experiment name string
 *     - jQuery object of div to put the table.
 *   Returns:
 *     - Nothing
 */
getDatasets = function(expName, datasetSelect) {

    datasetRow = function(datasetName) {
        return "<option class='dataset-option' value='" + 
                datasetName + 
                "'>" + 
                datasetName + 
                "</option>";
    }

    $.ajax({
        type: "GET",
        url: "/experiment_dataset",
        data: {
            'experiment': expName,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            datasetSelect.html("");
            for (const i in data) {
                datasetName = data[i].fields.name;
                datasetSelect.append(datasetRow(datasetName));
            }
            datasetSelect.selectpicker("refresh");
            datasetSelect.show(250);
        }
    });
}


/**
 * experimentDGETable
 *   Summary:
 *     Performs AJAX query to /experiment_dge_table, 
 *     retrieving the HTML code of the differential
 *     expression table and puting it in targetDiv.
 *   Arguments:
 *     - Experiment name string
 *     - jQuery object of div to put the table.
 *   Returns:
 *     - Nothing
 */
experimentDGETable = function(expName, dataset, condition1, condition2, targetDiv) {

    $.ajax({
        type: "GET",
        url: "/experiment_dge_table",
        data: {
            'experiment': expName,
            'dataset'   : dataset,
            'condition1': condition1,
            'condition2': condition2,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            targetDiv.html(data);
            targetDiv.hide();
            targetDiv.show(250);
        }
    });
}


/**
 * plotGeneExpression
 *   Summary:
 *     Performs AJAX query to /plot_gene_expression, 
 *     retrieving the JSON data to pass to Plotly
 *   Arguments:
 *     - Experiment name
 *     - Dataset
 *     - Gene name
 *     - jQuery object of div to plot.
 *   Returns:
 *     - Nothing
 */
plotGeneExpression = function(expName, dataset, geneName, plotDivId) {
    $("#expression-plot-loading").show();
    $("#" + plotDivId).html("");
    $.ajax({
        type: "GET",
        url: "/plot_gene_expression",
        data: {
            'experiment': expName,
            'dataset'   : dataset,
            'gene_name': geneName,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            if (data) {
                $("#plot-genenotfound").hide();
                Plotly.newPlot(plotDivId, data.data, data.layout);
            } else {
                $("#plot-genenotfound").show(250);
            }
            $("#expression-plot-loading").hide();
        }
    });
}



//----------------------------------------------------
/* BUTTONS AND EVENTS */

/**
 * selectExperiment
 *   Summary:
 *     Handles the selection of a given experiment.
 *     Performs all the actions necessary when that happens.
 */
$("#select-experiment").on("change", function() { 
    var expName = $(this).val();
    experimentSummary(expName, $("#planexp-summary"));
    getDatasets(expName, $("#select-dataset"));
    fillConditions(expName, $("select.condition-select"));

    // Hide on change 
    $("#planexp-dge-table-container").hide();
    $("#planexp-gene-expression").hide();
});


/**
 * Select Dataset
 *   Summary:
 *     Handles the selection of a given dataset.
 *     Will show the DGE table.
 */
$("#select-dataset").on("change", function(){
    var dataset = $("#select-dataset").val();

    // Empty DGE table + Gene Plot and Deselect Conditions
    $("#planexp-dge-table").html("");
    $('#planexp-dge-c1').selectpicker('val', '');
    $('#planexp-dge-c2').selectpicker('val', '');
    $("#expression-plot").html("");
    $("#plot-genenotfound").hide();

    // Show the necessary cards
    $("#planexp-dge-table-container").show(250);
    $("#planexp-gene-expression").show(250);

    
});



/**
 * Select Condition for DGE table
 *   Summary:
 *     Handles the selection of the conditions for the.
 *     DGE table.
 */
$("select.dge-table-condition-selects").on("change", function(){
    var expName = $("#select-experiment").val();
    var condition1 = $("#planexp-dge-c1").val();
    var condition2 = $("#planexp-dge-c2").val();
    var dataset = $("#select-dataset").val();
    if ( ! condition1 || ! condition2 ) {
        return;
    } 

    experimentDGETable(expName, dataset, condition1, condition2, $("#planexp-dge-table"));

});

/**
 * Get Gene Expression Plot
 *   Summary:
 *     Plots gene expression 
 */
$("#plot-expression-btn").on("click", function() {
    var expName = $("#select-experiment").val();
    var geneName = $("#gene-expression-search").val();
    var dataset = $("#select-dataset").val();

    if (!geneName) {
        $("#plot-genenotfound").show(250);
        return;
    }
    $("#plot-genenotfound").hide();
    plotGeneExpression(expName, dataset, geneName, "expression-plot");
})