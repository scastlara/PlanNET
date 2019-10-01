from .common import *


class IDConverter(object):

    def __init__(self, symbols):
        self.symbols = symbols
    
    def convert(self, to_db, by_db="Gene"):
        intermediate_elements = self._get_intermediate_elements(to_db, by_db)
        results = self._get_results(intermediate_elements, to_db, by_db)
        print(results)
        return results
            
    def _get_intermediate_elements(self, to_db, by_db):
        intermediate_elements = []
        for symbol in self.symbols:
            gene_search = GeneSearch(symbol, to_db)
            if by_db == "Gene":
                genes_for_symbol = gene_search.get_planarian_genes()
            elif by_db == "Human":
                genes_for_symbol = gene_search.get_human_genes()
                print(genes_for_symbol)
            input_node = self._return_input_node(gene_search)
            intermediate_elements.append((input_node, genes_for_symbol))
        return intermediate_elements

    def _return_input_node(self, gene_search):
        if gene_search.sterm_database == "Human":
            node_obj = HumanNode(gene_search.sterm, gene_search.sterm_database, query=False)
        elif gene_search.sterm_database == "Smesgene":
            node_obj = PlanarianGene(gene_search.sterm, gene_search.sterm_database, query=False)
        else:
            node_obj = PlanarianContig(gene_search.sterm, gene_search.sterm_database, query=False)
        return node_obj

    def _get_results(self, intermediate_elements, to_db, by_db):
        results = []
        for element in intermediate_elements:
            contigs_for_element = []
            intermediates_for_element = []
            for target_element in element[1]:
                if to_db == by_db:
                    contigs_for_element.append(target_element)
                else:
                    contigs_for_element.extend(target_element.get_planarian_contigs(to_db))
                    intermediates_for_element.append(target_element)
            results.append((element[0], intermediates_for_element, list(set(contigs_for_element))))
        return results
