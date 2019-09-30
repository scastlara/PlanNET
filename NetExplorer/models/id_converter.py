from .common import *


class IDConverter(object):

    def __init__(self, symbols):
        self.symbols = symbols
    
    def convert(self, to_db, by_db="Gene"):
        gene_list = self._initialize_gene_list(self.symbols, to_db)
        intermediate_elements = self._get_intermediate_elements(gene_list, by_db)
        results = self._get_results(intermediate_elements, to_db, by_db)
        print(results)
        return results
            
    def _get_intermediate_elements(self, gene_list, by_db):
        if by_db == "Gene":
            intermediate_elements = self._by_gene(gene_list)
        elif by_db == "Human":
            intermediate_elements = self._by_human(gene_list)
        return intermediate_elements

    def _initialize_gene_list(self, symbols, to_db):
        gene_list = GraphCytoscape()
        gene_list.new_nodes(self.symbols, to_db)
        return gene_list

    def _by_gene(self, gene_list):
        intermediate_elements = []
        for contig in gene_list.nodes:
            genes_for_gene = contig.get_genes()
            intermediate_elements.append((contig, genes_for_gene))
        return intermediate_elements
    
    def _by_human(self, gene_list):
        intermediate_elements = []
        for contig in gene_list.nodes:
            contig.get_homolog()
            if contig.homolog:
                human_homologs = [ contig.homolog.human ]
            else:
                human_homologs = []
            intermediate_elements.append((contig, human_homologs))
        return intermediate_elements

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
