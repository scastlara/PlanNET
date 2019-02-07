// CYTOSCAPE DEFINITION FOR PLANEXP



// Cytoscape variable definition
$( document ).ready(function() {

// Cytoscape style definition
    window.stylesheet = cytoscape.stylesheet()
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
            "border-color": "data(colorNODE)",
            "border-width": 2,
            "min-zoomed-font-size": 4,
        })
    .selector('.important')
        .css({
            "text-outline-color": "#404040",
            "color": "#FFFFFF",
        })
    .selector('edge')
        .css({
            'line-color': '#9d6cc1',
            'target-arrow-color': '#9d6cc1',
            'width': 3
        })
    .selector('edge[colorEDGE]')
        .css({
            'content': 'data(probability)',
            'font-size': 6,
            'width': 2,
            'color': "#404040",
            'text-background-opacity': 1,
            'text-background-color': '#F8F8F8',
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#404040',
            'text-border-width': 0.1,
            'text-border-opacity': 0.5,
            'line-color': 'data(colorEDGE)',
            'target-arrow-color': 'data(colorEDGE)',
            "min-zoomed-font-size": 6,
        })
    .selector('edge[colorEDGE]edge[type = "homology"]')
        .css({
            'line-style': 'dashed',
            'content': '',
            'opacity': 0.8
        })
    .selector('edge[colorEDGE]edge[type = "homologyInt"]')
        .css({
            'content': '',
            'opacity': 0.8
        })
    .selector('node[database != "Human"]')
        .css({
            'width': '15',
            'height': '15',
        })
    .selector('node[database = "Custom"]')
        .css({
            'border-color': "#ddadad",

        })
    .selector('node[database = "Smest"]')
        .css({
            'shape': 'circle',
            'border-color': "#bb4ab7",
        })
    .selector('node[database = "Cthulhu"]')
        .css({
            'shape': 'circle',
            'border-color': "#49b9d1",
        })
    .selector('node[database = "Consolidated"]')
        .css({
            'shape': 'circle',
            'border-color': "#74be47",
        })
    .selector('node[database = "Dresden"]')
        .css({
            'shape': 'circle',
            'border-color': "#ca552d",

        })
    .selector('node[database = "Graveley"]')
        .css({
            'shape': 'circle',
            'border-color': "#4b8c38",
        })
    .selector('node[database = "Illuminaplus"]')
        .css({
            'shape': 'circle',
            'border-color': "#b175e3",
        })
    .selector('node[database = "Newmark"]')
        .css({
            'shape': 'circle',
            'border-color': "#bcb042",
        })
    .selector('node[database = "Smed454"]')
        .css({
            'shape': 'triangle',
            'border-color': "#de9640",

        })
    .selector('node[database = "Adamidi"]')
        .css({
            'shape': 'circle',
            'border-color': "#648ad0"

        })
    .selector('node[database = "Blythe"]')
        .css({
            'shape': 'circle',
            'border-color': "#d34057"
        })
    .selector('node[database = "Pearson"]')
        .css({
            'shape': 'circle',
            'border-color': "#5fc38f"
        })
    .selector('node[database = "Gbrna"]')
        .css({
            'shape': 'circle',
            'border-color': "#818941"
        })
    .selector('.highlighted')
        .css({
            'background-color': '#F9FFBD',
            'shape': 'star'
        })
    .selector('node[database = "Human"]')
        .css({
            'width': 20,
            'height': 20,
            'shape': 'diamond',
            'background-color': '#6785d0',
        })
    .selector('.human-label')
        .css({
            'content': 'data(homolog)',
            'color': '#6785D0',
        })
    .selector('.important.human-label')
        .css({
            'content': 'data(homolog)',
            'text-outline-color': '#6785D0',
            'color': '#ffffff',

        });
        
    window.cy = cytoscape({
        style: stylesheet,
        layout: { name: 'random' },
        container: document.getElementById('planexp-cyt'),
        wheelSensitivity: 0.25,
        ready: function() {}
    })
});

