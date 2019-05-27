from ....helpers.common import *

def regulatory_links(request):
    """
    Returns a summary of a selected experiment.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        dataset (`str`): Dataset name.
        group (`int`): Integer indicating group of regulatory links to retrieve (1 to 10).

    Response:
        * **GET + AJAX**:
           * **str**: HTML with regulatory links table (template "NetExplorer/regulatory_links_table.html")

    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset_name = request.GET['dataset']
        group = request.GET.get('group')
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        response = dict()

        if group is None:
            group = 1
        regulatory_links = RegulatoryLinks.objects.filter(experiment=experiment, dataset=dataset, group=group)
        if regulatory_links:
            all_contigs = set()
            for link in regulatory_links:
                all_contigs.add(link.regulator)
                all_contigs.add(link.target)
            
            homologs = GraphCytoscape.get_homologs_bulk(list(all_contigs), dataset_name)
            genes = GraphCytoscape.get_genes_bulk(list(all_contigs), dataset_name)
            for link in regulatory_links:
                # Regulators
                if link.regulator in homologs:
                    link.regulator_homolog = homologs[link.regulator]
                if link.regulator in genes:
                    link.regulator_gene = genes[link.regulator]['gene']
                    link.regulator_name = genes[link.regulator]['name']
                # Targets
                if link.target in homologs:
                    link.target_homolog = homologs[link.target]
                if link.target in genes:
                    link.target_gene = genes[link.target]['gene']
                    link.target_name = genes[link.target]['name']
            response_to_render = { 'links' : regulatory_links, 'database': dataset }

            response = render_to_string('NetExplorer/regulatory_links_table.html', response_to_render)
        else:
            response = None

        return HttpResponse(response, content_type="application/html")
    else:
        return render(request, 'NetExplorer/404.html')