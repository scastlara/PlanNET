from .common import *

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
        response = None


        # First disambiguate gene names
        gene_symbols = list()
        for gene_name in gene_names:
            gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
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

        if plot_type == "violin" and is_one_sample(experiment, conditions):
            plot_type = "bar"

        if len(genes_in_experiment) > 0:
            creator = PlotCreator()
            theplot = creator.create_plot(
                plot_type, 
                experiment=experiment,
                dataset=dataset,
                conditions=conditions,
                genes=list(genes_in_experiment),
                ctype=ctype,
                only_toggle=only_toggle
            )
        
        try:
            if theplot is not None and not theplot.is_empty():
                response = theplot.plot()
            else:
                response = None
        except Exception as err:
            print(err)

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')