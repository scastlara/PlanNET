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
                    });
        }
        console.log("Init graph...");
        console.log(cyEditorStyle);
        try {
            this.cytoscape = cytoscape({
                container: document.getElementById(containerId),
                elements: JSON.parse(JSON.stringify(cyInput.elements().jsons())),
                layout: { name: 'preset' },
                positions: cyInput.nodes().positions(),
                style: cyEditorStyle
            });
            console.log(this.cy);
        } catch (error) {
            console.log(error);   
        }
        
    }
}

