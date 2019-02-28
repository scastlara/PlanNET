

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
                console.log(data);
                response(data);
            },
            error: function(data) {
                console.log(data.responseText);
            }
        });
    }
    if (s_string.startsWith("_") && s_string.length >= 3) {
        makeQuery(s_string, "Dresden");
    } else if (s_string.startsWith("SMESG") && s_string.length >= 11 ) {
        makeQuery(s_string, "Smesgene");        
    } else if (s_string.startsWith("SMEST") && s_string.length >= 10 ) {
        makeQuery(s_string, "Smest");
    } else if (s_string.startsWith("GO:") && s_string.length >= 7 ) {
        makeQuery(s_string, "Go");
    } else if (s_string.startsWith("PF") && s_string.length >= 4 ) {
        makeQuery(s_string, "Pfam");
    } else if (s_string.length >= 13) {
        makeQuery(s_string, "PlanarianContig");
    } else {
        response([]);
    }

};


var autocompletePlanExp = function(s_string, response, experiment) {
    console.log(experiment);


    var makeQuery = function(s_string) {
        $.ajax({
            type: "GET",
            url: window.ROOT + "/autocomplete",
            data: {
                's_string'    : s_string,
                'experiment'  : experiment,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                // Change Exp type
                response(data);
            },
            error: function(data) {
                console.log(data.responseText);
            }
        });
    }

    if (s_string.startsWith("_") && s_string.length >= 3) {
        makeQuery(s_string, "Dresden");
    } else if (s_string.startsWith("SMESG") && s_string.length >= 11 ) {
        makeQuery(s_string, "Smesgene");        
    } else if (s_string.startsWith("SMEST") && s_string.length >= 10 ) {
        makeQuery(s_string, "Smest");
    } else if (s_string.startsWith("GO:") && s_string.length >= 7 ) {
        makeQuery(s_string, "Go");
    } else if (s_string.startsWith("PF") && s_string.length >= 4 ) {
        makeQuery(s_string, "Pfam");
    } else if (s_string.length >= 13) {
        makeQuery(s_string, "PlanarianContig");
    } else {
        response([]);
    }


};
