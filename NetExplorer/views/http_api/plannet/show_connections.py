from ...helpers.common import *


def show_connections(request):
    """
    Returns connections for a given set of nodes ina  graph.
    
    Accepts:
        * **GET + AJAX**

    Args:
        nodes (`str`): Node symbols separated by commas.
        databases (`str`): Databases for nodes separated by commas (same order).

    Response:
        * **GET + AJAX**:
           * **str**: serialized :obj:`GraphCytoscape`.

    """
    if request.is_ajax():
        nodes_including = request.POST['nodes'].split(",")
        databases       = request.POST['databases'].split(",")
        graphelements   = GraphCytoscape()
        for symbol, database in zip(nodes_including, databases):
            graphelements.add_node( PlanarianContig(symbol, database, query=False) )
        graphelements.get_connections()
        return HttpResponse(graphelements, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')