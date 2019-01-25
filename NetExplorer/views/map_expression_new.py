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

        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        condition = Condition.objects.get(name=condition, experiment=experiment)
        samples = SampleCondition.objects.filter(condition=condition).values('sample')

        colormap = dict()
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
                    expression = expressions.expression_value
            else:
                expression = "NA"
            colormap[symbol] = condition.get_color(dataset, expression, profile)
        response = json.dumps(colormap)
        return HttpResponse(response, content_type="application/json")
    else:
        print("HA")
        return render(request, 'NetExplorer/404.html')