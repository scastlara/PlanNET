from .common import *

def get_card(request, symbol=None, database=None):
    """
    Function that gets a gene id and a database and returns the HTML of the card.
    """
    if request.method == 'GET' and request.is_ajax():
        symbol    = request.GET['target']
        database  = request.GET['targetDB']
    try:
        #card_node = query_node(symbol, database)
        card_node = GeneSearch(symbol, database)
        if database != "Human":
            card_node = card_node.get_planarian_nodes()[0]
            card_node.get_summary()
            card_node.get_neighbours()
            card_node.get_domains()
            card_node.get_geneontology()
            nodes, edges = card_node.get_graphelements()
            graph = GraphCytoscape()
            graph.add_elements(nodes)
            graph.add_elements(edges)
        else:
            card_node = card_node.get_human_nodes()[0]
            homologs = card_node.get_homologs()
            card_node.get_summary()
    except Exception:
        return render_to_response('NetExplorer/not_interactome.html')
    if database != "Human":
        response = {
            'node'      : card_node,
            'json_graph': graph.to_json(),
            'domains'   : card_node.domains_to_json()
        }
    else:
        response = {
            'node' : card_node,
            'homologs': homologs
        }
    if request.is_ajax():
        return render(request, 'NetExplorer/gene_card.html', response)
    else:
        return render(request, 'NetExplorer/gene_card_fullscreen.html', response)