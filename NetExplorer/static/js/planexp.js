/* PlanExp */



experimentSummary = function(exp_name) {

    conditionRow = function(cond_array) {
        var cond_name         = cond_array[0];
        var defines_cell_type = cond_array[1];
        var cell_type         = cond_array[2];
        var description       = cond_array[3];

        var html_string = "<div class='cond-name'>" + "<b>" + cond_name + "</b>" + " - " + description + "</div>";
        return html_string;

    }

    $.ajax({
        type: "GET",
        url: "/get_experiment",
        data: {
            'experiment'    : exp_name,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success : function(data) {
            $("#planexp-title").html(data.name);
            var citation_html = '<a href="' + data.url + '" target="_blank">' +  data.citation + '</a>';
            $("#planexp-citation").html(citation_html);
            $("#planexp-description").html(data.description);
            $('#planexp-experiment-type').append(data.type);

            for (const cond_type in data.conditions) {
                $("#planexp-conditions").append("<div class='cond-type'>" + cond_type + "</div>");
                for (const condition in data.conditions[cond_type]) {
                    var cond_array = data.conditions[cond_type][condition];
                    var cond_html  = conditionRow(cond_array);

                    $("#planexp-conditions").append(cond_html)

                }
            }
            $('#' + data.type).show();
            $("#planexp-summary").slideToggle(250);
        }
    });
    
}

selectExperiment = function(exp_name) {
    // Get Summary
    experimentSummary(exp_name);

    // Get over/under-expressed table

    // Get info for plots

    // ...
    
    
}

/* BUTTONS AND EVENTS */
$("#select-experiment").on("change", function() { selectExperiment($(this).val()) });