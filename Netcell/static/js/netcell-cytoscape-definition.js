// CYTOSCAPE DEFINITION FOR NET EXPLORER

// Cytoscape style definition
var stylesheet = cytoscape.stylesheet()
    .selector('node')
        .css({
            'content': 'data(name)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'background-color': '#404040',
            "font-size": 8,
            'text-outline-width': 2,
            "text-outline-color": "#FFFFFF",
            "color": "#404040",
            "border-color": "#FFFFFF",
            "border-width": 2,
            "min-zoomed-font-size": 6,
        })
    .selector('.highlighted')
        .css({
            'background-color': '#F9FFBD',
            'shape': 'star',
            'border-color': "#404040"
        })
    .selector('.semihidden0')
        .css({
            'background-color': "#dedede",
            'color': "#dedede"
        })
    .selector('.semihidden1')
        .css({
            'background-color': "#dedede",
            'color': "#dedede"
        })
    .selector('.semihidden2')
        .css({
            'background-color': "#dedede",
            'color': "#dedede"
        })
    .selector('edge')
        .css({
            'content': 'data(probability)',
            'font-size': 6,
            'width': 1,
            'color': "#404040",
            'text-background-opacity': 1,
            'text-background-color': '#F8F8F8',
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#404040',
            'text-border-width': 0.1,
            'text-border-opacity': 0.5,
            'line-color': '#404040',
            'target-arrow-color': '#FFFFFF',
            "min-zoomed-font-size": 6,
});



// Cytoscape variable definition
var cy = cytoscape({
    style: stylesheet,
    layout: { name: 'preset' },
    container: document.getElementById('cyt'),
    ready: function() {}
});
