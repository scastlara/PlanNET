/* 
 * CYTOSCAPE EDITOR FOR PLANNET
 * ------------------------------------------------
 */


class CyEditor {
    constructor(containerId, cyInput=null, stylesheet=null) {
        if (! stylesheet) {
            console.log("No stylesheet...");
            stylesheet = cyInput.style();
        }
        console.log("Init graph...");
        try {
            this.cytoscape = cytoscape({
                container: document.getElementById(containerId),
                elements: JSON.parse(JSON.stringify(cyInput.elements().jsons()))
            });
            console.log(this.cy);
        } catch (error) {
            console.log(error);   
        }
        
    }
}

