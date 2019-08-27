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
        mode = request.GET.get('mode')
        search_term = request.GET.get('search_term')

        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        response = {}



        if mode == "gene":
            # First disambiguate gene names
            gene_symbols = []
            for gene_name in search_term.split(","):
                gene_symbols.extend(disambiguate_gene(gene_name, dataset_name))
            regulatory_links = RegulatoryLinks.objects.filter(experiment=experiment, dataset=dataset, regulator__in=gene_symbols) | RegulatoryLinks.objects.filter(experiment=experiment, dataset=dataset, target__in=gene_symbols)
        else:
            print("REACTOME....")
            search_term = [ x.upper() for x in search_term.split(",") ]
            reactomes = Reactome.objects.filter(experiment=experiment, search_name__in=search_term) | Reactome.objects.filter(experiment=experiment, reactome_id__in=search_term )
            reactomes = list(reactomes.values_list('id', flat=True))

            regulatory_links = RegulatoryLinks.objects.filter(pk__in=ReactomeLinks.objects.filter(reactome__in=reactomes).values_list('regulatorylink'))
            print(regulatory_links)

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
            print(response_to_render)

            response = render_to_string('NetExplorer/regulatory_links_table.html', response_to_render)
        else:
            response = None

        return HttpResponse(response, content_type="application/html")
    else:
        return render(request, 'NetExplorer/404.html')