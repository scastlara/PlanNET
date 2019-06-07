from ....helpers.common import *


def plot_sample_count(request):
    """
    Plots UpSet with sample counts expressing one or more genes.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        dataset (`str`): Dataset name.
        gene_name (`str`): Gene symbol(s).
        ctype (`str`): Condition type.
        conditions (`str`): List of conditions to restrict the search of samples.

    Response:
        * **GET + AJAX**:
           * **str**: Binary blob with plot.
   
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset = request.GET['dataset']
        gene_names = request.GET['gene_name']
        ctype = request.GET['ctype']
        conditions = json.loads(request.GET.get('conditions'))
        
        # First disambiguate gene names
        gene_names = gene_names.split(",")
        gene_symbols = list()
        for gene_name in gene_names:
            if gene_name.strip():
                gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        if len(gene_symbols) < 2:
            response = None
        else:
            # Get Experiment and dataset
            experiment = Experiment.objects.get(name=exp_name)
            dataset = Dataset.objects.get(name=dataset)
            ctype = ConditionType.objects.get(name=ctype)
            
            # Do the plot
            creator = PlotCreator()
            theplot = creator.create_plot(
                "upset",
                experiment=experiment,
                dataset=dataset,
                conditions=conditions,
                genes=list(gene_symbols),
                ctype=ctype
            )

            response = {}
            if theplot is not None:
                response['plot'] = theplot.plot()
                response['csv']  = theplot.csv()
            else:
                response = None

        return HttpResponse(json.dumps(response), content_type="application/json")
