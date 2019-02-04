from .common import *

def map_expression_new(request):
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
        for symbol in symbols:
            expressions = ExpressionAbsolute.objects.filter(
                experiment=experiment,
                dataset=dataset,
                sample__in=samples,
                gene_symbol=symbol)
            if expressions:
                if len(expressions) > 1:
                    expression = mean([ exp.expression_value for exp in expressions ])
                else:
                    expression = expressions[0].expression_value
            else:
                expression = "NA"
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

        response = json.dumps(colormap)
        return HttpResponse(response, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')