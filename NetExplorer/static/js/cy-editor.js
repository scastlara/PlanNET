/* 
 * CYTOSCAPE EDITOR FOR PLANNET
 * ------------------------------------------------
 */




class CyEditor {
    constructor(containerId, cyInput=null, stylesheet=null) {

        if (! stylesheet) {
            console.log("No stylesheet...");
            var cyEditorStyle =  cytoscape.stylesheet()
                .selector('node')
                    .css({
                        'content': 'data(name)',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'background-color': '#404040',
                        "font-size": 12,
                        'text-outline-width': 2,
                        "text-outline-color": "#FFFFFF",
                        "color": "#404040",
                        "border-color": "data(colorNODE)",
                        "border-width": 2,
                        "min-zoomed-font-size": 2,
                    })
                .selector('node[database = "Custom"]')
                    .css({
                        'background-color': "#E7E7E7"
                    })    
                ;
        }
        console.log("Init graph...");
        console.log(cyEditorStyle);
        try {
            this.cytoscape = cytoscape({
                container: document.getElementById(containerId),
                elements: JSON.parse(JSON.stringify(cyInput.elements().jsons())),
                layout: { name: 'preset' },
                positions: cyInput.nodes().positions(),
                wheelSensitivity: 0.25,
                style: cyEditorStyle
            });
            console.log(this.cy);
        } catch (error) {
            console.log(error);   
        }
        
    }

    addNode(name, homolog) {
        var error = null;
        if (!name) {
            error = "Name must be provided.";
            return error;
        }

        var json_data = { 
            'nodes': [ 
                {
                    'data': { 
                        'id': name, 'name': name, 'database': 'Custom', 'colorNODE': "#404040" 
                    },
                }
            ] 
        };
        if (homolog) {
            json_data.nodes[0].data.homolog = homolog;
        };

        this.cytoscape.add(json_data);
        this.cytoscape.layout({
            name: 'cola',
            maxSimulationTime: 3000,
            fit: true,
            directed: false,
            padding: 40
        });
    }
}

