$(function() {
    var filterResults = function(elem) {
        var database = $(elem).attr("database");
        $(elem).css("opacity", 1);
        if (database == "All results") {
            $(".small-searchpanel").show();
            $(".filter-results").css("opacity", 1);
        } else {
            $(".filter-results").not(elem).css("opacity", 0.4);
            $(".small-searchpanel").hide();
            $(".small-searchpanel[targetDB='" + database + "']").show();
        }
        
    }

    $(".filter-results").on("click", function(){
        filterResults(this);
    });
})