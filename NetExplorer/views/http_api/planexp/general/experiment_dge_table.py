from ....helpers.common import *

#@register.filter
#def get_item(dictionary, key):
#    return dictionary.get(key)


def do_volcano_plot(expression):
    '''
    Creates a Volcano plot with a given comparison of conditions.

    Args:
        expression (:obj:`QuerySet` of :obj:`ExpressionRelative`): Relative 
            expression between the two conditions, sorted by absolute fold change.
    
    Return:
        :obj:`VolcanoPlot`: Plot with -log(p-value) as y-axis and log fold change as x-axis.
    '''
    theplot = VolcanoPlot()
    trace_name = "Volcano Plot"
    theplot.add_trace(trace_name)
    max_x = 0
    min_x = 0
    max_y = 0
    for gexp in expression:
        x = gexp.fold_change
        if gexp.pvalue == 0:
            y = -(math.log2(1e-303))
        else:
            y = -(math.log2(gexp.pvalue))
        theplot.add_x(trace_name, x)
        theplot.add_y(trace_name, y)
        theplot.add_name(trace_name, gexp.gene_symbol)

        # Get max and min X
        if min_x == 0:
            min_x = x
        if x > max_x:
            max_x = x
        elif x < min_x:
            min_x = x

        # Get max and min Y
        if y > max_y:
            max_y = y

    bigger_x = max([abs(min_x), abs(max_x)]) + 1
    theplot.set_limits('x', -bigger_x, bigger_x)
    theplot.set_limits('y', 0, max_y + max_y * 0.10) # Add +10% to make plot axis more visible
    theplot.add_units('x', 'log2 ( Fold Change ) ')
    theplot.add_units('y', '-log2 ( pvalue ) ')
    return theplot

def invert_expression_relative(expression):
    expression = list(expression)
    for exp in expression:
        tmp = exp.condition1
        exp.condition1 = exp.condition2
        exp.condition2 = tmp
        exp.fold_change = - exp.fold_change
    return expression



def experiment_dge_table(request):
    """
    Retrieves datasets for which an experiment has data.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        condition1 (`str`): Condition 1 name.
        condition2 (`str`): Condition 2 name.
        dataset (`str`): Dataset name.
        
    Response:
        * **GET + AJAX**:
           * **str**: JSON with DGE table and Volcano Plot.

    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        first_condition_name = request.GET['condition1']
        second_condition_name = request.GET['condition2']
        dataset_name = request.GET['dataset']
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        have_to_invert = False
        condition1 = Condition.objects.get(name=first_condition_name, experiment=experiment)
        condition2 = Condition.objects.get(name=second_condition_name, experiment=experiment)
        expression = ExpressionRelative.objects.filter(
            experiment=experiment, dataset=dataset, 
            condition1=condition1, condition2=condition2)
        if not expression.exists():
            # In case condition1 and condition2 are reversed in Database
            expression = ExpressionRelative.objects.filter(
                experiment=experiment, dataset=dataset, 
                condition1=condition2, condition2=condition1)
            if expression.exists():
                have_to_invert = True

        expression = expression.annotate(abs_fold_change=Func(F('fold_change'), function='ABS')).order_by('-abs_fold_change')

        if have_to_invert:
            expression = invert_expression_relative(expression)

        response = dict()
        if expression:
            contig_list = [ exp.gene_symbol for exp in expression ]
            homologs = GraphCytoscape.get_homologs_bulk(contig_list, dataset_name)
            genes = GraphCytoscape.get_genes_bulk(contig_list, dataset_name)
            for exp in expression:
                if exp.gene_symbol in homologs:
                    exp.homolog = homologs[exp.gene_symbol]
                if exp.gene_symbol in genes:
                    exp.gene = genes[exp.gene_symbol]['gene']
                    exp.name = genes[exp.gene_symbol]['name']
            response_to_render = { 'expressions' : expression, 'database': dataset }
            response['table'] = render_to_string('NetExplorer/experiment_dge_table.html', response_to_render)
            response['volcano'] = do_volcano_plot(expression).plot()
            try:
                json.dumps(response)
            except Exception as err:
                logging.error("PlanExp experiment_dge_table error: {}".format(err))
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')