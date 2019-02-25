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
        samples = SampleCondition.objects.filter(condition=condition).values('sample')

        colormap = dict()
        max_expression = 0
        units = None

        genes_in_experiment = set(ExperimentGene.objects.filter(
            experiment=experiment,
            gene_symbol__in=symbols
        ).values_list("gene_symbol", flat=True))
        
        for symbol in symbols:
            if symbol not in genes_in_experiment:
                # Gene symbol does not belong to the experiment
                continue
            expressions = ExpressionAbsolute.objects.filter(
                experiment=experiment,
                dataset=dataset,
                sample__in=samples,
                gene_symbol=symbol)
            if expressions.exists():
                # Check if expression is a single value for each gene in the network
                # or if there are replicates (multiple samples per condition -> multiple expression values)
                if units is None:
                    units = expressions[0].units
                if len(expressions) > 1:
                    mean_exp = 0
                    for exp in expressions:
                        mean_exp += exp.expression_value
                    # Add missing zeroes, because zeroes are not stored in DB
                    for i in range(1, len(samples) - len(expressions)):
                        mean_exp += 0
                    mean_exp = mean_exp / len(samples)
                    expression = mean_exp
                else:
                    expression = expressions[0].expression_value
            else:
                # Gene symbol belongs to the experiment, but does not have expression
                # in any sample (all of them == 0)
                expression = 0
            if reference == "Experiment":
                colormap[symbol] = condition.get_color(dataset, expression, profile)
            else:
                # We only save the expression value and after we have all of them,
                # we compute the colors in reference to the max expression
                colormap[symbol] = expression
                if expression != "NA" and expression > max_expression:
                    max_expression = expression
                    
        
        if reference == "Network":
            # If colors are to be computed according to the max expression in the network,
            # we need to change the expression values to colors now.
            for symbol, exp in colormap.items():
                colormap[symbol] = condition.get_color(dataset, exp, profile, max_expression)

        response = dict()
        response['colormap'] = colormap
        response['legend'] = condition.get_color_legend(profile=profile, units=units)
        response = json.dumps(response)
        return HttpResponse(response, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')