from .common import *


def plot_gene_coexpression(request):
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset = request.GET['dataset']
        gene1_name = request.GET['gene1_name']
        gene2_name = request.GET['gene2_name']
        ctype = request.GET['ctype']
        response = None

        # First disambiguate gene names
        gene_symbols = [ gene1_name, gene2_name ]
        for gene_name in [gene1_name, gene2_name]:
            gene_name = gene_name.replace(",", "")
            gene_symbols.extend(disambiguate_gene(gene_name, dataset))

        # Get Experiment and conditions
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset)
        ctype_tosearch = ctype
        conditions = Condition.objects.filter(
                        experiment__name=exp_name, 
                        cond_type=ConditionType.objects.get(name=ctype_tosearch))
        conditions = sorted(conditions, key= lambda x: condition_sort(x))

        # Filter genes to only those in experiment
        genes_in_experiment = ExperimentGene.objects.filter(
            experiment=experiment,
            gene_symbol__in=gene_symbols
        ).values_list("gene_symbol", flat=True)
        genes_in_experiment = list(genes_in_experiment)

        if len(genes_in_experiment) != 2:
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            creator = PlotCreator()
            theplot = creator.create_plot(
                'coexpression', 
                experiment=experiment,
                dataset=dataset,
                conditions=conditions,
                genes=genes_in_experiment,
                ctype=ctype,
            )

            response = theplot.plot()

        return HttpResponse(json.dumps(response), content_type="application/json")