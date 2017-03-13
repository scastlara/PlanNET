// Count nodes
function countNodes(cyto) {
    var nodes = cyto.elements('node[database != "Human"]');
    var count = nodes.length;
    if (count >= 150) {
        count = "<span class='text-danger'>" + count + " <span class='glyphicon glyphicon-warning-sign'></span></span>";
    }
    $("#node-count").html(count);
}
