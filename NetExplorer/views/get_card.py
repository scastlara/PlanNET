from .common import *

def get_card(request, symbol=None, database=None):
    """
    Function that gets a gene id and a database and returns the HTML of the card.
    """
    if request.method == 'GET' and request.is_ajax():
        symbol    = request.GET['target']
        database  = request.GET['targetDB']
        template  = ""
    try:
        gsearch = GeneSearch(symbol, database)
        if database == "Human":
            template = "NetExplorer/human_card.html"
            card_node = gsearch.get_human_nodes()[0]
            homologs = card_node.get_homologs()
            card_node.get_summary()
        elif database == "Smesgene":
            template = "NetExplorer/smesgene_card.html"
            card_node = gsearch.get_planarian_genes()[0]
            contigs = card_node.get_predictednodes()
            best_contig = card_node.get_best_transcript()
            nodes, edges = best_contig.get_graphelements()
            graph = GraphCytoscape()
            graph.add_elements(nodes)
            graph.add_elements(edges)
        else:
            template = "NetExplorer/contig_card.html"
            card_node = gsearch.get_planarian_contigs()[0]
            card_node.get_summary()
            card_node.get_neighbours()
            card_node.get_domains()
            card_node.get_geneontology()
            nodes, edges = card_node.get_graphelements()
            graph = GraphCytoscape()
            graph.add_elements(nodes)
            graph.add_elements(edges)
    except Exception as err:
        print(err)
        return render_to_response('NetExplorer/not_interactome.html')
    if database == "Human":
       response = {
            'node' : card_node,
            'homologs': homologs
        }
    elif database == "Smesgene":
        response = {
            'node': card_node,
            'transcripts': contigs,
            'json_graph': graph.to_json()
        }
    else:
        response = {
            'node'      : card_node,
            'json_graph': graph.to_json(),
            'domains'   : card_node.domains_to_json()
        }
        
    if request.is_ajax():
        return render(request, template, response)
    else:
        return render(request, 'NetExplorer/gene_card_fullscreen.html', response)