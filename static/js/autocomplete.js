
function splitSearch( val ) {
    return val.split( /,\s*/ );
}

function extractLast( term ) {
    return splitSearch( term ).pop();
}

var getDatasetRegexes = function() {
    $.ajax({
        type: "GET",
        url: window.ROOT + "/get_dataset_regexes",
        data: {
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(data) {
            // Change Exp type
            window.datasetRegexes = data
        },
        error: function(data) {
            console.log(data.responseText);
        }
    });
}

getDatasetRegexes();

var autocompleteContig = function(s_string, response) {
    var makeQuery = function(s_string, database="PlanarianContig") {
        $.ajax({
            type: "GET",
            url: window.ROOT + "/autocomplete",
            data: {
                's_string'    : s_string,
                'database'    : database,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                // Change Exp type
                response(data);
            },
            error: function(data) {
            }
        });
    }


    for (elem in window.datasetRegexes) {
        var datasetElement = window.datasetRegexes[elem];
        if (s_string.match(datasetElement[0])) {
            if (s_string.length < datasetElement[2]) {
                response([]);
                return;
            } else {
                makeQuery(s_string, datasetElement[1]);
                return;

            }
        } 
    }

    if (s_string.length >= 3) {
        makeQuery(s_string, "Human");
        return;
    } 
    

};


var autocompleteReactome = function(s_string, response) {
    console.log("THERE WE GO.");
    var makeQuery = function(s_string, database="ReactomeId") {
        $.ajax({
            type: "GET",
            url: window.ROOT + "/autocomplete",
            data: {
                's_string'    : s_string,
                'database'    : database,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                // Change Exp type
                response(data);
            },
            error: function(data) {
            }
        
        });

    }
    if (s_string.match("R-HSA-.+")) {
        makeQuery(s_string, "ReactomeId");
    } else {
        makeQuery(s_string, "ReactomeName");
    }
    return;


}