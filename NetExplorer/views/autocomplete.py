from .common import *


def autocomplete(request):
    '''
    Tries to autocomplete contig names
    '''
    s_string = request.GET['s_string']
    if not s_string:
        return None
    if s_string.startswith("_"):
        s_string = "dd_Smed_v6" + s_string
 
    s_string = re.sub("[\'\"]", "", s_string)
    if 'database' in request.GET:
        # Querying NEO4j
        database = request.GET['database']
        if database == "Pfam" or database == "Go":
            query = neoquery.AUTOCOMPLETE_ACCESSION % (database, s_string)
        else:
            query = neoquery.AUTOCOMPLETE_CONTIG % (database, s_string)
        
        results = GRAPH.run(query)
        results = results.data()
        results = [ val['symbol'] for val in results ]
        results = sorted(results, key=lambda x: (len(x),x))
    return HttpResponse(json.dumps(results), content_type="application/json")