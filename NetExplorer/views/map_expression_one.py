from .common import *

def map_expression_one(request):
    '''
    Gets a list of gene symbols, an experiment, a condition, and a color palette,
    returning the necessary colors for each gene.
    '''
    if request.is_ajax():
        exp_name = request.POST['experiment']
        dataset = request.POST['dataset']
        condition = request.POST['condition']
        symbols = request.POST['symbols']
        symbols = symbols.split(",")
        profile = request.POST['profile']
        reference = request.POST['reference']

        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        condition = Condition.objects.get(name=condition, experiment=experiment)
        samples = SampleCondition.objects.filter(condition=condition).values_list('sample', flat=True)

        colormap = dict()
        max_expression = 0
        units = None

        genes_in_experiment = set(ExperimentGene.objects.filter(
            experiment=experiment,
            gene_symbol__in=symbols
        ).values_list("gene_symbol", flat=True))
        
        expression = ExpressionAbsolute.objects.filter(
            experiment=experiment,   dataset=dataset, 
            sample__in=list(samples), gene_symbol__in=list(genes_in_experiment)
        ).values('gene_symbol').annotate(cond_sum = Sum('expression_value'))

        genes_found = set()
        for exp in expression:
            genes_found.add(exp['gene_symbol'])
            if exp['gene_symbol'] not in colormap:
                exp_mean = exp['cond_sum'] / len(samples)
                colormap[exp['gene_symbol']] = exp_mean
                if exp_mean != "NA" and exp_mean > max_expression:
                    max_expression = exp_mean
        # Add genes in experiment not found in query (they have expression == 0 for condition)
        genes_missing = set(list(genes_in_experiment)).difference(genes_found)
        for missing in genes_missing:
            if missing not in colormap:
                colormap[missing] = 0
        
        for gene, exp in colormap.items():
            if reference == "Experiment":
                colormap[gene] = condition.get_color(dataset, exp, profile)
            else:
                colormap[gene] = condition.get_color(dataset, exp, profile, max_expression)
        response = dict()
        response['colormap'] = colormap
        response['legend'] = condition.get_color_legend(profile=profile, units=units)
        response = json.dumps(response)
        return HttpResponse(response, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')