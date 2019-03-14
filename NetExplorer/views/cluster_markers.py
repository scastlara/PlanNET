from .common import *

def cluster_markers(request):
    """
    View from PlanExp that returns the HTML of a table with markers for each cluster
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset_name = request.GET['dataset']
        cluster_name = request.GET['cluster']
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        condition = Condition.objects.get(experiment=experiment, name=cluster_name)

        response = dict()
        markers = ClusterMarkers.objects.filter(experiment=experiment, dataset=dataset, condition=condition).order_by("-auc")
        if markers:
            all_contigs = [ mark.gene_symbol for mark in markers ]
            homologs = GraphCytoscape.get_homologs_bulk(all_contigs, dataset_name)
            genes = GraphCytoscape.get_genes_bulk(all_contigs, dataset_name)

            for mark in markers:
                
                if mark.gene_symbol in homologs:
                    mark.homolog = homologs[mark.gene_symbol]
                if mark.gene_symbol in genes:
                    mark.gene = genes[mark.gene_symbol]['gene']
                    mark.name = genes[mark.gene_symbol]['name']
            try:
                response = render_to_string('NetExplorer/markers_table.html', { 'markers': markers, 'experiment': experiment, 'database': dataset })
            except Exception as err:
                print(err)
                response = None
        else:
            response = None
        return HttpResponse(response, content_type="application/html")
    else:
        return render(request, 'NetExplorer/404.html')