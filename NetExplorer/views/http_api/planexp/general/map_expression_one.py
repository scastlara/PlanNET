from ....helpers.common import *

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
        num_samples = SampleCondition.objects.filter(condition=condition).count()

        colormap = defaultdict(int)
        max_expression = 0
        units = None

        genes_in_experiment = set(ExperimentGene.objects.filter(
            experiment=experiment,
            gene_symbol__in=symbols
        ).values_list("gene_symbol", flat=True))
        
        expression = ExpressionCondition.objects.filter(
            experiment=experiment,   
            condition=condition, 
            gene_symbol__in=list(genes_in_experiment)
        ).values('gene_symbol', 'sum_expression')

        for exp in expression:
            exp_mean = exp['sum_expression'] / num_samples
            colormap[exp['gene_symbol']] = exp_mean
            
            if exp_mean > max_expression:
                    max_expression = exp_mean

        # Add genes in experiment not found in query (they have expression == 0 for condition)
        genes_missing = set(list(genes_in_experiment)).difference(colormap.keys())
        for missing in genes_missing:
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