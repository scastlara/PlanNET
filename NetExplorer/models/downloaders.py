from .common import *

# ------------------------------------------------------------------------------
class DownloadHandler(object):
    """
    Class that handles downloadable files.

    Attributes:
        data_from_node (`dict` of `str`: `fun`): Class attribute, dictionary mapping data type keywords, 
            to the methods that handle them.

    Example::
    
        dhandler = DownloadHandler()
        the_file = dhandler.download_data(identifiers, database, data)
        response = the_file.to_response()
    

    Methods get_*_data returns a list of tuples, each tuple being a line, and each
    element of the tuple being a column.
    """

    def _get_contig_data(node):
        """
        Function to return a line with the contig sequence.
        
        Args:
            node (PlanarianContig): PlanarianContig object.

        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Contig sequence.
                    3. Contig database.
                    4. Gene symbol (if available, otherwise "NA").
        """
        if not node.sequence:
            node.get_all_information()

        genes = node.get_genes()
        gene = "NA"
        if genes:
            gene = genes[0].symbol
        return [(node.symbol, node.sequence, node.database, gene)]

    def _get_orf_data(node):
        """
        Function to return line with contig Open Reading Frame (ORF) 
        and other data.

        Args:
            node (PlanarianContig): PlanarianContig object.
        
        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Contig ORF sequence.
                    3. Contig database.
                    4. Gene symbol (if available, otherwise "NA").
        """
        if not node.orf:
            node.get_all_information()
        genes = node.get_genes()
        gene = "NA"
        if genes:
            gene = genes[0].symbol
        return [(node.symbol, node.orf, node.database, gene)]

    def _get_homology_data(node):
        """
        Function to return line with Homology data for a contig.

        Args:
             node (PlanarianContig): PlanarianContig object.
            
        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Gene symbol (if available, otherwise "NA")..
                    3. Homolog symbol (if available, otherwise "NA").
                    4. Blast E-Value (if available, otherwise "NA").
                    5. Blast Coverage (if available, otherwise "NA").
                    6. EggNOG HMMER E-Value (if available, otherwise "NA").
                    7. PFAM meta-alignment score (if available, otherwise "NA").
        """
        genes = node.get_genes()
        gene = "NA"
        if genes:
            gene = genes[0].symbol
        if node.homolog is not None:
            return [(node.symbol, gene, node.homolog.human.symbol, 
                    node.homolog.blast_eval, node.homolog.blast_cov, 
                    node.homolog.nog_eval, node.homolog.pfam_sc)]
        else:
            return [(node.symbol, gene, "NA", 
                    "NA", "NA", 
                    "NA", "NA")]

    def _get_pfam_data(node):
        """
        Function to return line with PFAM domain data for a contig.

        Args:
            node (PlanarianContig): PlanarianContig object.
        
        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Gene symbol (if available, otherwise "NA").
                    3. PFAM domains, in the form of (`accession`:`start`-`end`), separated by `;`.
        """
        node.get_domains()
        genes = node.get_genes()
        gene = "NA"
        if genes:
            gene = genes[0].symbol

        if node.domains:
            domains = ";".join([ "%s:%s-%s"  % (str(dom.domain.accession), str(dom.s_start), str(dom.s_end)) for dom in node.domains ])
        else:
            domains = "NA"
        
        return([(node.symbol, gene, domains)])

    def _get_go_data(node):
        """
        Function to return line with GO for a contig.

        Args:
            node (PlanarianContig): PlanarianContig object.
        
        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Gene symbol (if available, otherwise "NA").
                    3. GO terms, in the form of (`accession`=`domain`=`name`), separated by `;`.
        """
        node.get_geneontology()
        genes = node.get_genes()
        gene = "NA"
        if genes:
            gene = genes[0].symbol
        gos = ";".join([ go.accession + "=" + go.domain + "=" + go.name  for go in node.gene_ontologies ])
        if not gos:
            gos = "NA"
        return [(node.symbol, gene, gos)]

    def _get_interactions_data(node):
        """
        Function to return several line with interactions for a contig.

        Args:
            node (PlanarianContig): PlanarianContig object.
        
        Returns:
            `list` of `tuple` of `str`: List with data for a row in the downloadable
                file. Contains: 
                    1. Contig symbol.
                    2. Gene symbol (if available, otherwise "NA").
                    3. Interactor contig symbol.
                    4. Interactor gene symbol (if available, otherwise "NA").
                    5. Interaction score (if available, otherwise "NA")
        """
        node.get_neighbours()
        genes1 = node.get_genes()
        gene1 = "NA"
        if genes1:
            gene1 = genes1[0].symbol

        ints = []
        if node.neighbours:
            for interaction in node.neighbours:
                genes2 = interaction.target.get_genes()
                if genes2:
                    gene2 = genes2[0].symbol
                else:
                    gene2 = "NA"
                ints.append((node.symbol, gene1, interaction.target.symbol, gene2, str(interaction.parameters['int_prob'])))
        else:
            ints.append((node.symbol, gene1, "NA", "NA", "NA"))
        return ints

    data_from_node = {
        'contig': _get_contig_data,
        'orf': _get_orf_data,
        'homology': _get_homology_data,
        'pfam': _get_pfam_data,
        'go': _get_go_data,
        'interactions': _get_interactions_data
    }

    def download_data(self, identifiers, database, data):
        """
        Creates file object with the specified data for the
        specified identifiers.

        Args: 
            identifiers (`list` of `str`): List of gene/transcript identifiers.
            database (str): Database name of desired results to download.
            data (str): Desired data to download. 
                Can be ['contig', 'orf', 'homology', 'pfam', 'go', 'interactions']
        
        Returns:
            ServedFile: ServedFile object with the file ready to download.
        """
        fformat = 'csv'
        if data == "contig" or data == "orf":
            fformat = 'fasta'
        dfile = ServedFile(self.get_filename(data), fformat, self.get_header(data))
        for identifier in identifiers:
            try:
                gsearch = GeneSearch(identifier, database)
                nodes = gsearch.get_planarian_contigs()
                for node in nodes:
                    dfile.add_elements(self.data_from_node[data](node))
            except exceptions.NodeNotFound:
                continue
        return dfile

    def get_filename(self, data):
        """
        Returns filename string.

        Args:
            data (str): Desired data to download. 
                Can be ['contig', 'orf', 'homology', 'pfam', 'go', 'interactions']
        
        Returns:
            str: String with filename according to the data to download.
        """
        if data == "contig" or data=="orf":
            filename = "fasta.fa"
        elif data == "homology":
            filename = "homologs.csv"
        elif data == "pfam":
            filename = "domains.csv"
        elif data == "interactions":
            filename = "interactions.csv"
        else:
            filename = "gene_ontologies.csv"
        return filename

    def get_header(self, data):
        """
        Returns header string.

        Args:
            data (str): Desired data to download. 
                Can be ['contig', 'orf', 'homology', 'pfam', 'go', 'interactions']
        
        Return:
            str: String with first line (header) of the file.
        """
        if data == "homology":
            header = "NAME,GENE,HUMAN,BLAST_EVALUE,BLAST_COVERAGE,EGGNOG_EVALUE,META_ALIGNMENT_SCORE\n"
        else:
            header = None
        return header


# ------------------------------------------------------------------------------
class ServedFile(object):
    """
    Class of served files for download.

    Attributes:
        oname (str): String with output filename.
        fformat (str): String with file format, can be 'csv' or 'fasta'.
        header (bool): Bool describing if file should have a header.
        filename (NamedTemporaryFile): NamedTemporaryFile object.
        elements (`list` of `tuple`): List of tuples. Each tuple contains the
            data for each line.
        written (bool): Bool describing if the file has data on it or not.

    Args:
        oname (str): String with output filename.
        fformat (str, optional): String with file format, can be 'csv' or 'fasta'. 
            Defaults to 'csv'.
        header (str, optional): Header string to write on the first line of the file.
            Defaults to `None`.

    """
    def __init__(self, oname, fformat='csv', header=None):
        self.oname = oname
        self.fformat = fformat
        self.header = header
        self.filename = tempfile.NamedTemporaryFile()
        self.elements = []
        self.written = False

    def add_elements(self, elem):
        """
        Adds a register to the list of elements.

        Args:
            elem (`list` of `tuple`): List of tuples. 
                Each tuple corresponds to a line.

        """
        self.elements.extend(elem)
        return self

    def write(self, what=None):
        """
        Writes to temp file.

        Args:
            what (None): Nothing.

        """
        with open(self.filename.name, "w") as fh:
            if self.header is not None:
                fh.write(self.header)
            for elem in self.elements:
                if self.fformat == 'csv':
                    fh.write( "%s\n" % ",".join(elem) )
                elif self.fformat == 'fasta':
                    formatseq = "".join(elem[1][i:i+64] + "\n" for i in range(0,len(elem[1]), 64)) 
                    fh.write(">%s|%s|%s\n%s" % (elem[0], elem[2], elem[3], formatseq))
                else:
                    raise InvalidFormat(self.fformat)
        self.written = True
        return self

    def to_response(self, what=None):
        """
        Creates a response object to be served to the user for download.

        Args:
            what (None): Nothing.

        Returns:
            `HttpResponse`: HttpResponse object with the file to be returned 
                in a request.
                    
        """
        if not self.written:
            self.write(what)
        wrapper = FileWrapper(open(self.filename.name))
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.oname
        response['Content-Length'] = os.path.getsize(self.filename.name)
        return response


from NetExplorer.models import exceptions