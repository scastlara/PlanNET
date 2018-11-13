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
 *     - JQuery object of div to put the summary
 *   Returns:
 *     - Nothing
 *   
 */
experimentSummary = function(expName, targetDiv) {

    $.ajax({
        type: "GET",
        url: "/experiment_summary",
        data: {
            'experiment'    : expName,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success : function(data) {
            targetDiv.html(data);
            targetDiv.slideToggle(250);
        }
    });
    
}



/**
 * selectExperiment
 *   Summary:
 *     Handles the selection of a given experiment.
 *     Performs all the actions necessary when that happens.
 *   Arguments:
 *     - Experiment name.
 *     - JQuery object of div to put the summary.
 *   Returns:
 *     - Nothing
 *   
 */
selectExperiment = function(expName, summaryDiv) {
    // Get Summary
    experimentSummary(expName, summaryDiv);

    // Get over/under-expressed table

    // Get info for plots

    // ...
    
    
}

/* BUTTONS AND EVENTS */
$("#select-experiment")
    .on("change", function() { 
        selectExperiment($(this).val(), $("#planexp-summary")) 
    });