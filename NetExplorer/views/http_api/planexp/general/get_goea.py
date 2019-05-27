from ....helpers.common import *


def get_goea(request):
    """
    Performs Gene Ontology Enrichment Analysis for a given comparison of conditions.
    
    Accepts:
        * **GET**

    Response:
        * **GET**:
           * **str**: JSON with html (template "NetExplorer/goea_plots.html") with GO plots and download button.

    """
    response = dict()

    exp_name = request.GET['experiment']
    c1_name = request.GET['condition1']
    c2_name = request.GET['condition2']
    condition_focus = request.GET['condition_focus']
    dataset_name = request.GET['dataset']
    pvalue_threshold = 0.001
    experiment = Experiment.objects.get(name=exp_name)
    dataset = Dataset.objects.get(name=dataset_name)
    condition1 = Condition.objects.get(name=c1_name, experiment=experiment)
    condition2 = Condition.objects.get(name=c2_name, experiment=experiment)
    expression = ExpressionRelative.objects.filter(
        experiment=experiment, dataset=dataset, 
        condition1=condition1, condition2=condition2, pvalue__lte=pvalue_threshold)
    if not expression.exists():
        # In case condition1 and condition2 are reversed in Database
        expression = ExpressionRelative.objects.filter(
            experiment=experiment, dataset=dataset, 
            condition1=condition2, condition2=condition1, pvalue__lte=pvalue_threshold)

    if expression:
        if condition_focus == expression[0].condition1.name:
            # Must get Positive fold changes
            gene_set = list(expression.filter(fold_change__gte=0).values_list('gene_symbol', flat=True))

        else:
            # Must get Negative fold changes
            gene_set = list(expression.filter(fold_change__lte=0).values_list('gene_symbol', flat=True))
        # Get homologous proteins
        gene_human_set = GraphCytoscape.get_homologs_bulk(gene_set, dataset_name).values()
        go_analysis = GeneOntologyEnrichment()
        go_analysis.get_enriched_gos(gene_human_set)

        plots = go_analysis.get_plots()
        go_list = go_analysis.get_go_list()

        try:
            html_to_return = render_to_string('NetExplorer/goea_plots.html', { 'plots': plots, 'golist': go_list })
        except Exception as err:
            print(err)
        
        response['html'] = html_to_return

    return HttpResponse(json.dumps(response), content_type="application/json")