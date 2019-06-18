from ..helpers.common import *

def sort_results(datasets, results):
    """
    Sorts gene/node results by:
        1- Dataset (Smesgene - Human - AllContigs by year)
        2- Gene Name.
        3- Contig/Gene symbol.
    Also removes results from not allowed datasets.

    Args:
        datasets (`list` of :obj:`Dataset`): list of allowed Datasets.
        results (:obj:`GraphCytoscape`): GraphCytoscape of search results to sort.
    
    Returns:
        `list` of `tuple`: Lists of tuples. Each tuple has (`dataset`, `node name`, `node symbol`).
    """
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
    """
    Cretes a summary of the searched performed in gene_search.

    Args:
        datasets (`list` of `str`): List of all datasets to which User 
            has permissions to.
        results (`list` of `Node`): List of Node objects that match the serach.

    Returns:
        `list` of `tuple`: List of tuples with each one of them having the name 
        of the Dataset and the second having the number of hits for that 
        dataset. 
    """
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
    """
    Search for planarian genes and transcripts using their identifiers or any 
    of their annotations (PFAM, GO, homologs).

    Accepts:
        * **GET**

    Args:
        genesymbol (str): Search term with gene symbol(s).
        database (str): Database in which to search for gene symbol(s).

    Response:
        * **res** (`list` of `Nodes`): Results to be displayed.
        * **summary** (str): Summary of the search.
        * **search_error** (int): Indicates if there was an error in the search.
        * **valid_query** (bool): Indicates if query is valid.

    Template:
        * **NetExplorer/gene_search.html**
    """
    response = {}
    response['databases'] = Dataset.get_allowed_datasets(request.user)
    response['valid_query'] = False
    if request.method == "GET" and "genesymbol" in request.GET:
        # Get Form input
        symbols = request.GET['genesymbol']
        database = None
        if "database" in request.GET and request.GET['database']:
            database = request.GET['database']
        nodes = []
        response['search_error'] = 0
        response['symbols'] = symbols
        response['database'] = database
        if symbol_is_empty(symbols) is False:
            # If there is a search term
            
            symbols = symbols.split(",")
            symbols = [ re.sub("[\'\"]", "", symbol) for symbol in symbols ]
            if not database:
                database = "ALL"
                response['database'] = database

            # Valid search (symbols + database)
            response['valid_query'] = True
            nodes_graph = GraphCytoscape()
            nodes_graph.new_nodes(symbols, database)

            if not nodes_graph:
                response['search_error'] = 1
            else:
                response['res'] = sort_results(response['databases'], nodes_graph)
                response['summary'] = get_search_summary(response['databases'], response['res'])
    return render(request, 'NetExplorer/gene_search.html', response)