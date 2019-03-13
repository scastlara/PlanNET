from .common import *
from .gene_ontology_data import *
from django.conf import settings


class GeneOntologyEnrichment(object):
    '''
    Class used for GeneOntology Enrichment
    '''
    obodag = GODag(os.path.join(settings.BASE_DIR, 'share', 'go-basic.obo'))
    def __init__(self):
        self.goe = GOEnrichmentStudy(
            go_geneids, 
            geneid2go, 
            GeneOntologyEnrichment.obodag, 
            propagate_counts=False, 
            alpha=0.05, 
            methods=['fdr_bh']
        )
        self.results = None
    
    def get_enriched_gos(self, gene_symbols):
        try:
            gene_ids = [ genesymbol2id[symbol] for symbol in gene_symbols if symbol in genesymbol2id ]
            results = self.goe.run_study(gene_ids)
            self.results = [ r for r in results if r.p_fdr_bh < 0.05 ]
            return self.results
        except Exception as err:
            print(err)
            return None


    def get_plots(self):
        if not self.results:
            return None
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.name += "{NS}.png"

        plot_results(tmp.name, self.results)
        plot_dict = { 'BP': None, 'CC': None, 'MF': None }
        for domain in ["BP", "CC", "MF"]:
            fn = tmp.name.format(NS=domain)
            try:
                plot_dict[domain] = base64.b64encode(open(fn, 'rb').read()).decode('utf-8').replace('\n', '')
            except Exception as err:
                print(err)
                continue
        return plot_dict

    def get_go_list(self):
        if not self.results:
            return None
        
        # GO list

