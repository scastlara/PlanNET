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
            targetDiv.slideToggle(250);
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
            conditionSelects.html(); // clean previous HTML
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
            datasetSelect.html();
            for (const i in data) {
                datasetName = data[i].fields.name;
                console.log(datasetName);
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

            targetDiv.show(250);
        }
    });
}



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
    fillConditions(expName, $("select.condition-select"))
});


/**
 * selectDataset
 *   Summary:
 *     Handles the selection of a given dataset.
 *     Will show the DGE table.
 */
$("#select-dataset").on("change", function(){
    var dataset = $("#select-dataset").val();
    $("#planexp-dge-table-container").show(250);
});


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