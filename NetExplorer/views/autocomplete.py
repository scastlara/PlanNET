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

    if 'database' in request.GET:
        # Querying NEO4j
        database = request.GET['database']
        if database == "Pfam" or database == "Go":
            query = neoquery.AUTOCOMPLETE_ACCESSION % (database, s_string)
        else:
            query = neoquery.AUTOCOMPLETE_CONTIG % (database, s_string)
        
        print(query)
        results = GRAPH.run(query)
        results = results.data()
        results = [ val['symbol'] for val in results ]
    elif 'experiment' in request.GET:
        experiment = request.GET['experiment']
        experiment = Experiment.objects.get(name=experiment)
        # Querying PlanExp mysql
        results = list(ExperimentGene.objects.filter(
            experiment=experiment, gene_symbol__startswith=s_string
        ).values_list('gene_symbol', flat=True).distinct())
    return HttpResponse(json.dumps(results), content_type="application/json")