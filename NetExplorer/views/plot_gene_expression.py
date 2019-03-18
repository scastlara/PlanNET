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


def do_violin(experiment, dataset, conditions, gene_symbols, ctype, only_toggle):
    '''
    THE CHECK
    dd_Smed_v6_7_0_1,dd_Smed_v6_702_0_1,dd_Smed_v6_659_0_1,dd_Smed_v6_920_0_1
    '''
    theplot = None
    units = None
    theplot = ViolinPlot()
    condition_expression = dict()
    condition_list = list()
    gene_conditions = dict()

    for condition in conditions:
        samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)

        expression = ExpressionAbsolute.objects.filter(
            experiment=experiment,   dataset=dataset, 
            sample__in=list(samples), gene_symbol__in=gene_symbols
        ).values('gene_symbol', 'sample', 'expression_value')
        genes_found = set()

        gene_expression_dict = dict()
        for exp in expression:
            genes_found.add(exp['gene_symbol'])
            if exp['gene_symbol'] not in gene_expression_dict:
                gene_expression_dict[exp['gene_symbol']] = dict()
            gene_expression_dict[exp['gene_symbol']][exp['sample']] = exp['expression_value']

        # Add missing genes
        genes_missing = set(gene_symbols).difference(genes_found)
        for missing in genes_missing:
            if missing not in gene_expression_dict:
                gene_expression_dict[missing] = dict()

        for gene, sample_exp in gene_expression_dict.items():
            if gene not in condition_expression:
                condition_expression[gene] = list()

            gcounter = 0 # Counts number of samples per gene
                         # for only_toggle because plotly 
                         # needs at least two samples!

            for sample in samples:
                if not only_toggle:
                    # We need an expression value for each sample/cell,
                    # even if not in database / gene_expression_dict
                    if sample not in sample_exp:
                        condition_expression[gene].extend([0])
                    else:
                        condition_expression[gene].extend([ sample_exp[sample] ])
                if only_toggle:
                    # Only add expressions in database
                    if sample in sample_exp:
                        condition_expression[gene].extend([ sample_exp[sample] ])
                        if gene not in gene_conditions:
                            gene_conditions[gene] = list()
                        gene_conditions[gene].append(condition.name)
                        gcounter += 1
            if only_toggle:
                if gcounter < 2:
                    missing = 2 - gcounter 
                    for i in range(0, missing):
                        condition_expression[gene].extend([ 0 ])
                        if gene not in gene_conditions:
                            gene_conditions[gene] = list()
                        gene_conditions[gene].append(condition.name)


        if not only_toggle: 
            # We need a list of conditions of the same length as
            # samples, because ALL are included, even if no expression
            for sample in samples:
                condition_list.append(condition.name)

    for gene in gene_symbols:
        # Single Factor. Simple Line Chart.
        theplot.traces.append(PlotlyTrace(name=gene))
        if not only_toggle :
            theplot.traces[-1].x = condition_list
        else:
            theplot.traces[-1].x = gene_conditions[gene]
        theplot.traces[-1].y = condition_expression[gene]
        theplot.traces[-1].type = "violin"
    theplot.add_units('y', units)
    return theplot


def do_heatmap(experiment, dataset, conditions, gene_symbols, ctype):
    '''
    Creates a heatmap comparing multiple genes in multiple conditions
    '''
    theplot = None
    condition_expression = dict()
    theplot = HeatmapPlot()
    all_samples = list()
    if ctype != "Samples":
        # Each column will be a condition
        theplot.add_conditions(conditions)
    for condition in conditions:
        samples = SampleCondition.objects.filter(experiment=experiment, condition=condition).values_list('sample', flat=True)
        if ctype != "Samples":
            # Plot mean expression per Condition
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment,   dataset=dataset, 
                sample__in=list(samples), gene_symbol__in=gene_symbols
            ).values('gene_symbol').annotate(cond_sum = Sum('expression_value'))
        else:
            # Plot expression per cell
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment,   dataset=dataset, 
                sample__in=list(samples), gene_symbol__in=gene_symbols
            ).values('gene_symbol', 'sample', 'expression_value')
            all_samples.extend([ condition.name + " - " + str(i) for i in range(len(list(samples))) ])
        genes_found = set()

        if ctype != "Samples":
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
        else:
            gene_expression_dict = dict()
            for exp in expression:
                genes_found.add(exp['gene_symbol'])
                if exp['gene_symbol'] not in gene_expression_dict:
                    gene_expression_dict[exp['gene_symbol']] = dict()
                gene_expression_dict[exp['gene_symbol']][exp['sample']] = exp['expression_value']

            # Add missing genes
            genes_missing = set(gene_symbols).difference(genes_found)
            for missing in genes_missing:
                if missing not in gene_expression_dict:
                    gene_expression_dict[missing] = dict()

            # Add missing cells
            for gene, sample_exp in gene_expression_dict.items():
                if gene not in condition_expression:
                    condition_expression[gene] = list()
                for sample in samples:
                    if sample not in sample_exp:
                        condition_expression[gene].extend([0])
                    else:
                        condition_expression[gene].extend([ sample_exp[sample] ])
    
    if ctype == "Samples":
        #print(all_samples)
        theplot.add_conditions(all_samples)
    for gene in gene_symbols:
        theplot.add_gene(gene)
        theplot.add_gene_expression(condition_expression[gene]) 
    return theplot


def do_linechart(experiment, dataset, conditions, gene_symbols, ctype):
    '''
    Creates a linechart with mean expression for each point. 
    It tries to put any Day/Time factor on the X, and then divide
    the other factor (if it is an interaction, e.g.: "Time - Cluster" or "Time - RNAi")
    as subplots.
    '''
    theplot = None
    condition_expression = dict()

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

    conditions = [ condition.name for condition in conditions ]
    theplot = LinePlot()
    group_idxs = dict()
    time_idxs = list()
    if " - " in conditions[0]:
        # Interaction Factor. Multiple Subplots.
        for c_idx, condition in enumerate(conditions):
            c1, c2 = condition.split(" - ")
            if c1 not in set(time_idxs):
                time_idxs.append(c1)
            if c2 not in group_idxs:
                group_idxs[c2] = list()
            group_idxs[c2].append(c_idx)
    
    if not group_idxs:
        for gene in gene_symbols:
            # Single Factor. Simple Line Chart.
            theplot.traces.append(PlotlyTrace(name=gene))
            theplot.traces[-1].x = conditions
            theplot.traces[-1].y = condition_expression[gene]
            theplot.traces[-1].type = "scatter"
    else:
        # Interaction Factor. Multiple Subplots.
        subplot_i = 1
        for group_name, group_i in group_idxs.items():
            for gene in gene_symbols:
                theplot.traces.append(PlotlyTrace(name=gene))
                theplot.traces[-1].x = time_idxs
                theplot.traces[-1].y = [ condition_expression[gene][i] for i in group_i ]
                theplot.traces[-1].xaxis = "x" + str(subplot_i)
                theplot.traces[-1].yaxis = "y" + str(subplot_i)
                theplot.traces[-1].type = "scatter"
                theplot.traces[-1].subplot_title = group_name
                theplot.traces[-1].legend_group = gene
            subplot_i += 1
    
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
        only_toggle = json.loads(request.GET['only']) # If active, will only show expressed cells in violin plot
        gene_names = gene_names.split(",")


        # First disambiguate gene names
        gene_symbols = list()
        for gene_name in gene_names:
            gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)

        # WILL NEED TO CHANGE THE ORDER BY TO SORT
        # USING MIXED SORT
        ctype_tosearch = ctype
        if ctype == "Samples":
            ctype_tosearch = "Cluster"
        conditions = Condition.objects.filter(
                        experiment__name=exp_name, 
                        cond_type=ConditionType.objects.get(name=ctype_tosearch))
        conditions = sorted(conditions, key= lambda x: condition_sort(x))

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
                    
                    theplot = do_violin(experiment, dataset, conditions, list(genes_in_experiment), ctype, only_toggle)
            elif plot_type == "heatmap":
                # PLOT HEATMAP
                theplot = do_heatmap(experiment, dataset, conditions, list(genes_in_experiment), ctype)
            else:
                # LINE PLOT
                theplot = do_linechart(experiment, dataset, conditions, list(genes_in_experiment), ctype)
            if theplot is not None and not theplot.is_empty():
                response = theplot.plot()
            else:
                response = None

        else:
            response = None

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')