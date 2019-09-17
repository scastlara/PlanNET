/* PlanExp */

$( document ).ready(function(){

    window.expType = Object.freeze({"Single-Cell":1, "RNA-Seq":2});
    window.currentExpType = false;
    var csrftoken = getCookie('csrftoken');

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

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
        
        return $.ajax({
            type: "GET",
            url: window.ROOT + "/experiment_summary",
            data: {
                'experiment'    : expName,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                // Change Exp type
                currentExpType = expType[data.exp_type];
                targetDiv.html(data.html);
                targetDiv.hide();
                targetDiv.show(250);
            },
            error: function(data) {
                console.log(data.responseText);
            }
        });
        
    }


    conditionRow = function(conditionName, ctype) {
        conditionClass = ctype.replace(/ /g, "_");
        return "<option class='condition-option " + 
                conditionClass + "'" +
                " value='" + 
                conditionName + 
                "'>" + 
                conditionName + 
                "</option>\n";
    }

    ctypeRow = function(conditionName) {
        return "<option class='condition-option' value='" + 
                conditionName  + 
                "'>" + 
                conditionName + 
                "</option>";
    }


    optGroupOpen = function(ctype) {
        return "<optgroup label='" + 
                ctype + 
                "' " + 
                "class='condition-option " + 
                ctype.replace(/ /g, "_") + "'" + 
                ">\n";
    }

    optGroupClose = function() {
        return "</optgroup>\n";
    }


    rgb2hex = function(rgb) {
        if (/^#[0-9A-F]{6}$/i.test(rgb)) return rgb;
    
        rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        function hex(x) {
            return ("0" + parseInt(x).toString(16)).slice(-2);
        }
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
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

        return $.ajax({
            type: "GET",
            url: window.ROOT + "/experiment_conditions",
            data: {
                'experiment'    : expName,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                conditionSelects.html(""); // clean previous HTML
                //data = data.conditions;
                window.comparisons = data.comparisons;
                var keys = Object.keys(data.conditions);

                // Group conditions by Condition Type
                groups = {};
                for (var i=0; i<keys.length; ++i) {
                    if (! groups[ data.conditions[keys[i]] ]) {
                        groups[ data.conditions[keys[i]] ] = [];
                    }
                    groups[ data.conditions[keys[i]] ].push(keys[i]);
                }
                
                var html_to_add = "";
                // Add conditions to dropdowns sorted within each Condition Type.
                for (ctype in groups) {
                    html_to_add += optGroupOpen(ctype);
                    var conditions = groups[ctype];

                    for (cond in conditions) {
                        var conditionName = conditions[cond];
                        //if (!conditionName in data.comparisons) {
                        //    continue;
                        //}
                        html_to_add += conditionRow(conditionName, ctype);
                    }
                    html_to_add += optGroupClose();
                    
                }
                conditionSelects.append(html_to_add);
                // Remove some condition types from only some selects
                $("#markers-select").children().remove("optgroup[label!='Cluster']");
                $("#planexp-dge-c1").children().remove("optgroup[label='Technical']");
                $("#planexp-dge-c2").children().remove("optgroup[label='Technical']");
                conditionSelects.selectpicker('refresh');
            },
            error: function(data) {
                console.log(data.responseText);
            }
        })
    }



    /**
     * fillCtypes
     *   Summary:
     *     Performs AJAX query to /experiment_condition_types,
     *     retrieving the condition types for a given experiment.
     *   Arguments:
     *     - Experiment name string
     *     - jQuery object of select objects to fill.
     *   Returns:
     *     - Nothing
     */
    fillCtypes = function(expName, ctypeSelects) {
        
        return $.ajax({
            type: "GET",
            url: window.ROOT + "/experiment_condition_types",
            data: {
                'experiment'    : expName,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                ctypeSelects.html(""); // clean previous HTML
                var first = true;
                var ctypes = data.ctypes;
                for (const ctype in ctypes) {
                    ctypeName = ctypes[ctype];
                    ctypeSelects.append(ctypeRow(ctypeName));
                    if (first) {
                        $('.condition-option[value="' + ctypeName + '"]').attr('selected', 'selected');
                        first = false;
                    }
                }
                
                var ctypesDge = data.ctypes_dge;
                first = true;
                $("#planexp-dge-ctype").html("");

                if (ctypesDge.length > 0) {
                    window.dgeAvailable = true;
                    for (const ctype in ctypesDge) {
                        ctypeName = ctypesDge[ctype];
                        $("#planexp-dge-ctype").append(ctypeRow(ctypeName));
                        if (first) {
                            $('.condition-option[value="' + ctypeName + '"]').attr('selected', 'selected');
                            first = false;
                        }
                    }
                } else {
                    // Hide DGE section... no condition type with DGE
                    window.dgeAvailable = false;
                }
                
                ctypeSelects.selectpicker('refresh');
            },
            error: function(data) {
                console.log(data.responseText);
            }
        })
    }

    /**
     * getDatasets
     *   Summary:
     *     
     *     
     *   Arguments:
     *    
     *   Returns:
     *    
     */
    getDatasets = function(expName, datasetSelect) {
        datasetRow = function(datasetName) {
            //<option data-content="<img class=" legend-db'="" src="/static/Images/legend-Adamidi.png">Adamidi' value='Adamidi'</option>


            //<option data-content="<img class='legend-db' src='{% static 'Images/' %}legend-{{ db.name }}.png'>{{ db.name }}" value="{{ db.name }}">{{ db.name }}</option>
            return "<option data-content='<img class=\"" +
                    "legend-db\" src=\"" +
                    window.ROOT + 
                    "/static/Images/legend-" + 
                    datasetName +
                    ".png\">" +
                    datasetName +
                    "'" +
                    " value='" +
                    datasetName +
                    "'" +
                    "</option>"; 
            //return "<option class='dataset-option' value='" + 
            //        datasetName + 
            //        "'>" + 
            //        datasetName + 
            //        "</option>";
        }

        return $.ajax({
            type: "GET",
            url: window.ROOT + "/experiment_dataset",
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


    showNecessaryCards = function() {
        if (currentExpType == expType['Single-Cell']) {
            $('#planexp-links').show(250);
            $('#planexp-links-toc').show(250);
        } else {
            $('#planexp-links-toc').hide();
            $('#planexp-links').hide();
        }

        // Show the necessary cards
        if (window.dgeAvailable) {
            $("#planexp-dge-table-container").show(250);
            $("#planexp-dge-table-container-toc").show(250);
            $('#planexp-dge-table-container-toc').css('display', 'inline-block');
        }

        $("#planexp-gene-expression").show(250);
        $("#planexp-gene-expression-toc").show(250);
        $('#planexp-gene-expression-toc').css('display', 'inline-block');
        $("#planexp-gene-coexpression").show(250);
        $('#planexp-gene-coexpression-toc').css('display', 'inline-block');
        $("#planexp-sample-counter").show(250);
        $("#planexp-sample-counter-toc").show(250);

        $("#planexp-network").show(250, function(){
            // Initialize cytoscape now that the container div is visible
            initCytoscape();
        });
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
        condition1 = condition1.replace(/ \(.+\)/, "");
        condition2 = condition2.replace(/ \(.+\)/, "");

        $("#dge-loading").show();
        targetDiv.hide();
        $.ajax({
            type: "GET",
            url: window.ROOT + "/experiment_dge_table",
            data: {
                'experiment': expName,
                'dataset'   : dataset,
                'condition1': condition1,
                'condition2': condition2,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (jQuery.isEmptyObject(data)) {
                    targetDiv.hide();
                    $("#dge-table-notfound").show(250);

                } else {
                    $("#dge-table-notfound").hide();
                    targetDiv.html(data.table);
                    targetDiv.hide();
                    targetDiv.show(250);
                    Plotly.newPlot("volcano-plot", data.volcano);
                }
                $("#dge-loading").hide();
            },
            error: function(data) {
                $("#dge-loading").hide();
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
    plotGeneExpression = function(expName, dataset, geneName, ctype, plotType, onlyToggle, plotDivId) {
        $("#expression-plot-loading").show();
        $("#" + plotDivId).html("");
        $.ajax({
            type: "GET",
            url: window.ROOT + "/plot_gene_expression",
            data: {
                'experiment': expName,
                'dataset'   : dataset,
                'gene_name' : geneName,
                'plot_type' : plotType,
                'ctype'     : ctype,
                'only'      : onlyToggle,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data) {
                    $("#plot-genenotfound").hide();
                    var thePlot = document.getElementById(plotDivId);
                    Plotly.newPlot(thePlot, data.data, data.layout);
                    if (plotType == "heatmap") {
                        thePlot.on('plotly_afterplot', function(){
                            Plotly.d3.selectAll(".yaxislayer-above").selectAll('text')
                                  .on("click", function(d) {
                                    getCard({ target: d.text, targetDB: dataset });
                            });
    
                        });
                    }
                    
                } else {
                    $("#plot-genenotfound").show(250);
                }
                $("#expression-plot-loading").hide();
            }
        });
    }
    plotGeneCoexpression = function(expName, dataset, gene1Name, gene2Name, ctype, plotDivId) {
        $("#coexpression-plot-loading").show();
        $("#" + plotDivId).html("");
        $.ajax({
            type: "GET",
            url: window.ROOT + "/plot_gene_coexpression",
            data: {
                'experiment': expName,
                'dataset'   : dataset,
                'gene1_name' : gene1Name,
                'gene2_name' : gene2Name,
                'ctype'     : ctype,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data) {
                    $("#coexpression-plot-genenotfound").hide();
                    var thePlot = document.getElementById(plotDivId);
                    Plotly.newPlot(thePlot, data.data, data.layout);
                } else {
                    $("#coexpression-plot-genenotfound").show(250);
                }
                $("#coexpression-plot-loading").hide();
            }
        });
    }

    /**
     * plotTSNE
     *   Summary:
     *     Performs AJAX query to /plot_tsne to 
     *     retrieve the data for the TSNE plot to pass it 
     *     to Plotly.
     *   Arguments:
     *     - Experiment name
     *     - Dataset
     *     - Gene name
     *     - jQuery object of div to plot.
     *     - withcolor: Bool to indicate if color dimension is necessary (i.e.: if we are plotting a gene).
     *     - Type of condition.
     *     - Id of the plot.
     *   Returns:
     *     - Nothing
     */
    plotTSNE = function(expName, dataset, geneName, withcolor, genePlotType, ctype, plotDivId, loadingDiv) {
        $("#" + loadingDiv).show();
        $("#" + plotDivId).html("");
        $.ajax({
            type: "GET",
            url: window.ROOT + "/plot_tsne",
            data: {
                'experiment': expName,
                'dataset'   : dataset,
                'gene_name' : geneName,
                'ctype'     : ctype,
                'withcolor' : withcolor,
                'gene_plot_type': genePlotType,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data) {
                    $("#plot-genenotfound").hide();
                    Plotly.newPlot(plotDivId, data.data, data.layout);
                } else {
                    $("#tsne-plot-genenotfound").show(250);
                }
                $("#" + loadingDiv).hide();
            }
        });

    }

    plotSampleCount = function(expName, dataset, geneName, ctype, conditions, plotDivId, loadingDiv) {
        $("#" + loadingDiv).show();
        $("#" + plotDivId).html("");
        $("#counter-plot-genenotfound").hide(250);
        $.ajax({
            type: "GET",
            url: window.ROOT + "/plot_sample_count",
            data: {
                'experiment' : expName,
                'dataset'    : dataset,
                'gene_name'  : geneName,
                'ctype'      : ctype,
                'conditions' : JSON.stringify(conditions),
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                $("#" + loadingDiv).hide();
                if (data) {
                    $("#counter-plot-genenotfound").hide(250);
                    $("#" + loadingDiv).hide();
                    $("#" + plotDivId).html(
                        '<a id="sample-count-plot-link" href="data:image/png;base64,' 
                        + data.plot
                        + '" download="sample_counts.png">'
                        + '<div class="btn btn-default btn-sample-count"><span class="glyphicon glyphicon-picture"> </span> Download Image</div> </a>'
                        + '<a id="sample-count-csv-link" href="data:text/plain;base64,'
                        + data.csv
                        + '" download="sample_counts.txt">'
                        + '<div class="btn btn-default btn-sample-count"><span class="glyphicon glyphicon-floppy-disk"> </span>Download CSV</div></a>'
                    );

                } else {
                    $("#counter-plot-genenotfound").show(250);
                    
                }

            },
            error: function(err) {
                $("#" + loadingDiv).hide();
                $("#" + plotDivId).html("");
                $("#counter-plot-genenotfound").show(250);
            }
        });
    }



    showConditionTypes = function(selectDivClass, ctype) {
        var ctype = ctype.replace(/ /g, "_");
        $("." + selectDivClass + " option").prop("selected", false);
        $("." + selectDivClass + " option").hide();
        $("." + selectDivClass + " " + "." + ctype).show();
        $("." + selectDivClass).selectpicker("refresh");
    }


    initCytoscape = function(graphelements="", layout="cola") {
        window.cy = cytoscape({
            style: window.stylesheet,
            layout: { name:  layout, animationDuration: 200 },
            container: document.getElementById('planexp-cyt'),
            elements: graphelements,
            wheelSensitivity: 0.25,
            hideEdgesOnViewport: true,
            ready: function() {}
        })
    }


   /**
    * Add JSON Graph to Cytoscape
    **/
   addJsonToCy = function(graphelements, layout="cola") {
        try {
            initCytoscape(graphelements, layout);
            cy.layout({'name': layout, animationDuration: 200});
            colorByCondition();
        }
        catch(err) {
            console.log(err);
            displayError("Incorrect graph definition");
        }
    }


    handleFileSelect = function(evt) {
        var files = evt.target.files; // FileList object
        // files is a FileList of File objects. List some properties.
        var output = [];
        var file = files[0];
        var format = "";
      
        // Read file
        var reader = new FileReader();
        reader.onload = function(){
          var graphelements;
          textfile = reader.result;
          // Check format
          if (evt.target.id == "import-json") {
            try {
              graphelements = JSON.parse(textfile);
              addJsonToCy(graphelements);
            }
            catch (err) {
              displayError("Incorrect JSON file.");
            }
          }

          // Close overlay
          $('.card-overlay-netcell-uploadgraph').slideToggle(450);
          $('.close-overlay-uploadgraph').slideToggle(450);
      
        };
        reader.readAsText(file);
    }


    /**
     * changeNetworkColor
     *   Summary:
     *     Changes the color gradient of the displayed network.
     *   Arguments:
     *     - Color gradient picked.
     *   Returns:
     *     - Nothing
     */
    changeNetworkColor = function(element) {
        $("#" + $(element).parent().attr("id") + " .color-pick").removeClass("active");
        $(element).addClass("active");
    }
      

    /**
     * colorByCondition
     *   Summary:
     *     Changes the color of the nodes in the graph according to the 
     *     expression values. Will call colorOneCondition or colorTwoConditions
     *     depending on the active panel.
     *   Arguments:
     *     - None
     *     
     *   Returns:
     *     - Nothing
     */
    colorByCondition = function() {
        var mode = $("#color-by li.active").attr("id"); 
        if (mode == "one-sample-nav") {
            colorOneCondition();
        } else {
            colorTwoConditions();
        }

    }


    /**
     * colorTwoCondition
     *   Summary:
     *     Maps expression of Two conditions to the network
     *   Arguments: 
     *     - None
     *   Returns:
     *     - Nothing
     */
    colorTwoConditions = function() {
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var condition1 = $("#network-color-condition1").val();
        var condition2 = $("#network-color-condition2").val();
        condition1 = condition1.replace(/ \(.+\)/, "");
        condition2 = condition2.replace(/ \(.+\)/, "");
        var cprofile = $("#two-sample .color-pick.active").attr("id");
        
        var gene_symbols = [];
        for (var i = 0; i < cy.nodes().length; i++) {
            gene_symbols.push( cy.nodes()[i].data("id") );
        }
        gene_symbols = gene_symbols.join(",");

        if (!expName || !dataset || !condition1 || !condition2 || !cprofile || !gene_symbols) {
            return;
        }

        $("#planexp-cyt-legend").html(""); // Removing legend


        $.ajax({
            type: "POST",
            url: window.ROOT + "/map_expression_two",
            data: {
                'experiment'    : expName,
                'dataset'       : dataset,
                'condition1'    : condition1,
                'condition2'    : condition2,
                'symbols'       : gene_symbols,
                'profile'       : cprofile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                var colormap = data.colormap;
                $("#planexp-cyt-legend").html(data.legend);
                cy.filter(function(i, element){
                    if ( element.isNode() ) {
                        if (element.data("name") in colormap) {
                            element.css("background-color", colormap[element.data("id")]);
                        } else {
                            element.css("background-color", "#000000");
                        }
                    }
                });
            },
            error: function(data) {
                $("#planexp-cyt-legend").html(""); // Removing legend
                console.log(data.responseText);
            }
        });
    }



    /**
     * colorOneCondition
     *   Summary:
     *     Maps expression of one condition to the network
     *   Arguments: 
     *     - None
     *   Returns:
     *     - Nothing
     */
    colorOneCondition = function() {
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var condition = $("#network-color-conditions").val();
        condition = condition.replace(/ \(.+\)/, "");
        var cprofile = $("#one-sample .color-pick.active").attr("id");
        var creference = $("input[name='color-reference']:checked").val()
        var gene_symbols = [];
        for (var i = 0; i < cy.nodes().length; i++) {
            gene_symbols.push( cy.nodes()[i].data("id") );
        }
        gene_symbols = gene_symbols.join(",");

        if (!expName || !dataset || !condition || !cprofile || !creference || !gene_symbols) {
            return;
        }

        $("#planexp-cyt-legend").html(""); // Removing legend


        $.ajax({
            type: "POST",
            url: window.ROOT + "/map_expression_one",
            data: {
                'experiment'    : expName,
                'dataset'       : dataset,
                'condition'     : condition,
                'symbols'       : gene_symbols,
                'profile'       : cprofile,
                'reference'     : creference,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                var colormap = data.colormap;
                $("#planexp-cyt-legend").html(data.legend);
                cy.filter(function(i, element){
                    if ( element.isNode() ) {
                        if (element.data("name") in colormap) {
                            element.css("background-color", colormap[element.data("id")]);
                        } else {
                            element.css("background-color", "#000000");
                        }
                    }
                });
            },
            error: function(data) {
                $("#planexp-cyt-legend").html(""); // Removing legend
                console.log(data.responseText);
            }
        });
    }

    /**
     * getRegulatoryLinksTable
     *   Summary:
     *     Retrieves table with regulatory links for experiment if available
     *   Arguments: 
     *     - None
     *   Returns:
     *     - Nothing, fills html of table.
     */
    var getRegulatoryLinksTable = function(searchTerm, mode, tableId) {
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        $("#planexp-links-loading").show();

        $.ajax({
            type: "GET",
            url: window.ROOT + "/regulatory_links",
            data: {
                'experiment'    : expName,
                'dataset'       : dataset,
                'mode'          : mode,
                'search_term'   : searchTerm,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                if (data != "None") {
                    $("#" + tableId).html(data).promise().done(function(){
                        $("#planexp-links-table").DataTable().destroy();
                        $("#planexp-links-table").DataTable({
                            "order": [[ 7, "desc" ], [ 6, "desc" ]]
                        });
                        window.linksTable = $("#planexp-links-table").DataTable();
    
                        $("#send-to-network").on("click", function(){
                            sendToNetwork(window.linksTable);
                        });
            
                        $("#download-links-table").on("click", function(){
                            downloadCSV(window.linksTable);
                        });
                        $("#" + tableId).show(250);
                    });
                    
                    
                    
                } else {
                    $("#" + tableId).hide(250);
                    $("#planexp-links-error").show(250); 
                    setTimeout(function(){$("#planexp-links-error").hide(250); }, 3000);
                }
                $("#planexp-links-loading").hide();
            },
            error: function(data) {
                console.log(data.responseText);
                $("#planexp-links-loading").hide();
            }
        });
    }


    /**
     * getClusterMarkers
     *   Summary:
     *     Retrieves table with markers for each cluster
     *   Arguments: 
     *     - None
     *   Returns:
     *     - Nothing, fills html of table.
     */
    var getClusterMarkersTable = function(tableId, experiment, dataset, cluster) {

        $.ajax({
            type: "GET",
            url: window.ROOT + "/cluster_markers",
            data: {
                'experiment'    : experiment,
                'dataset'       : dataset,
                'cluster'       : cluster,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                if (data != "None") {
                    $("#markers-table-notfound").hide();
                    $(tableId).hide()
                    $(tableId).html(data);
                    $(tableId).show(250);
                } else {
                    $(tableId).html("");
                    $("#markers-table-notfound").show(250);


                }
            },
            error: function(data) {
                console.log(data.responseText);
            }
        });

    }


    function stripHtml(html) {
        var tmp = document.createElement("DIV");
        tmp.innerHTML = html;
        tmp.textContent = tmp.textContent.split("\n").join("");
        tmp.textContent = tmp.textContent.replace("Show pathways", "");
        return tmp.textContent.trim() || tmp.innerText.trim() || "";
    }

    /**
     * sendToNetwork
     *   Summary:
     *     Sends regulatory links table to network viewer in planexp
     *   Arguments: 
     *     - None
     *   Returns:
     *     - Nothing, fills html of table.
     */
    window.sendToNetwork = function(dt) {
        $.scrollTo("#planexp-network", 500);
        var toImport = { 'nodes': [], 'edges': [] };
        dt.rows({filter:"applied"}).eq(0).each( function ( index ) {
            var row = dt.row( index );
            var data = row.data();
            toImport.nodes.push({ data: { id: stripHtml(data[0]), name: stripHtml(data[0]), homolog: stripHtml(data[2]), colorNODE: "#404040" } });
            toImport.nodes.push({ data: { id: stripHtml(data[3]), name: stripHtml(data[3]), homolog: stripHtml(data[5]), colorNODE: "#404040" } });
            toImport.edges.push({ data: { 
                    source: stripHtml(data[0]), 
                    target: stripHtml(data[3]), 
                    colorEDGE: "#a5b8ff", 
                    type: "geneLink" 
                }
            });
        });

        toImport.nodes = [ ... new Set(toImport.nodes)];
        addJsonToCy(toImport, "cola");

    }

    window.downloadCSV = function(dt) {
        var data = dt.data().toArray();
        data = data.map( function(row) { return  row.map(stripHtml) });
        data = data.join("\n");
        data = data.split("• ").join("");
        
        var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
        saveAs(blob, "gene-coexpression-links.csv"); 
    }


    var filterNetwork = function(expName, dataset, inclusiveFlag, conditions, nodeIds) {

        $.ajax({
            type: "GET",
            url: window.ROOT + "/filter_network",
            data: {
                'experiment' : expName,
                'dataset'    : dataset,
                'inclusive_flag': inclusiveFlag,
                'conditions' : JSON.stringify(conditions),
                'node_ids'   : JSON.stringify(nodeIds),
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                if (data) {
                    cy.elements().css('opacity', 0.05);
                    cy.batch(function(){
                        cy.filter(function(i, element){
                            if ( element.isNode() ) {
                                if (data.includes(element.data("id"))) {
                                    element.css('opacity', 1);
                                } else {
                                    element.css('opacity', 0.05);
                                }
                            
                            } else {
                                if (data.includes(element.data("source")) && data.includes(element.data("target"))) {
                                    element.css('opacity', 1);
                                } else {
                                    element.css('opacity', 0.05);
                                }
                            }
                        });
                    });
                } else {
                    console.log("no data...");
                    cy.elements().css('opacity', 1);
                }
                
            },
            error: function(data) {
                cy.elements().css('opacity', 1);
            }
        });
    }


    var changeLabels = function(cyobj) {
        var newLabel = $("#change-labels input:checked").val();
        if (newLabel == "human") {
            cyobj.nodes().addClass('human-label');
        } else {
            cyobj.nodes().removeClass('human-label');
        }
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

        window.experimentPromise = new Promise((resolve, reject) => {
            var expName = $(this).val();
            experimentSummary(expName, $("#planexp-summary"));
            getDatasets(expName, $("#select-dataset"));
            fillConditions(expName, $("select.condition-select"));
            var fillCtypesPromise = fillCtypes(expName, $("select.ctype-select"));

            // Hide and show on change 
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
            $("#planexp-sample-counter-toc").hide();

            try {
                cy.nodes().remove();
            } catch {
                // nothing to do
            }
            fillCtypesPromise.then(resolve(1));
        });

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
        $("#coexpression-plot").html("");
        $("#tsne-plot-gene").html("");
        $("#tsne-plot-condition").html("");
        $("#volcano-plot").html("");
        $("#plot-genenotfound").hide();
        $("#counter-plot-genenotfound").hide();  
        $("#planexp-goea-condition").html("");
        $("#planexp-goea-condition").selectpicker("refresh");
        $("#goea-results").html("");
        $("#planexp-links-table-container").html("");

        
        // Change DGE table ConditionType select
        // only when experiment is correctly selected
        window.experimentPromise.then(function(){
            var ctype = $("#planexp-dge-ctype").val();
            if (ctype) {
                showConditionTypes("dge-table-condition-selects", ctype);
            }
            
            // Change Network ConditionType select
            var ctype = $("#network-ctype").val();
            showConditionTypes("network-condition-selects", ctype);
    
            // Change Sample counter
            var ctype = $("#counter-ctype").val();
            showConditionTypes("counter-condition-selects", ctype);

            showNecessaryCards();
        })
        
    });



    /**
     * Select Condition for DGE table
     *   Summary:
     *     Handles the selection of the conditions for the.
     *     DGE table.
     */
    $("select.dge-table-condition-selects").on("change", function(){
        var expName = $("#select-experiment").val();
        var condition1 = $("#planexp-dge-c1").val().replace(/ \(.+\)/, "");
        var condition2 = $("#planexp-dge-c2").val().replace(/ \(.+\)/, "");
        var dataset = $("#select-dataset").val();
        $("#planexp-goea-condition").html("");
        $("#planexp-goea-condition").selectpicker("refresh");
        $("#goea-results").html("");

        if (condition1 && ! condition2) {
            var availableComparisons = window.comparisons[condition1];
            // Condition1 provided, must hide some condition2
            $("#planexp-dge-c2 option").prop("selected", false);
            $("#planexp-dge-c2 option").hide();
            if (availableComparisons) {
                $("#planexp-dge-c2 option").filter(function(){
                    if (availableComparisons.indexOf($(this).val().replace(/ \(.+\)/, "")) == -1) {
                        return false;
                    } else {
                        return true;
                    }
                }).show();
            }
            $("#planexp-dge-c2").selectpicker("refresh");
        } else if (condition1 && condition2) {
            var availableComparisons = window.comparisons[condition1];
            if (! availableComparisons) {
                $("#planexp-dge-c2 option").prop("selected", false);
                $("#planexp-dge-c2 option").hide();
                $("#planexp-dge-c2").selectpicker("refresh");
                return;
            } else if (availableComparisons.indexOf(condition2) == -1) {
                $("#planexp-dge-c2 option").prop("selected", false);
                $("#planexp-dge-c2 option").hide();
                $("#planexp-dge-c2 option").filter(function(){
                    if (availableComparisons.indexOf($(this).val().replace(/ \(.+\)/, "")) == -1) {
                        return false;
                    } else {
                        return true;
                    }
                }).show();
                $("#planexp-dge-c2").selectpicker("refresh");
                return;
            } else {
                $("#planexp-dge-c2 option").hide();
                $("#planexp-dge-c2 option").filter(function(){
                    if (availableComparisons.indexOf($(this).val().replace(/ \(.+\)/, "")) == -1) {
                        return false;
                    } else {
                        return true;
                    }
                }).show();
                $("#planexp-dge-c2").selectpicker("refresh");
            }
        } 
        
        if ( ! condition1 || ! condition2 ) {
            return;
        } 
        
        // Clean volcano plot 
        $("#volcano-plot").html("");
        experimentDGETable(expName, dataset, condition1, condition2, $("#planexp-dge-table"));

        $("#planexp-goea-condition").append(conditionRow(condition1, ""));
        $("#planexp-goea-condition").append(conditionRow(condition2, ""));
        $("#planexp-goea-condition").selectpicker("refresh");

    });


    $("#run-goea").on("click", function() {
        var expName = $("#select-experiment").val();
        var condition1 = $("#planexp-dge-c1").val().replace(/ \(.+\)/, "");
        var condition2 = $("#planexp-dge-c2").val().replace(/ \(.+\)/, "");
        var conditionFocus = $("#planexp-goea-condition").val();
        var dataset = $("#select-dataset").val();
        
        if (!expName || !condition1 || !condition2 || !conditionFocus || !dataset) {
            return;
        }

        
        // Show loading and remove images
        $("#goea-loading").show();
        $(".goea-plot").remove();
        $.ajax({
            type: "GET",
            url: window.ROOT + "/get_goea",
            data: {
                'experiment'    : expName,
                'dataset'       : dataset,
                'condition1'    : condition1,
                'condition2'    : condition2,
                'condition_focus': conditionFocus,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                // Change Exp type
                $("#goea-loading").hide();
                $("#goea-results").html(data.html);

            },

            error: function(data) {
                $("#goea-loading").hide();
                console.log(data.responseText);
            }
        });



    });

    $('body').on('click', "#download-go-csv", function() {
        var data = $(this).attr("data");
        var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
        saveAs(blob, "gene-ontology.csv"); 
    });


    /**
     * Get Gene Expression Plot
     *   Summary:
     *     Plots gene expression 
     */
    $("#plot-expression-btn").on("click", function() {
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var geneName = $("#gene-expression-search").val();
        var ctype    = $("#gene-expression-ctype").val();
        var plotType = $("#gene-expression-plot-type").val();
        var onlyToggle = $("#gene-expression-expressed").prop("checked");

        if (!geneName) {
            $("#plot-genenotfound").show(250);
            return;
        }
        $("#plot-genenotfound").hide();
        plotGeneExpression(expName, dataset, geneName, ctype, plotType, onlyToggle, "expression-plot");
    })


    $("#plot-coexpression-btn").on("click", function(){
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var gene1Name = $("#gene-coexpression-1").val();
        var gene2Name = $("#gene-coexpression-2").val();
        var ctype    = $("#coexpression-ctype").val();

        if (!gene1Name || !gene2Name) {
            return;
        }
        $("#coexpression-plot-genenotfound").hide();

        plotGeneCoexpression(expName, dataset, gene1Name, gene2Name, ctype, "coexpression-plot");
    });


    $("#gene-expression-ctype").on("change", function(){
        if ($(this).val() == "Samples") {
            $("#gene-expression-plot-type option").attr("disabled", "true");
            $("#gene-expression-plot-type option").prop('selected', false);
            $("#gene-expression-plot-type option[value='heatmap']").removeAttr('disabled');
            $("#gene-expression-plot-type option[value='heatmap']").prop('selected', true);
            $("#gene-expression-expressed-container").hide();
        } else {
            $("#gene-expression-plot-type option").removeAttr('disabled');
        }
        $("#gene-expression-plot-type").selectpicker("refresh");
    });

    $("#gene-expression-plot-type").on("change", function(){
        if (currentExpType == expType['Single-Cell']) {
            if ($(this).val() == "violin") {
                $("#gene-expression-expressed-container").show();
            } else {
                $("#gene-expression-expressed-container").hide();
            }
        } 
    });



    $("#planexp-dge-ctype").on("change", function(){
        var ctype = $("#planexp-dge-ctype").val();
        showConditionTypes("dge-table-condition-selects", ctype);
    });


    $(".plot-tsne-btn").on("click", function() {
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var geneName = $("#tsne-search").val();
        var ctype    = $("#tsne-ctype").val();
        var genePlotType = $('input[name="planexp-tsne-search-type"]:checked').val();
        var activePanel = $("#planexp-tsne .tab-content .tab-pane.active");
        var withcolor = false;
        var plotDiv = "tsne-plot-condition";
        var loadingDiv = "tsne-plot-condition-loading";
        if (activePanel.attr('id') == "tsne-gene-tab") {
            withcolor = true;
            ctype = "Cluster";
            plotDiv = "tsne-plot-gene";
            loadingDiv = "tsne-plot-gene-loading";
            if (!geneName) {
                $("#tsne-plot-genenotfound").show(250);
                return;
            }
        }
        
        $("#tsne-plot-genenotfound").hide();

        plotTSNE(expName, dataset, geneName, withcolor, genePlotType, ctype, plotDiv, loadingDiv);
    });


    $(".sample-counter-btn").on("click", function(){
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var geneName = $("#counter-search").val();
        var ctype    = $("#counter-ctype").val();
        var conditions = $("#counter-conditions").val();
        var plotDiv = "counter-btns";
        var loadingDiv = "counter-plot-loading";

        if (!geneName || !conditions) {

            $("#counter-plot-genenotfound").show(250);
            return;
        }

        plotSampleCount(expName, dataset, geneName, ctype, conditions, plotDiv, loadingDiv)

    });


    $("#links-submit-btn").on("click", function(){
        var expName  = $("#select-experiment").val();
        var dataset  = $("#select-dataset").val();
        var geneName = $("#links-gene-search").val();
        var reactomeId = $("#links-reactome-search").val();
        var mode = $("#link-tabs li.active").attr("id"); 

        if (mode == "links-gene-symbol-li") {
            getRegulatoryLinksTable(geneName, "gene", "planexp-links-table-container");
        } else {
            getRegulatoryLinksTable(reactomeId, "reactome", "planexp-links-table-container");
        }

    })



    // SCROLL BEHAVIOUR
    $(".planexp-toc-link").on("click", function(event){
        event.preventDefault();
        $.scrollTo($(this).attr("href"), 500);

    });

    // SAMPLE COUNTER CONDITIONS
    $("#counter-ctype").on("change", function(){
        var ctype = $("#counter-ctype").val();
        showConditionTypes("counter-condition-selects", ctype);
    });

    // NETWORK CONDITIONS
    $("#network-ctype").on("change", function(){
        var ctype = $("#network-ctype").val();
        showConditionTypes("network-condition-selects", ctype);
    });

    // IMPORT NETWORK
    $(function(){
        document.querySelector("#import-json").addEventListener('change', handleFileSelect, false);
    });

    // NETWORK BUTTONS
    // CENTER
    $("#planexp-cyt-center").on("click", function() { cy.center(); cy.fit(); });

    

    // EXPORT
    $("#planexp-cyt-export").on("click", function() { 
        var jsonGraph = JSON.stringify(cy.json().elements);
        var blob = new Blob([jsonGraph], {type: "text/plain;charset=utf-8"});
        saveAs(blob, "graph-export.json"); 
    });

    // SAVE IMAGE
    $("#planexp-cyt-save").on("click",   function() { 
        var graph_png = cy.png(); 
        $('#save-image-link').attr('href', graph_png); 
    });
    
    // DELETE
    $("#planexp-cyt-delete").on("click", function() { 
        $( "#dialog-confirm" ).dialog({
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            buttons: {
                Cancel: function() {
                    $( this ).dialog( "close" );
                },
                "Delete graph": function() {
                    cy.nodes().remove();
                    $( this ).dialog( "close" );
                }
            }

        })

     });

     // CHANGE LAYOUT
     $("#planexp-cyt-layout").on("change", function() {
        cy.layout({ name: $(this).val().toLowerCase() });
     });

    // NETWORK COLOR
    $(".color-pick").on("click", function() { 
        changeNetworkColor(this);
        colorByCondition();
    });

    // Reference
    $("input[type='radio'][name='color-reference']").on("change", function(){
        colorByCondition();
    });


    // Changing condition dropdowns
    $("#network-color-conditions").on("change", function(){
        colorByCondition();
    });

    $("#network-color-condition1").on("change", function(){
        colorByCondition();
    });
    
    $("#network-color-condition2").on("change", function(){
        colorByCondition();
    });


    // Markers table
    $("#markers-select").on("change", function(){
        var expName = $("#select-experiment").val();
        var dataset = $("#select-dataset").val();
        var cluster = $(this).val()

        getClusterMarkersTable("#planexp-markers-table-container", expName, dataset, cluster);

    });

    
    // FILTER NETWORK
    $("#planexp-filter-network").on("click", function(){
        var expName = $("#select-experiment").val();
        var dataset = $("#select-dataset").val();
        var networkConditions = $("#network-conditions").val();
        var nodes = cy.nodes();
        var booleanAndOr = $("input[name='fiter-network-andor']:checked").val();
        var nodeIds = [];
        for (var i = 0; i < nodes.length; i++) {
            nodeIds.push( nodes[i].data("id") );
        }
        
        filterNetwork(expName, dataset, booleanAndOr, networkConditions,nodeIds);

        //console.log(networkConditions);
        //console.log(minExp);

        // AJAX REQUEST TO GET LIST OF GENES THAT SHOULD BE DISPLAYED



    });


    // NETWORK EDITOR
    // -----------------------------------
    // EDIT

    // EDIT GRAPH DIALOG
    $("#close-edit-graph").on("click", function(){
        $("#edit-graph-dialog").hide(250);
     });

    $("#planexp-cyt-edit").on("click",   function() { 
        $("#edit-graph-dialog").show(250, function() {
            window.theEditor = new CyEditor('cytoscape-editor', cy);

            theEditor.cytoscape.edgehandles({
                toggleOffOnLeave: true,
                handleNodes: "node",
                handleSize: 10,
                handlePosition:'middle top', // sets the position of the handle in the format of "X-AXIS Y-AXIS" such as "left top", "middle top"
                edgeType: function() {
                    return 'flat';
                }
            });
        });
    });

    $("#editor-add-node-btn").on("click", function() {
        var nodeToAdd = $("#editor-add-node-text").val();
        var homologToAdd = $("#editor-add-node-homolog").val();
        theEditor.addNode(nodeToAdd, homologToAdd);
    });

    $(".editor-switch").on("change", function(){
        var currValue = $("input:checked", this).val();
        if (currValue == "on") {
            // Change all other editor switches to OFF.
            var currInputOff = $("input[value=off]", this);
            $("input[value=off]", ".editor-switch").not(currInputOff).prop("checked", true);
        }
    });

    $("#editor-cancel").on("click", function(){
        $("#edit-graph-dialog").hide();
    })

    $("#editor-save").on("click", function(){
        if (theEditor.cytoscape.elements()) {
            cy.nodes().remove();
            cy.add( JSON.parse(JSON.stringify(theEditor.cytoscape.elements().jsons())));
            cy.layout({'name': 'cola'});
            $("#edit-graph-dialog").hide();
        }
        
        colorByCondition();
    })

    $( "#planexp-cyt-legend" ).tooltip({
        track: true,
        content: function(){
            return $(this).attr("title");
        }
    });

    $( document ).on({
        mouseenter: function () {
            //stuff to do on mouse enter
            $('.grid-legend').css('opacity', 0.5);
            $('.grid-legend').css('cursor', 'pointer');
            $(this).css('opacity', 1);
            var color = rgb2hex($(this).css('background-color')).toUpperCase();
            cy.elements().css('opacity', 0.05);
            cy.batch(function(){
                cy.filter(function(i, element){
                    if ( element.isNode() ) {
                        var nodeColor = element.css("background-color").toUpperCase();
                        if (nodeColor.length == 4) {
                        // short hex
                        nodeColor = nodeColor[0] + nodeColor[1] + nodeColor[1] + nodeColor[2] + nodeColor[2] + nodeColor[3] + nodeColor[3];
                        }
                        if (nodeColor == color) {
                            element.css('opacity', 1);
                        } else {
                        }

                    }
                });
            });
        },
        mouseleave: function () {
            //stuff to do on mouse leave
            $('.grid-legend').css('opacity', 1);
            cy.elements().css("opacity", 1);
        }
    }, ".grid-legend"); //pass the element as an argument to .on

 

    $('#color-by a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        colorByCondition();
        $("#planexp-cyt-legend").html(""); // Removing legend
    });
     


    // AUTOCOMPLETE FOR GENE SYMBOL SEARCH
    $("#gene-expression-search").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });

    // AUTOCOMPLETE FOR LINKS GENE SYMBOL SEARCH
    $("#links-gene-search").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });


    $("#links-reactome-search").autocomplete({
        source: function (request, response) {
            autocompleteReactome(extractLast(request.term), response);
        },
        minLength: 6,
        focus: function() {
            // prevent value inserted on focus
            return false;
        },
        select: function( event, ui ) {
            var terms = splitSearch( this.value );
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push( ui.item.value );
            // add placeholder to get the comma-and-space at the end
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
        }
    });

    $("#tsne-search").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });

    $("#counter-search").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });


    $("#gene-coexpression-1").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });

    $("#gene-coexpression-2").autocomplete({
        source: function (request, response) { 
            autocompleteContig(extractLast( request.term ), response);
        
        },
        minLength: 2,
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = splitSearch( this.value );
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push( ui.item.value );
                // add placeholder to get the comma-and-space at the end
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
    });





    $("#editor-add-node-text").autocomplete({
        source: function (request, response) { 
            autocompleteContig(request.term, response);
        
        },
        minLength: 2
            
    });
    $(".ui-autocomplete").css("z-index", "2147483647");

    
});
