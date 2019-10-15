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
        self.study_results = None
        self.results = None
        self.results_all = None
        self.pvalue_cutoff = 0.05
    
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
            self.study_results = self.goe.run_study(gene_ids, alpha=self.pvalue_cutoff)
            self.results = [ r for r in self.study_results if r.p_fdr_bh <= self.pvalue_cutoff ]
            self.results_all = list(self.results)
            self._keep_best_n()
            return self.results
        except Exception as err:
            return None

    def get_stats(self, gene_set):
        """
        Returns some stats of GO analysis performed
        """
        stats = {'genes_with_go': 0, 'num_of_go': 0, 'input_genes': len(gene_set), 'num_of_sig_go': 0}
        if not self.study_results:
            return stats

        genes_with_go, num_of_go = self.goe.get_item_cnt(self.study_results, "study_items")

        stats['genes_with_go'] = len(genes_with_go)
        stats['num_of_go'] = num_of_go
        stats['input_genes'] = len(gene_set)
        stats['num_of_sig_go'] = len(self.results_all)
        return stats

    def _keep_best_n(self, n=20):
        """
        Filters results to keep best n GO for each domain.
        """
        best_for_domain = {"BP": [], "CC": [], "MF": []}
        domain_counter  = {"BP": 0, "CC": 0, "MF": 0} 
        for result in sorted(self.results, key=lambda x: x.p_fdr_bh):
            if domain_counter[result.NS] < n:
                domain_counter[result.NS] += 1
                best_for_domain[result.NS].append(result)
        self.results = best_for_domain["BP"] + best_for_domain["CC"] + best_for_domain["MF"]



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
        if not self.results_all:
            return None
        golist = [ str(res.goterm) for res in self.results_all ]
        golist = [ row.replace("\t", ",") for row in golist ]
        golist = "\n".join(golist)
        return golist
        

