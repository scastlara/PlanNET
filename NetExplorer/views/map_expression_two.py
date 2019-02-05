from .common import *

def map_expression_two(request):
    '''
    Gets a list of gene symbols, an experiment, two conditions, and a color palette,
    returning the colors for each gene according to the fold change.
    '''
    exp_name = request.POST['experiment']
    dataset = request.POST['dataset']
    condition1 = request.POST['condition1']
    condition2 = request.POST['condition2']
    symbols = request.POST['symbols']
    symbols = symbols.split(",")
    profile = request.POST['profile']
    
    experiment = Experiment.objects.get(name=exp_name)
    dataset = Dataset.objects.get(name=dataset)
    condition1 = Condition.objects.get(name=condition1, experiment=experiment)
    condition2 = Condition.objects.get(name=condition2, experiment=experiment)

    colormap = dict()
    color_gradient = colors.ColorGenerator(10, -10, profile)
    for symbol in symbols:
        try:
            expression = ExpressionRelative.objects.get(
                experiment=experiment,
                dataset=dataset,
                condition1=condition1,
                condition2=condition2,
                gene_symbol=symbol)
            expression = expression.fold_change
        except ExpressionRelative.DoesNotExist:
            # In case condition1 and condition2 are reversed in Database
            try:
                expression = ExpressionRelative.objects.get(
                    experiment=experiment,
                    dataset=dataset,
                    condition1=condition2,
                    condition2=condition1,
                    gene_symbol=symbol)
                # We take the negative value of logFC because
                # we are comparing c2 vs c1 in this case.
                expression = -expression.fold_change
            except ExpressionRelative.DoesNotExist:
                # If there is no expression fold change for a particular
                # gene, that could mean its p-value is too big to be 
                # stored on the database (there is no significant fold change)
                # between condition 1 and condition 2 for that gene.
                expression = "NA"
        
        colormap[symbol] = color_gradient.map_color(expression)

    response = json.dumps(colormap)
    return HttpResponse(response, content_type="application/json")