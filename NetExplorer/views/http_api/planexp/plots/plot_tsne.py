from ....helpers.common import *


def plot_tsne(request):
    """
    Plots t-SNE for single cell experiment.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        dataset (`str`): Dataset name.
        gene_name (`str`): Gene symbol.
        with_color (`bool`): True if gene was provided (and thus cells should be colored
            according to expression). False otherwise.
        gene_plot_type (`str`): "single" for one gene (or none). "multiple" for more than one gene. 

    Response:
        * **GET + AJAX**:
           * **str**: JSON with ScatterPlot.
        
    Example:

        .. code-block:: bash

            curl -H "X-REQUESTED-WITH: XMLHttpRequest" \\
                 -X GET \\
                 "https://compgen.bio.ub.edu/PlanNET/plot_gene_expression?experiment=2018+Rajewsky+Cell+Atlas&dataset=Dresden&gene_name=dd_Smed_v6_740_0_1%2C+&plot_type=heatmap&ctype=Cluster&only=false"

    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset = request.GET['dataset']
        gene_names = request.GET['gene_name']
        ctype = request.GET['ctype']
        with_color = json.loads(request.GET.get('withcolor', 'false'))
        gene_plot_type = request.GET['gene_plot_type']
        gene_names = gene_names.split(",")

        # First disambiguate gene names
        gene_symbols = list()
        for gene_name in gene_names:
            if gene_name.strip():
                if with_color and gene_plot_type == "single":
                    gene_symbols = [ disambiguate_gene(gene_name, dataset)[0] ]
                    break
                else:
                    gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        conditions = Condition.objects.filter(
            experiment=experiment, 
            cond_type=ConditionType.objects.get(name=ctype))
        
        conditions = sorted(conditions, key= lambda x: condition_sort(x))

        # Do the plot

        if not with_color:
            gene_symbols = []
        
        creator = PlotCreator()
        theplot = creator.create_plot(
            "tsne",
            experiment=experiment,
            dataset=dataset,
            conditions=conditions,
            genes=list(gene_symbols),
            ctype=ctype
        )
        if theplot is not None:
            response = theplot.plot()
        else:
            response = None

        return HttpResponse(json.dumps(response), content_type="application/json")
