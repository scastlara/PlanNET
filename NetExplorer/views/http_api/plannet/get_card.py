from ...helpers.common import *
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.storage import default_storage
from django.contrib.staticfiles import finders

def get_card(request, symbol=None, database=None):
    """
    Returns a card with information about a human gene, a planarian gene or a 
    planarian contig.
    
    Accepts:
        * **GET**
        * **GET + AJAX**

    Args:
        symbol (`str`): Identifier of entity for which to generate card.
        database (`str`): Database of symbol.

    Response:
        * **GET**:
            * **node** (:obj:`Smesgene` or :obj:`Human` or :obj:`PlanarianContig`): Instance of card element.
            * **transcripts** (`list` of :obj:`PlanarianContig`): List of contigs associated with gene (only for :obj:`PlanarianGene`) 
            * **best_transcript** (:obj:`PlanarianContig`): Best planarian contig for gene (only for :obj:`PlanarianGene`)
            * **json_graph** (str): Interaction graph of predicted interactions in JSON format (only for :obj:`PlanarianGene` or :obj:`PlanarianContig`). 
            * **homologs** (`list` of `tuple`): Homologous :obj:`PlanarianContig` s for Human gene. First element is Database name, second is :obj:`PlanarianContig` object (only for :obj:`Human`).
            * **domains** (str): PFAM domains in JSON format (only for :obj:`PlanarianContig`).

        * **GET + AJAX**:
            * **HttpResponse**: Response with a file.
    
    Example:

        .. code-block:: bash

            curl -H "X-REQUESTED-WITH: XMLHttpRequest" \\
                 -H "Content-Type: application/json"   \\
                 -X GET \\
                 "https://compgen.bio.ub.edu/PlanNET/info_card?target=SMESG000005930.1&targetDB=Smesgene"
                 
    """
    if request.method == 'GET' and request.is_ajax():
        symbol    = request.GET['target']
        database  = request.GET['targetDB']
        template  = ""
    try:
        
        if database == "Human":
            template = "NetExplorer/human_card.html"
            card_node = HumanNode(symbol, database)
            homologs = card_node.get_homologs()
            card_node.get_summary()
            all_databases = Dataset.get_allowed_datasets(request.user)
            sorted_homologs = list()
            for db in all_databases:
                if db.name in homologs:
                    sorted_homologs.append((db.name, homologs[db.name]))
                else:
                    sorted_homologs.append((db.name, list()))
        elif database == "Smesgene":
            template = "NetExplorer/smesgene_card.html"
            card_node = PlanarianGene(symbol, database)
            contigs = card_node.get_planarian_contigs()
            best_contig = card_node.get_best_transcript()
            graph = GraphCytoscape()
            card_node.get_transcription_factors("promoter")
            #card_node.get_transcription_factors("enhancer")
            has_logo_proximal = gene_has_logo("promoter", card_node.symbol)
            #has_logo_enhancer = gene_has_logo("enhancer", card_node.symbol)
            has_logo_enhancer = False

            print(has_logo_proximal)
            if best_contig:
                best_contig.get_homolog()
                best_contig.get_neighbours()
                best_contig.get_geneontology()
                if best_contig.homolog:
                    best_contig.homolog.human.get_summary()
                nodes, edges = best_contig.get_graphelements()
                graph.add_elements(nodes)
                graph.add_elements(edges)

        else:
            template = "NetExplorer/contig_card.html"
            gsearch = GeneSearch(symbol, database)
            card_node = gsearch.get_planarian_contigs()[0]
            card_node.get_summary()
            card_node.get_neighbours()
            card_node.get_domains()
            card_node.get_geneontology()
            nodes, edges = card_node.get_graphelements()
            graph = GraphCytoscape()
            graph.add_elements(nodes)
            graph.add_elements(edges)
    except Exception as err:
        logging.error("Can't find symbol {} - {} in get_card() {}".format(symbol, database, err))
        return render_to_response('NetExplorer/not_interactome.html')
    if database == "Human":
       response = {
            'node' : card_node,
            'homologs': sorted_homologs
        }
    elif database == "Smesgene":
        response = {
            'node': card_node,
            'transcripts': contigs,
            'best_transcript': best_contig,
            'json_graph': graph.to_json(),
            'has_logo_proximal': has_logo_proximal,
            'has_logo_enhancer': has_logo_enhancer
        }
    else:
        response = {
            'node'      : card_node,
            'json_graph': graph.to_json(),
            'domains'   : card_node.domains_to_json()
        }
    
    if request.is_ajax():
        response['base_template'] = 'NetExplorer/null.html'
    else:
        response['base_template'] = 'NetExplorer/base.html'
    
    return render(request, template, response)


def gene_has_logo(re_type, symbol):
    print('Images/{}-images/{}-promoter.png'.format(re_type, symbol))
    return finders.find('Images/{}-images/{}-promoter.png'.format(re_type, symbol))