from ..helpers.common import *


def create_tf_dict(tfs):
    tf_info = {}
    for tf in tfs:
        tf_info[tf.symbol] = {}
        tf_info[tf.symbol]['name'] = tf.name
        tf_info[tf.symbol]['url'] = tf.url
        tf_info[tf.symbol]['tf_name'] = tf.tf_name
        tf_info[tf.symbol]['domain'] = tf.domain
        tf_info[tf.symbol]['number'] = tf.number
        tf_info[tf.symbol]['source'] = tf.source
    return tf_info

def convert_cre_type(cre_type):
    if cre_type == "Enhancers":
        return "enhancer"
    elif cre_type == "Proximal regulatory regions":
        return "promoter"
    else:
        return "any"

def tf_tools(request):
    """
    Views for TF Tools.

    Accepts:
        * **GET**
        
    Response:
        * **experiments** (`list` of :obj:`Experiment`): List of Experiments to which user has access to.
    
    Hint:
        PlanExp works as an async single-page app (for the most part). See `http_api.planexp` for more information.

    """

    if request.is_ajax():
        if request.GET.get("mode") == "search":
            motif_symbol = request.GET.get("tf_symbol")

            cre_type = request.GET.get("cre_type")
            cre_type = convert_cre_type(cre_type)
            tf_motif = TfMotif(symbol=motif_symbol, database="Tf_motif")

            genes = tf_motif.get_planarian_genes(cre_type)
            genes.sort(key= lambda x: (x.name if x.name else "ZZZ", x.symbol))
            genelist = [ "{},{}".format(gene.symbol, gene.name) for gene in genes ]
            genelist = "\n".join(genelist)
            numgenes = str(len(genes))
            response = {
                'res': genes, 
                'symbol': motif_symbol, 
                'genelist': genelist ,
                'numgenes': numgenes
            }
            return render(request, "NetExplorer/tf_search_results.html", response)
        else:
            print("enrichment")
            pass
    else:
        print("Not ajax")
        response = {}
        response['databases'] = Dataset.get_allowed_datasets(request.user)
        search_mode = request.GET.get("search_mode")
        response['search_mode'] = search_mode
        tf_motifs = TfMotif.get_all_from_database()
        response['transcription_factors'] = tf_motifs
        response['tf_motifs_info'] = json.dumps(create_tf_dict(tf_motifs))
        return render(request, 'NetExplorer/tf_tools.html', response)
  