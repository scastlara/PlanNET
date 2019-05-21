from .common import *
from .gene_ontology_data import *
from django.conf import settings


class GeneOntologyEnrichment(object):
    """
    Class used for GeneOntology Enrichment.

    Attributes:
        goe (GOEnrichmentStudy): GOEA object from goatools that contains the 
            analysis performed.
        results (`list` of `GOEnrichmentRecord`): Records with overrepresented
            GO terms
    
    """
    _obodag = GODag(os.path.join(settings.BASE_DIR, 'share', 'go-basic.obo'))
    def __init__(self):
        self.goe = GOEnrichmentStudy(
            go_geneids, 
            geneid2go, 
            GeneOntologyEnrichment._obodag, 
            propagate_counts=False, 
            alpha=0.05, 
            methods=['fdr_bh']
        )
        self.results = None
    
    def get_enriched_gos(self, gene_symbols):
        """
        Gets the enriched GO terms in a list of gene symbols.

        Args:
            gene_symbols (str): Human gene symbols to compute enrichment for.
        
        Returns:
            `list` of `GOEnrichmentRecord` or `None`: Records with overrepresented
                GO terms if available, otherwise `None`.
        """
        try:
            gene_ids = [ genesymbol2id[symbol] for symbol in gene_symbols if symbol in genesymbol2id ]
            results = self.goe.run_study(gene_ids)
            self.results = [ r for r in results if r.p_fdr_bh < 0.05 ]
            return self.results
        except Exception as err:
            return None


    def get_plots(self):
        """
        Returns plots for GO analysis.

        Returns:
            `dict` of `str`: `base64`: Dictionary with the three plots (keys: 'BP', 'CC', and 'MF') 
                generated by goatools, encoded as `base64` binary strings. 

        """

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
        """
        Gets list of GO terms formatted for further use.

        Returns:
            `str`: Formatted string with gene ontology data (accession, level, 
                depth, Name, domain) separated by commas. Each line ("\\n")
                corresponds to a different GO term.
        """
        golist = []
        if not self.results:
            return None
        golist = [ str(res.goterm) for res in self.results ]
        golist = [ row.replace("\t", ",") for row in golist ]
        golist = "\n".join(golist)
        return golist
        

