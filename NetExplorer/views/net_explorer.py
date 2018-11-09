from common import *

def net_explorer(request):
    '''
    This is the cytoscape graph-based search function.
    '''
    if request.method == "GET" and request.is_ajax():
        # CHECK IF FORM IS OK
        if (not "genesymbol" in request.GET or
            not "database" in request.GET or
            symbol_is_empty(request.GET['genesymbol'])):
            return HttpResponse(status=400)
        symbols  = request.GET['genesymbol']
        symbols  = symbols.split(",")
        database = request.GET['database']

        # ADDING NODES USING CONTIG_IDS, PROTEIN SYMBOLS, GO CODES OR PFAM IDENTIFIERS
        if request.GET['type'] == "node":
            graphobject = GraphCytoscape()
            graphobject.new_nodes(symbols, database)
            # Clone the list of nodes to search for interactions
            nodes_to_search = list(graphobject.nodes)
            for node in nodes_to_search:
                try:
                    node.get_neighbours()
                    node.important = True
                    nodes, edges = node.get_graphelements()
                    graphobject.add_elements(nodes)
                    graphobject.add_elements(edges)
                except (NodeNotFound, IncorrectDatabase) as err:
                    continue
            if graphobject.is_empty():
                return HttpResponse(status=404)
            else:
                json_data = graphobject.to_json()
                return HttpResponse(json_data, content_type="application/json")
        # ADDING A PATHWAY USING KEGG CODES
        else:
            kegg = KeggPathway(symbol=symbols[0], database=database)
            if not kegg.is_empty():
                return HttpResponse(kegg.graphelements, content_type="application/json")
            else:
                return HttpResponse(status=404)
    elif request.method == "POST":
        json_text = None
        if 'json_text' in request.POST:
            json_text = request.POST['json_text']
        render_to_return = upload_graph(request, json_text)
        return render_to_return
    else:
        return render(request, 'NetExplorer/netexplorer.html', { 'experiments': ExperimentList(request.user), 'databases': Dataset.get_allowed_datasets(request.user)} )

