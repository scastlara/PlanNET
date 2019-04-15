from .common import *

def sort_results(datasets, results):
    '''
    Sorts gene/node results by:
        1- Dataset (Smesgene - Human - AllContigs by year)
        2- Gene Name.
        3- Contig/Gene symbol.
    Also removes results from not allowed datasets
    '''
    dataset_names = set([ dat.name for dat in datasets ])
    dataset_names.add("Smesgene")
    dataset_names.add("Human")

    dataset_order = [ dat.name for dat in datasets ]
    dataset_order.insert(0, 'Smesgene')
    dataset_order.insert(1, 'Human')
    # Remove results from not allowed datasets
    results = [ res for res in list(results.nodes) if res.database in dataset_names ]
    # Sort the thing
    sorted_results = sorted(
        results, 
        key= lambda a: (dataset_order.index(a.database), a.name, a.symbol) if hasattr(a, 'name') and a.name else (dataset_order.index(a.database), "a", a.symbol)
    )
    return sorted_results

def get_search_summary(datasets, results):
    dataset_order = [ dat.name for dat in datasets ]
    dataset_order.insert(0, 'Smesgene')
    dataset_order.insert(1, 'Human')

    summary = dict()
    for node in results:
        if node.database not in summary:
            summary[node.database] = 1
        else:
            summary[node.database] += 1
    sorted_summary = list()
    all_results = 0
    for dataset in dataset_order:
        if dataset in summary:
            sorted_summary.append((dataset, summary[dataset]))
            all_results += summary[dataset]
    sorted_summary.insert(0, ("All results", all_results))
    return sorted_summary


def gene_search(request):
    '''
    This is the text-based database search function.
    response:
        - symbols
        - database
        - databases
        - search_error
        - res
        - valid_query
    '''
    response = dict()
    response['databases'] = Dataset.get_allowed_datasets(request.user)
    response['valid_query'] = False
    if request.method == "GET" and "genesymbol" in request.GET:
        # Get Form input
        symbols = request.GET['genesymbol']
        database = None
        if "database" in request.GET and request.GET['database']:
            database = request.GET['database']
        nodes = list()
        response['search_error'] = 0
        response['symbols'] = symbols
        response['database'] = database
        if symbol_is_empty(symbols) is False:
            # If there is a search term
            
            symbols = symbols.split(",")
            if not database:
                database = "ALL"
                response['database'] = database

            # Valid search (symbols + database)
            response['valid_query'] = True
            nodes_graph = GraphCytoscape()
            try:
                nodes_graph.new_nodes(symbols, database)
            except Exception as err:
                print(err)
                logging.info("Node not found.")
            if not nodes_graph:
                response['search_error'] = 1
            else:
                response['res'] = sort_results(response['databases'], nodes_graph)
                response['summary'] = get_search_summary(response['databases'], response['res'])
    return render(request, 'NetExplorer/gene_search.html', response)