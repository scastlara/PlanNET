"""
Views of PlanNet
"""

from django.shortcuts   import render
from django.shortcuts   import render_to_response
from django.http        import HttpResponse
from django.template    import RequestContext
from NetExplorer.models import *
from subprocess import Popen, PIPE, STDOUT
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import tempfile
import textwrap
import json
import re
import logging
import math
import time
import requests
import time
import os


# -----------------------
# CONSTANTS
# -----------------------
BLAST_DB_DIR    = "/home/sergio/code/PlanNET/blast/"
MAX_NUMSEQ      = 50
MAX_CHAR_LENGTH = 25000


# -----------------------
# FUNCTIONS
# -----------------------

def get_databases(request):
    '''
    This function returns the databases allowed for the user to see
    '''
    if not request.user.is_authenticated():
        return sorted(DATABASES)
    else:
        # User is logged in, get the allowed databases for the user
        try:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT auth_user.username, user_db_permissions.database
                FROM auth_user
                INNER JOIN user_db_permissions ON auth_user.id=user_db_permissions.user_id
                WHERE auth_user.username = %s;
            ''', [request.user.username])
            rows = cursor.fetchall()
            user_databases = set(DATABASES)
            user_databases.update([row[1] for row in rows])
            return sorted(user_databases)
        except Exception:
            return sorted(DATABASES)


# ------------------------------------------------------------------------------
def symbol_is_empty(symbol):
    '''
    Checks if the input symbol from the forms is empty or not
    '''
    if re.match(r"[a-zA-Z0-9]", symbol):
        return False
    else:
        return True

# ------------------------------------------------------------------------------
def get_shortest_paths(startnodes, endnodes, plen):
    '''
    This function gets all the possible shortest paths between the specified nodes.
    Returns a json string with all the nodes and edges, the length of the paths and
    the total number of paths
    '''
    graphelements = list()
    numpath = 0
    for snode in startnodes:
        for enode in endnodes:
            paths = snode.path_to_node(enode, plen)
            if paths is None:
                # Return no-path that matches the query_node
                continue
            else:
                for path in paths:
                    graphelements.append( GraphCytoscape() )
                    graphelements[numpath].add_elements(path.graph.nodes)
                    graphelements[numpath].add_elements(path.graph.edges)
                    graphelements[numpath] = (graphelements[numpath].to_json, round(path.score, 2))
                    numpath += 1
    return graphelements, numpath


# -----------------------
# VIEWS
# -----------------------

# ------------------------------------------------------------------------------
def index_view(request):
    '''
    This is the first view the user sees.
    It contains the forms, a mini-tutorial, etc.
    And links to all the functions.
    '''

    return render(request, 'NetExplorer/index.html')

# ------------------------------------------------------------------------------
def get_fasta(request):
    '''
    This function will serve FASTA files
    '''

    genesymbol   = request.GET['genesymbol']
    typeseq      = request.GET['type']
    if "database" in request.GET:
        database = request.GET['database']
    else:
        pass # server error!!

    node = None
    try:
        node = query_node(genesymbol, database)
    except (NodeNotFound, IncorrectDatabase):
        pass # server error!

    sequence = str()
    filename = "%s" % node.symbol
    if typeseq == "sequence":
        sequence = textwrap.fill(node.sequence, 70)
        filename = filename + ".fa"
    elif typeseq == "orf":
        sequence = textwrap.fill(node.orf, 70)
        filename = filename + "-orf.fa"

    sequence = ">%s\n" % node.symbol + sequence
    response = HttpResponse(sequence, content_type='text/plain; charset=utf8')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


# ------------------------------------------------------------------------------
def get_card(request, symbol=None, database=None):
    """
    Function that gets a gene id and a database and returns the HTML of the card.
    """
    if request.method == 'GET' and request.is_ajax():
        symbol    = request.GET['target']
        database  = request.GET['targetDB']

    try:
        card_node = query_node(symbol, database)
        if database != "Human":
            card_node.get_neighbours()
            card_node.get_domains()
            card_node.get_geneontology()
            nodes, edges = card_node.get_graphelements()
            graph = GraphCytoscape()
            graph.add_elements(nodes)
            graph.add_elements(edges)
        else:
            homologs = card_node.get_homologs()
            card_node.get_summary()
    except (NodeNotFound, IncorrectDatabase):
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


# ------------------------------------------------------------------------------
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
            if database is None:
                # No database selected
                response['search_error'] = 2
                response['res'] = nodes
            else:
                # Valid search (symbols + database)
                response['valid_query'] = True
                nodes_graph = GraphCytoscape()
                nodes_graph.new_nodes(symbols, database)
                if not nodes_graph:
                    response['search_error'] = 1
                else:
                    response['res'] = nodes_graph.nodes
    return render(request, 'NetExplorer/gene_search.html', response)


# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
def planexp(request):
    return render(request, 'NetExplorer/planexp.html')

# ------------------------------------------------------------------------------
def show_connections(request):
    """
    View that handles an AJAX request and, given a list of identifiers, returns
    all the interactions between those identifiers/nodes.
    """
    if request.is_ajax():
        nodes_including = request.POST['nodes'].split(",")
        databases       = request.POST['databases'].split(",")
        graphelements   = GraphCytoscape()
        for symbol, database in zip(nodes_including, databases):
            graphelements.add_node( PredictedNode(symbol, database, query=False) )
        graphelements.get_connections()
        return HttpResponse(graphelements, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')

# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
def blast(request):
    """
    View for the BLAST form page
    """
    if request.POST:
        if not request.POST['database']:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No Database selected", 'databases': get_databases(request)})
        if "type" not in  request.POST or not request.POST['type']:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No valid BLAST application selected",'databases': get_databases(request)})

        fasta = str()
        database = request.POST['database'].lower()
        results = list()
        if request.FILES:
            logging.info("There is a file")
            # Must check if FASTA
            fasta = request.FILES['fastafile'].read()
        else:
            logging.info("No-file")
            # Must check if FASTA/plain or otherwise not valid
            fasta = request.POST['fasta_plain']

        if not fasta:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No query", 'databases': get_databases(request)})

        # Check length of sequence/number of sequences
        joined_sequences = list()
        numseq           = 0
        for line in fasta.split("\n"):
            if not line:
                continue
            if line[0] == ">":
                numseq += 1
                continue
            joined_sequences.append(line.strip())
        joined_sequences = "".join(joined_sequences)

        if numseq > MAX_NUMSEQ:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "Too many query sequences (> 50)", 'databases': get_databases(request)})
        elif len(joined_sequences) >  MAX_CHAR_LENGTH:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "Query sequence too long (> 25,000 characters)", 'databases': get_databases(request)})

        # Create temp file with the sequences
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(fasta)
            temp.flush()
            # Run BLAST
            pipe = Popen([request.POST['type'], "-evalue", "1e-10", "-db", BLAST_DB_DIR + database , "-query", temp.name, '-outfmt', '6'], stdout=PIPE, stderr=STDOUT)
            stdout, stderr = pipe.communicate()
            results = [ line.split("\t") for line in stdout.split("\n") if line ]
        if results:
            return render(request, 'NetExplorer/blast.html', {'results': results, 'database': database.title(), 'databases': get_databases(request) })
        else:
            return render(request, 'NetExplorer/blast.html', {'results': results, 'noresults': True, 'database': database.title(), 'databases': get_databases(request) })
    else:
        return render(request, 'NetExplorer/blast.html',{'databases': get_databases(request)})

# ------------------------------------------------------------------------------
def map_expression(request):
    """
    View to handle a possible ajax request to map expression onto graph
    """
    if request.is_ajax():
        nodes      = request.GET['nodes'].split(",")
        databases  = request.GET['databases'].split(",")
        sample     = request.GET['sample']
        to_color   = request.GET['to_color']
        from_color = request.GET['from_color']
        comp_type  = request.GET['type'] # Can be 'one-sample' or 'two-sample'
        # Check if experiment is in DB
        response = dict()
        response['status']     = ""
        response['experiment'] = ""
        response['expression']       = ""
        try:
            experiment = Experiment(request.GET['experiment'])
            experiment.color_gradient(from_color, to_color, comp_type)
            response['experiment'] = experiment.to_json()
        except ExperimentNotFound as err:
            logging.info(err)
            response['status'] = "no-expression"
            response = json.dumps(response)
            return HttpResponse(response, content_type='application/json; charset=utf8')
        if comp_type == "two-sample":
            # We have to samples to compare
            sample = sample.split(":")
            response['sample'] = sample
        else:
            sample = [sample]

        newgraph = GraphCytoscape()
        newgraph.add_elements([ PredictedNode(node, database, query=False) for node, database in zip(nodes, databases) ])
        expression_data = newgraph.get_expression(experiment, sample)
        response['expression'] = dict()
        if comp_type == "two-sample":
            foldchange = dict()
            for node in expression_data:
                exp_sample1 = expression_data[node][sample[0]]
                exp_sample2 = expression_data[node][sample[1]]
                if exp_sample1 == 0 or exp_sample2 == 0:
                    # Don't know how to deal with zeros
                    continue
                foldchange[node] = dict()
                foldchange[node]["foldchange"] = math.log10(exp_sample2 / exp_sample1) / math.log10(2)
            # Now remove samples from list sample and add new key to expression_data dictionary with
            # fold changes.
            sample = list()
            sample.append("foldchange")
            expression_data = foldchange

        for node in expression_data:
            for bin_exp in experiment.gradient:
                if expression_data[node][sample[0]] >= bin_exp[0]:
                    response['expression'][node] = bin_exp[1] # Color
                else:
                    continue
        if not response['expression']:
            response['status'] = "no-expression"
            response = json.dumps(response)
            return HttpResponse(response, content_type='application/json; charset=utf8')
        else:
            response['expression']  = json.dumps(response['expression'])
            response['type']        = comp_type
            response = json.dumps(response)
            return HttpResponse(response, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')

# ------------------------------------------------------------------------------
def path_finder(request):
    """
    View for the Pathway Finder.
    Returns a list called "graphelements". This is a list of tuples, with the first element
    of the tuple being the JSON of the graph to be used by cytoscape.js, and the second element being
    the score assigned to the given pathway.
    """
    if 'start' in request.GET and 'end' in request.GET:
        # We have a search
        if not request.GET['database']:
            return render(request, 'NetExplorer/pathway_finder.html', {"nodb": True, 'databases': get_databases(request)})
        if symbol_is_empty(request.GET['start']) or symbol_is_empty(request.GET['end']):
            return render(request, 'NetExplorer/pathway_finder.html', {"nonodes": True, 'databases': get_databases(request)})
        if not request.GET['plen']:
            return render(request, 'NetExplorer/pathway_finder.html', {"noplen": True, 'databases': get_databases(request)})
        # Search
        # Valid search
        database   = request.GET['database']
        plen       = request.GET['plen']
        start_nodes = GraphCytoscape()
        start_nodes.new_nodes([request.GET['start']], database)
        end_nodes = GraphCytoscape()
        end_nodes.new_nodes([request.GET['end']], database)
        # Get shortest paths
        graphelements, numpath = get_shortest_paths(
            start_nodes.nodes,
            end_nodes.nodes,
            plen
        )
        response = dict()
        response['database']  = database
        response['snode']     = request.GET['start']
        response['enode']     = request.GET['end']
        response["plen"]      = plen
        response["databases"] = Dataset.get_allowed_datasets(request.user)

        if graphelements:
            # We have graphelements to display (there are paths)
            graphelements = sorted(graphelements, key=lambda k: k[1], reverse=True)
            #response["pathways"] = graphelements
            response["numpath"]  = numpath
            paginator = Paginator(graphelements, 10) # Show 25 contacts per page
            page = request.GET.get('page')
            try:
                graphs_for_page = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                graphs_for_page = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                graphs_for_page = paginator.page(paginator.num_pages)
            response['pathways'] = graphs_for_page
            return render(request, 'NetExplorer/pathway_finder.html', response)
        else:
            # No results
            response['noresults'] = True
            return render(request, 'NetExplorer/pathway_finder.html', response)
    else:
        # Not a search
        response = dict()
        response["databases"] = Dataset.get_allowed_datasets(request.user)
        return render(request, 'NetExplorer/pathway_finder.html', response)


# ------------------------------------------------------------------------------
def downloader(request):
    """
    Handles the download of sequence and annotations
    """
    MAX_IDS = 10000
    if 'identifiers' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')
    if 'data' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')
    if 'database' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')

    identifiers = request.POST['identifiers']
    identifiers = re.split(r"[\n\r,;]+", identifiers)
    identifiers = [ symbol.replace(" ", "") for symbol in identifiers ]
    if len(identifiers) > MAX_IDS and not request.user.is_authenticated():
        identifiers = identifiers[0:MAX_IDS]
    database = request.POST['database']
    data = request.POST['data']
    dhandler = DownloadHandler()
    file = dhandler.download_data(identifiers, database, data)
    response = file.to_response()
    return response

# ------------------------------------------------------------------------------
def tutorial(request):
    """
    View for tutorial
    """
    return render(request, 'NetExplorer/tutorial.html')

# ------------------------------------------------------------------------------
def downloads(request):
    """
    View for downloads
    """
    response = dict()
    response['databases'] = get_databases(request)
    return render(request, 'NetExplorer/downloads.html', response)

# ------------------------------------------------------------------------------
def datasets(request):
    """
    View for datasets
    """
    datasets = Dataset.get_allowed_datasets(request.user)
    return render(request, 'NetExplorer/datasets.html', {'databases': datasets})


# ------------------------------------------------------------------------------
def about(request):
    """
    View for about
    """
    return render(request, 'NetExplorer/about.html', {'databases': get_databases(request)})

# ------------------------------------------------------------------------------
def register(request):
    """
    Login view
    """
    if 'usr' in request.POST and 'pwd' in request.POST:
        user = authenticate(username=request.POST['usr'], password=request.POST['pwd'])
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            return render(request, 'NetExplorer/index.html')
        else:
            # No backend authenticated the credentials
            return render(request, 'NetExplorer/login.html', {'error_msg': "Incorrect username or password"})
    return render(request, 'NetExplorer/login.html')

# ------------------------------------------------------------------------------
def logout_view(request):
    """
    Logout view
    """
    logout(request)
    return render(request, 'NetExplorer/index.html')


# ------------------------------------------------------------------------------
def account_view(request):
    """
    View for account options
    """
    if request.user.is_authenticated():
        if request.method == "POST":
            # Check that everything was sent
            if "previous" in request.POST and "pwd1" in request.POST and "pwd2" in request.POST:
                if request.POST['pwd1'] != request.POST['pwd2']:
                    return render(request, 'NetExplorer/account.html', {'error_msg': "New passwords don't match!."})
                if request.POST['pwd1'] == request.POST['previous']:
                    return render(request, 'NetExplorer/account.html', {'error_msg': "New Password must be different to previous password."})
                # Changing a password
                if request.user.check_password(request.POST['previous']):
                    # Everything is correct
                    request.user.set_password(request.POST['pwd1'])
                    request.user.save()
                    return render(request, 'NetExplorer/account.html', {'success_msg': "Password changed successfully."})
                else:
                    return render(request, 'NetExplorer/account.html', {'error_msg': "Incorrect password!."})
            else:
                # Something was not introduced
                return render(request, 'NetExplorer/account.html', {'error_msg': "Please, fill in the camps."})
        return render(request, 'NetExplorer/account.html')
    else:
        return render(request, 'NetExplorer/login.html')

# ------------------------------------------------------------------------------
def handler404(request):
    """
    Handler for error 404, doesn't work.
    """
    response = render_to_response('NetExplorer/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


# ------------------------------------------------------------------------------
def handler500(request):
    """
    Handler for error 500 (internal server error), doesn't work.
    """
    response = render_to_response('NetExplorer/500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
