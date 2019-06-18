from ....helpers.common import *

def map_expression_two(request):
    """
    Maps expression of genes ina two-conditions comparison for coloring the nodes in PlanExp graph.
    
    Accepts:
        * **GET + AJAX**
    
    Args:
        experiment (`str`): Experiment name.
        dataset (`str`): Dataset name.
        condition1 (`str`): Condition 1 name.
        condition2 (`str`): Condition 2 name.
        symbols (`str`): Node symbols separated by commas.
        profile (`str`): Color profile name.

    Response:
        * **GET**:
           * **str**: JSON with color mappings.

           .. code-block:: javascript

                {
                    'colormap': 
                        {
                            'gene1': '#fff',
                            ...
                        },
                    'legend' : str
                }

    """
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

    colormap = {}
    color_gradient = colors.ColorGenerator(10, -10, profile)
    units = "Log Fold Change"
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

    response = {}
    response['colormap'] = colormap
    response['legend'] =  color_gradient.get_color_legend(units=units)
    response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")