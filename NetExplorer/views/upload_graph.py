from common import *

def upload_graph(request, json_text):
    """
    This function will take the request with a JSON file and it will return
    a template with the graph loaded (it will also handle the errors).
    It will return a render object to be returned by net_explorer view.
    """
    # JSON with graph uploaded
    graph_content = str()
    no_layout     = 0
    if json_text is None:
        graph_content   = request.FILES['myfile'].read()
        graph_content   = graph_content.replace("\xef\xbb\xbf", "") # Remove unicode BOM
        graph_content.replace("'", '"') # Json only allows double quotes
    else:
        graph_content = json_text
        no_layout = 1

    try: # Check if file is a valid JSON
        json_graph = json.loads(graph_content)
        all_experiments = ExperimentList(request.user)
        try: # Check if JSON is a graph declaration
            json_graph[u'nodes']
        except KeyError:
            logging.info("ERROR: Json is not a graph declaration (no nodes) in upload_graph")
            return render(request, 'NetExplorer/netexplorer.html', {'json_err': True,'databases': get_databases(request), 'experiments': all_experiments})
    except ValueError as err:
        logging.info("ERROR: Not a valid Json File %s in upload_graph\n" % (err))
        return render(request, 'NetExplorer/netexplorer.html', {'json_err': True,'databases': get_databases(request)})
    
    # Check if homologs are defined... 
    # They are not if we are coming from Pathway Finder to save time.
    if u'homolog' not in json_graph[u'nodes'][0][u'data']:
        for node in json_graph[u'nodes']:
            qnode = PredictedNode(node[u'data'][u'id'], node[u'data'][u'database'])
            node[u'data'][u'homolog'] = str(qnode.homolog.human.symbol)
        graph_content = json.dumps(json_graph)
    return render(request, 'NetExplorer/netexplorer.html', {'upload_json': graph_content, 'no_layout': no_layout,'databases': get_databases(request), 'experiments': all_experiments})
