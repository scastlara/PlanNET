from common import *

def do_barplot(experiment, dataset, conditions, gene_symbols):
    """
    Creates a Barplot out of one or multiple genes.
    Useful when we have One Sample per Condition per Gene (one value to plot).
    """
    theplot = None
    for g_idx, gene_symbol in enumerate(gene_symbols):
        if theplot is None:
            theplot = BarPlot()
            theplot.add_trace_name(g_idx, gene_symbol)
        else:
            theplot.add_trace(g_idx)
            theplot.add_trace_name(g_idx, gene_symbol)
        
        for condition in conditions:
            samples = SampleCondition.objects.filter(condition=condition).values('sample')
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment, dataset=dataset, 
                sample__in=samples,    gene_symbol=gene_symbol)
            if expression:
                expression = expression[0].expression_value
            else:
                expression = 0
            theplot.add_group(condition.name)
            theplot.add_value(expression, condition.name, g_idx)
    return theplot


def do_violin(experiment, dataset, conditions, gene_symbols):
    '''
    THE CHECK
    dd_Smed_v6_7_0_1,dd_Smed_v6_702_0_1,dd_Smed_v6_659_0_1,dd_Smed_v6_920_0_1
    '''
    theplot = None
    for g_idx, gene_symbol in enumerate(gene_symbols):
        if theplot is None:
            theplot = ViolinPlot()
            theplot.add_trace_name(g_idx, gene_symbol)
        else:
            theplot.add_trace(g_idx)
            theplot.add_trace_name(g_idx, gene_symbol)
        
        for condition in conditions:
            samples = SampleCondition.objects.filter(condition=condition).values('sample')
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment, dataset=dataset, 
                sample__in=samples,    gene_symbol=gene_symbol)
            theplot.add_group(condition.name)
            if expression:
                for exp in expression:
                    if exp.expression_value:
                        theplot.add_value(exp.expression_value, condition.name, g_idx)
                    else:
                        theplot.add_value(0, condition.name, g_idx)
            else:
                expression = 0
    return theplot


def is_one_sample(experiment, conditions):
    '''
    Checks if there is only one sample per condition in experiment.
    '''
    samples_in_condition = SampleCondition.objects.filter(experiment=experiment, condition=conditions[0])
    if len(samples_in_condition) == 1:
        return True
    else:
        return False

def plot_gene_expression(request):
    """
    View from PlanExp that returns data to plot gene expression
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset = request.GET['dataset']
        gene_names = request.GET['gene_name']
        gene_names = gene_names.split(",")

        # First disambiguate gene names
        gene_symbols = list()
        for gene_name in gene_names:
            gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        conditions = Condition.objects.filter(experiment__name=exp_name)

        if is_one_sample(experiment, conditions):
            theplot = do_barplot(experiment, dataset, conditions, gene_symbols)
        else:
            # Do Violin plot
            try:
                conditions = Condition.objects.filter(experiment__name=exp_name, name__in= [ "1", "2", "3","4", "5", "6", "7"],cond_type=ConditionType.objects.get(name="Cluster",))
                theplot = do_violin(experiment, dataset, conditions, gene_symbols)
            except Exception as err:
                print(err)
        if theplot is not None:
            response = theplot.plot()
        else:
            response = None

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')