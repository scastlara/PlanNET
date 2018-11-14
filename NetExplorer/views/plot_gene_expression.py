from common import *

def plot_gene_expression(request):
    """
    View from PlanExp that returns data to plot gene expression
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset = request.GET['dataset']
        gene_name = request.GET['gene_name']

        # First disambiguate gene name
        gene_symbol = disambiguate_gene(gene_name, dataset)

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        conditions = Condition.objects.filter(experiment__name=exp_name)

        # Prepare plot data
        theplot = None

        # Get expression
        for condition in conditions:
            # Get Samples in Condition (Cluster or Experimental, doesn't matter)
            # Then Get expression for those samples & Experiment & Dataset & GeneSymbol
            samples = SampleCondition.objects.filter(condition=condition).values('sample')
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment, dataset=dataset, 
                sample__in=samples,    gene_symbol=gene_symbol)
            if len(expression) > 1:
                # Multiple samples/values per group -> ViolinPlot
                theplot = ViolinPlot()
            elif len(expression) == 1:
                # Only one sample/value per group -> BarPlot
                if theplot is None:
                    theplot = BarPlot()
                    theplot.add_title(gene_symbol)
                    theplot.add_ylab(expression[0].units)
                expression = expression[0].expression_value
                theplot.add_group(condition.name)
                theplot.add_value(expression, condition.name)
            else:
                expression = 0
        if theplot is not None:
            response = theplot.plot()
        else:
            response = None
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')
