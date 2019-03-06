from .common import *

def do_barplot(experiment, dataset, conditions, gene_symbols):
    """
    Creates a Barplot out of one or multiple genes.
    Useful when we have One Sample per Condition per Gene (one value to plot).
    """
    theplot = None
    units = None
    for g_idx, gene_symbol in enumerate(gene_symbols):
        if theplot is None:
            theplot = BarPlot()
            theplot.add_trace_name(g_idx, gene_symbol)
        else:
            theplot.add_trace(g_idx)
            theplot.add_trace_name(g_idx, gene_symbol)
        
        for condition in conditions:
            samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment, dataset=dataset, 
                sample__in=list(samples),    gene_symbol=gene_symbol).values_list("expression_value", flat=True)
            if expression:
                expression = expression[0]
            else:
                expression = 0

            theplot.add_group(condition.name)
            theplot.add_value(expression, condition.name, g_idx)
            
    theplot.add_units("y", units)
    return theplot


def do_violin(experiment, dataset, conditions, gene_symbols, ctype):
    '''
    THE CHECK
    dd_Smed_v6_7_0_1,dd_Smed_v6_702_0_1,dd_Smed_v6_659_0_1,dd_Smed_v6_920_0_1
    '''
    theplot = None
    units = None
    condition_samples = dict()
    for condition in conditions:
        samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)
        condition_samples[condition] = list(samples)
        
    for g_idx, gene_symbol in enumerate(gene_symbols):
        if theplot is None:
            theplot = ViolinPlot()
            theplot.add_trace_name(g_idx, gene_symbol)
        else:
            theplot.add_trace(g_idx)
            theplot.add_trace_name(g_idx, gene_symbol)
        
        for condition in conditions:
            if ctype == "Cluster" and str(condition.name).isdigit():
                condname = "c" + str(condition.name)
            else:
                condname = str(condition.name)

            samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment, dataset=dataset, 
                sample__in=list(samples),    gene_symbol=gene_symbol).values_list("expression_value", flat=True)
            theplot.add_group(condname)
            added_values = int()
            if expression:
                for exp in expression:
                    if exp:
                        theplot.add_value(exp, condname, g_idx)
                    else:
                        theplot.add_value(0, condname, g_idx)
                    added_values += 1
            else:
                # No expression in any cell/sample for this condition
                theplot.add_value(0, condname, g_idx)
                added_values += 1
            
            # Add missing values in database: genes don't have expression in some
            # samples because we don't store zeroes, thus, we have to add the zeroes manually.
            missing = len(samples) - added_values
            for i in range(1, missing):
                theplot.add_value(0, condname, g_idx)
    theplot.add_units('y', units)
    return theplot


def do_heatmap(experiment, dataset, conditions, gene_symbols, ctype):
    '''
    Creates a heatmap comparing multiple genes in multiple conditions
    '''
    theplot = None
    condition_expression = dict()
    theplot = HeatmapPlot()
    theplot.add_conditions(conditions)
    for condition in conditions:
        samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)
        expression = ExpressionAbsolute.objects.filter(
            experiment=experiment,   dataset=dataset, 
            sample__in=list(samples), gene_symbol__in=gene_symbols
        ).values('gene_symbol').annotate(cond_sum = Sum('expression_value'))
        genes_found = set()
        for exp in expression:
            genes_found.add(exp['gene_symbol'])
            if exp['gene_symbol'] not in condition_expression:
                condition_expression[exp['gene_symbol']] = list()
            condition_expression[exp['gene_symbol']].append(exp['cond_sum'] / len(samples))
        genes_missing = set(gene_symbols).difference(genes_found)
        for missing in genes_missing:
            if missing not in condition_expression:
                condition_expression[missing] = list()
            condition_expression[missing].append(0)
    for gene in gene_symbols:
        theplot.add_gene(gene)
        theplot.add_gene_expression(condition_expression[gene]) 
    return theplot



def is_one_sample(experiment, conditions):
    '''
    Checks if there is only one sample per condition in experiment.
    '''
    samples_in_condition = SampleCondition.objects.filter(experiment=experiment, condition=conditions[0]).count()
    if samples_in_condition == 1:
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
        ctype = request.GET['ctype']
        plot_type = request.GET['plot_type']
        gene_names = gene_names.split(",")

        # First disambiguate gene names
        gene_symbols = list()
        for gene_name in gene_names:
            gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        conditions = Condition.objects.filter(
                        experiment__name=exp_name, 
                        cond_type=ConditionType.objects.get(name=ctype)).order_by("name")
        conditions = list(conditions)

        # Filter genes to only those in experiment
        genes_in_experiment = ExperimentGene.objects.filter(
            experiment=experiment,
            gene_symbol__in=gene_symbols
        ).values_list("gene_symbol", flat=True)
        
        if len(genes_in_experiment) > 0:
            if plot_type == "violin":
                if is_one_sample(experiment, conditions):
                    theplot = do_barplot(experiment, dataset, conditions, list(genes_in_experiment))
                else:
                    
                    theplot = do_violin(experiment, dataset, conditions, list(genes_in_experiment), ctype)
            else:
                # PLOT HEATMAP
                theplot = do_heatmap(experiment, dataset, conditions, list(genes_in_experiment), ctype)

            if theplot is not None and not theplot.is_empty():
                response = theplot.plot()
            else:
                response = None

        else:
            response = None

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')