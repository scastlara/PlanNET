from .common import *

# NEO4J CLASSES
# ------------------------------------------------------------------------------
class Node(object):
    """
    Base class for all the nodes in the database.

    Attributes:
        symbol (str): String containing the symbol attribute in Neo4j of a given node.
        database (str): The Label for the symbol in Neo4j.
        neighbours (:obj:`list` of :obj:`PredInteraction`): List of Interaction objects 
            connecting nodes adjacent to the Node.
        domains (`list` of `HasDomain`): HasDomain objects describing domains 
            in the sequence/node. 
        allowed_databases (`set` of `str`): Class attribute. Set of allowed 
            Labels for Node.
    """

    def __init__(self, symbol, database):
        super(Node, self).__init__()
        self.symbol     = symbol
        self.database   = database.capitalize()
        self.neighbours = []
        self.domains    = []
        if self.database not in self.allowed_databases:
            raise exceptions.IncorrectDatabase(self.database)

    def __query_node(self):
        """
        This method will be overriden by HumanNode or PlanarianContig.
        It will query the Neo4j database and it will get the required node.
        """

    def get_domains(self):
        """
        Gets domains annotated for a particular Node. It updates the Node attribute
        and it also returns the domain.

        Returns:
            Union([`list` of `Domain`, None]): List of domains annotated for 
            this Node. None if there are no domain annotations.
        """
        query = neoquery.DOMAIN_QUERY % (self.database, self.symbol)

        results = GRAPH.run(query)
        results = results.data()

        if results:
            annotated_domains = []
            for row in results:
                domain = Domain(
                    accession   = row['accession'],
                    description = row['description'],
                    identifier  = row['identifier'],
                    mlength     = row['mlength']
                )
                domain_annotation = HasDomain(
                    node    = self,
                    domain  = domain,
                    p_start = row['p_start'],
                    p_end   = row['p_end'],
                    s_start = row['s_start'],
                    s_end   = row['s_end'],
                    perc    = row['perc']
                )
                annotated_domains.append(domain_annotation)
            annotated_domains.sort(key=lambda x: x.s_start)
            self.domains = annotated_domains
            return self.domains
        else:
            self.domains = None
            return self.domains

    def domains_to_json(self):
        """
        This function will return a json string with the information about
        the domains of the node. You have to call "get_domains()" before!

        Returns:
            str: JSON string with Domains data, see Domain.to_jsondict().
        """
        if self.domains is None:
            return None
        else:
            all_domains = [ dom.to_jsondict() for dom in self.domains ]
            json_data   = json.dumps(all_domains)
            return json_data

    def __str__(self):
        return "{} - {}".format(self.symbol, self.database)

# ------------------------------------------------------------------------------
class Homology(object):
    """
    Class for homology relationships between a PlanarianContig and a HumanNode.

    Attributes:
        human (Human): Human object.
        blast_cov (float): Float with BLAST coverage value in %.
        blast_eval (float): Float with BLAST e-value. 
        blast_brh (bool): Bool flag indicating if homology is best reciprocal
            hit in BLAST alignment. 
        nog_brh (bool): Bool flag indicating if homology is best reciprocal 
            hit in EggNOG alignment.
        nog_eval (float): Float with EggNOG alignment e-value.
        pfam_sc (float): Float with pfam meta-alignment score.
        pfam_brh (bool): Bool flag indicating if homology is best reciprocal 
            hit in pfam alignment.
        prednode (PlanarianContig): PlanarianContig object.
    
    Args:
        human (Human): Human object.
        blast_cov (float, optional): Float with BLAST coverage value in %.
        blast_eval (float, optional): Float with BLAST e-value. 
        blast_brh (bool, optional): Bool flag indicating if homology is best reciprocal
            hit in BLAST alignment. 
        nog_brh (bool, optional): Bool flag indicating if homology is best reciprocal 
            hit in EggNOG alignment.
        nog_eval (float, optional): Float with EggNOG alignment e-value.
        pfam_sc (float, optional): Float with pfam meta-alignment score.
        pfam_brh (bool, optional): Bool flag indicating if homology is best reciprocal 
            hit in pfam alignment.
        prednode (PlanarianContig, optional): PlanarianContig object.
    """

    def __init__(
            self,  human, blast_cov=None, blast_eval=None, 
            nog_brh=None, pfam_sc=None, nog_eval=None, 
            blast_brh=None, pfam_brh=None, prednode=None):
        self.prednode   = prednode
        self.human      = human
        self.blast_cov  = blast_cov
        self.blast_eval = blast_eval
        self.nog_brh    = nog_brh
        self.pfam_sc    = pfam_sc
        self.nog_eval   = nog_eval
        self.blast_brh  = blast_brh
        self.pfam_brh   = pfam_brh


# ------------------------------------------------------------------------------
class Domain(object):
    """
    Class for PFAM domains.

    Attributes:
        accession (str): String with accession for pfam domain (PFXXXXX).
        description (str): String with description for pfam domain.
        identifier (str): String with identifier for pfam domain.
        mlength (int): Integer with domain length.
        pfam_regexp (str): Class attribute. Regex for PFAM domain accessions.

    Args:
        accession (str): String with accession for pfam domain (PFXXXXX).
        description (str, optional): String with description for pfam domain.
        identifier (str, optional): String with identifier for pfam domain.
        mlength (int, optional): Integer with domain length.
        pfam_regexp (str, optional): Class attribute. Regex for PFAM domain accessions.
    """

    pfam_regexp = r'PF\d{5}'

    def __init__(self, accession=None, description=None, identifier=None, mlength=None):
        if accession is None and identifier is None:
            raise ValueError("Pfam Domains should be initialzied with accession OR identifier.")

        if accession and not re.match(Domain.pfam_regexp, accession):
            raise exceptions.NotPFAMAccession(accession)
        
        if identifier and not accession:
            self._get_domain_by_identifier(identifier)
        else:
            self.accession   = accession
            self.description = description
            self.identifier  = identifier
            self.mlength     = mlength

    @classmethod
    def is_symbol_valid(cls, symbol):
        """
        Classmethod for checking if accession is a valid PFAM accession.

        Args:
            symbol (str): Symbol to check if it's a valid PFAM accession.

        Returns:
            bool: `True` if it is valid, `False` otherwise.
        """
        return re.match(cls.pfam_regexp, symbol)

    def get_planarian_contigs(self, database):
        """
        Returns a list of PlanarianContigs of 'database'.

        Args:
            database: str, database from which to retrieve the planarian contigs.
        
        Returns:
            `list` of `PlanarianContigs`: PlanarianContigs with this domain 
            annotated.

        Raises:
            NodeNotFound: raised if there are no planarian contigs with this Domain.
        """
        query = "";
        if not re.match(Domain.pfam_regexp + r'\.\d+', self.accession):
            # Fuzzy pfam accession (no number)
            acc_regex = self.accession + ".*"
            query = neoquery.DOMAIN_TO_CONTIG_FUZZY % (database, acc_regex)
        else:
            query = neoquery.DOMAIN_TO_CONTIG % (database, self.accession)

        results = GRAPH.run(query)
        results = results.data()
        nodes = []
        if results:
            for row in results:
                nodes.append(PlanarianContig(row['symbol'], database, query=False))
            return nodes
        else:
            raise exceptions.NodeNotFound(self.accession, "Pfam-%s" % database)

    def get_planarian_genes(self, database):
        query = neoquery.GET_GENES_FROMDOMAIN_QUERY % (database, self.accession)
        results = GRAPH.run(query)
        results = results.data()
        planarian_genes = []
        if results:
            for row in results:
                smesgene = PlanarianGene(
                    row['symbol'], 
                    'Smesgene', 
                    name=row['name'], 
                    start=row['start'], 
                    end=row['end'], 
                    strand=row['strand'], 
                    sequence=row['sequence'],
                    query=False
                )
                planarian_genes.append(smesgene)

        return planarian_genes


    def _get_domain_by_identifier(self, identifier):
        """
        Queries domain by identifier instead of accession. Fills all attributes.
        """
        query = neoquery.DOMAIN_IDENTIFIER_QUERY % (identifier.upper())
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.accession = results[0]['accession']
            self.identifier = results[0]['identifier']
            self.description = results[0]['description']
            self.mlength = results[0]['mlength']
        else:
            raise exceptions.NodeNotFound(identifier, "Pfam")


# ------------------------------------------------------------------------------
class HasDomain(object):
    """
    Class for relationships between a node and a Pfam domain annotated on the sequence.

    Attributes:
        domain (Domain): Domain object.
        node (Node): Node object.
        p_start (int): Integer describing the start coordinate (1-indexed) on the PFAM domain.
        p_end (int): Integer describing the end coordinate (1-indexed) on the PFAM domain.
        s_start (int): Integer describing the start coordinate (1-indexed) on the sequence.
        s_end (int): Integer describing the end coordinate (1-indexed) on the sequence.
        perc (float): Float with % of domain in sequence.

    """
    def __init__(self, domain, node, p_start, p_end, s_start, s_end, perc):
        self.domain  = domain
        self.node    = node
        self.p_start = int(p_start)
        self.p_end   = int(p_end)
        self.s_start = int(s_start)
        self.s_end   = int(s_end)
        self.perc    = perc

    def to_jsondict(self):
        """
        Transforms data for Sequence-Domain relationship to a JSON string.

        Returns:
            dict: Dictionary with JSON structure. Has the following keys::

                {
                    'accession': 'Domain accession',
                    'description': 'Domain description',
                    'identifier': 'Domain identifier',
                    'mlength': 'Length (in aa) of PFAM domain',
                    'p_start': 'PFAM domain start coordinate',
                    'p_end': 'PFAM domain end coordinate',
                    's_start': 'PFAM domain sequence start coordinate',
                    's_end': 'PFAM domain sequence start coordinate',
                    'perc': 'Percentage of Domain in sequence'
                }

        """
        json_dict = {}
        json_dict['accession']   = self.domain.accession
        json_dict['description'] = self.domain.description
        json_dict['identifier']  = self.domain.identifier
        json_dict['mlength']     = self.domain.mlength
        json_dict['p_start']     = self.p_start
        json_dict['p_end']       = self.p_end
        json_dict['s_start']     = self.s_start
        json_dict['s_end']       = self.s_end
        json_dict['perc']        = self.perc
        return json_dict

# ------------------------------------------------------------------------------
class PredInteraction(object):
    """
    Class for predicted interactions.
    Source and target are :obj:`PlanarianContig` attributes.

    Attributes:
        source_symbol (str): Symbol of parent node of interaction.
        target (Node): :obj:`Node` object of the child node of the interaction.
        database (str): Neo4j label of parent and child nodes.
        parameters (`dict`): Dictionary containing the interaction properties.
            Has following structure::

                {
                    'int_prob': float, 
                    'path_length': int, 
                    'cellcom_nto': float, 
                    'molfun_nto': float, 
                    'bioproc_nto': float, 
                    'dom_int_sc': float
                }
    
    Args:
        source_symbol (str): Symbol of parent node of interaction.
        target (Node): :obj:`Node` object of the child node of the interaction.
        database (str): Neo4j label of parent and child nodes.
        parameters (:obj:`dict`, optional): Dictionary containing the 
            interaction properties. Defaults to None::
            
                {
                    'int_prob': float, 
                    'path_length': int, 
                    'cellcom_nto': float, 
                    'molfun_nto': float, 
                    'bioproc_nto': float, 
                    'dom_int_sc': float
                }

        query (bool): Bool flag indicating if interaction should be queried to 
            database on creation. Defaults to True. Query will only be performed
            if query = `True` and parameters = None.
    """

    def __init__(self, source_symbol, target, database, parameters=None, query=True):
        self.source_symbol = source_symbol
        self.target        = target
        self.database      = database
        self.parameters    = parameters
        if query and self.parameters is None:
            self.__query_interaction()

    def __query_interaction(self):
        """
        This private method will fetch the interaction from the DB. It will fill 
        the attributes ['int_prob', 'path_length', 'cellcom_nto', 'molfun_nto', 'bioproc_nto', 'dom_int_sc'] 
        of the :obj:`PredInteraction` instance. If interaction is not found, they all will 
        be `None`.
        """
        query = neoquery.PREDINTERACTION_QUERY % (self.database, self.database, self.source_symbol, self.target.symbol)

        results = GRAPH.run(query)
        results = results.data()

        if results:
            for row in results:
                self.parameters['int_prob']    = row['int_prob']
                self.parameters['path_length'] = row['path_length']
                self.parameters['cellcom_nto'] = row['cellcom_nto']
                self.parameters['molfun_nto']  = row['molfun_nto']
                self.parameters['bioproc_nto'] = row['bioproc_nto']
                self.parameters['dom_int_sc']  = row['dom_int_sc']

    def to_jsondict(self):
        """
        This function takes a PredInteraction object and returns a dictionary with the necessary
        structure to convert it to json and be read by cytoscape.js.

        Returns:
            `dict`: Serialized `PredInteraction`.

            .. code-block:: python

                {
                    'data': 
                        {
                            'id': 'edge identifier',
                            'source': 'node identifier',
                            'target': 'node identifier',
                            'pathlength': int,
                            'probability': float,
                            'colorEdge': 'HEX color code',
                        }
                }

        """
        element         = {}
        element['data'] = {}
        element['data']['id']          = "-".join(sorted((self.source_symbol, self.target.symbol)))
        element['data']['source']      = self.source_symbol
        element['data']['target']      = self.target.symbol
        if self.parameters is not None:
            element['data']['pathlength']  = self.parameters['path_length']
            element['data']['probability'] = self.parameters['int_prob']

            if self.parameters['path_length'] == 1:
                element['data']['colorEDGE']   = "#72a555"
            else:
                element['data']['colorEDGE']   = "#CA6347"
        else:
            element['data']['colorEDGE']   = "#CA6347"

        return element

    def __hash__(self):
        return hash((self.source_symbol, self.target.symbol, self.database))

    def __eq__(self, other):
        return (self.source_symbol, self.target.symbol, self.database) == (other.source_symbol, other.target.symbol, other.database)


# ------------------------------------------------------------------------------
class HumanNode(Node):
    """
    Human node class definition. Inherits from 'Node'.

    Attributes:
        summary: String with gene summary.
        summary_source: String with the source of the summary.
    """

    allowed_databases = set(["Human"])

    def __init__(self, symbol, database, query=True):
        super(HumanNode, self).__init__(symbol, database)
        if query:
            self.__query_node()
        self.summary = None
        self.summary_source = None

    def __query_node(self):
        query = neoquery.HUMANNODE_QUERY % (self.database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                self.symbol   = row["symbol"]
        else:
            raise exceptions.NodeNotFound(self.symbol, self.database)

    def get_neighbours(self):
        """
        Gets HumanNodes that interact with this HumanNode. Not implemented yet.
        """
        pass

    def to_jsondict(self):
        """
        Serializes HumanNode to a dictionary for converting it to JSON.

        Returns:
            `dict`: Serialized HumanNode.

                .. code-block:: python

                    {
                        'data': 
                            {
                                'id': 'node identifier',
                                'name': 'node name',
                                'database': 'Human'
                            }
                    }

        """
        element                     = {}
        element['data']             = {}
        element['data']['id']       = self.symbol
        element['data']['name']     = self.symbol
        element['data']['database'] = self.database
        return element

    def get_planarian_genes(self, database):
        """
        Gets planarian gene objects (PlanarianGene) connected to HumanNode
        through contigs of dataset 'database', i.e.: (:Human)->(:Database)->(:Smesgene)

        Args:
            database (str): Database of contigs to get PlanarianGene
        
        Returns:
            list: List of :obj:`PlanarianGene` instances.
        """
        query = neoquery.GET_GENES_FROMHUMAN_QUERY % (database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            smesgenes = []
            for row in results:
                smesgene = PlanarianGene(
                    row['symbol'], 
                    'Smesgene', 
                    name=row['name'], 
                    start=row['start'], 
                    end=row['end'], 
                    strand=row['strand'], 
                    sequence=row['sequence'],
                    query=False
                )
                homology = Homology(
                    prednode   = PlanarianContig(row['prednode_symbol'], database, query=False),
                    human      = self,
                    blast_cov  = row['blast_cov'],
                    blast_eval = row['blast_eval'],
                    nog_brh    = row['nog_brh'],
                    pfam_sc    = row['pfam_sc'],
                    nog_eval   = row['nog_eval'],
                    blast_brh  = row['blast_brh'],
                    pfam_brh   = row['pfam_brh']
                )
                smesgene.homolog = homology
                smesgenes.append(smesgene)
            return smesgenes
        else:
            return []


    def get_summary(self):
        """
        Retrieves gene summary when available and saves it into attribute.
        """
        query = neoquery.SUMMARY_QUERY % (self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.summary = results[0]['summary']
            self.summary_source = results[0]['summary_source']
        else:
            self.summary = "NA"
            self.summary_source = "NA"
        return self            

    def get_planarian_contigs(self, database):
        """
        Gets all PlanarianContigs homologous to HumanNode.

        Args:
            database (str): Database from which to retrieve planarian contigs.

        Returns:
            `list`: :obj:`PlanarianContig` objects.
        """
        homologs = self.get_homologs(database)
        planarian_contigs = []
        for db, homologies in homologs.items():
            for homology in homologies:
                planarian_contigs.append(homology.prednode)
        return planarian_contigs

    def get_homologs(self, database="ALL"):
        """
        Gets all homologs of the specified database.

        Args:
            database (str): Database of desired homologous planarian contigs. Defaults to "ALL".
        Returns:
            `dict`: Dictionary with homologous contigs to HumanNode.
            
                .. code-block:: python

                    {
                        'database1': [Homology, Homology, ...],
                        ...
                    } 

        """
        # Initialize homologs dictionary
        homologs         = {}
        database_to_look = set()
        query_to_use = neoquery.HOMOLOGS_QUERY
        if database == "ALL":
            database_to_look = set(DATABASES)
            query_to_use = neoquery.HOMOLOGS_QUERY_ALL % (self.symbol)
        else:
            database_to_look = set([database])
            query_to_use = neoquery.HOMOLOGS_QUERY % (database, self.symbol)
        for db in database_to_look:
            homologs[db] = []

        # Get the homologs
        results  = GRAPH.run(query_to_use)
        results  = results.data()
        if results:
            for row in results:
                database = [ database for database in row['database'] if database != "PlanarianContig" ][0]
                if database not in database_to_look:
                    continue
                try:
                    homolog_node = PlanarianContig(row['homolog'], database, query=False)
                    homolog_node.get_gene_name()
                except Exception as err:
                    continue
                homolog_rel    = Homology(
                    prednode   = homolog_node,
                    human      = self,
                    blast_cov  = row['blast_cov'],
                    blast_eval = row['blast_eval'],
                    nog_brh    = row['nog_brh'],
                    pfam_sc    = row['pfam_sc'],
                    nog_eval   = row['nog_eval'],
                    blast_brh  = row['blast_brh'],
                    pfam_brh   = row['pfam_brh']
                )
                homolog_node.homolog = homolog_rel
                homologs[database].append(homolog_rel)
        if homologs:
            return homologs
        else:
            logging.info("NO HOMOLOGS")
            return None

# ------------------------------------------------------------------------------
class WildCard(object):
    """
    Class for wildcard searches. Returns a list of symbols.

    Args:
        search (str): String to search.
        database (str): Database (label in neo4j) for the search.

    Attributes:
        search (str): String to search.
        database (str): Database (label in neo4j) for the search.
    """
    def __init__(self, search, database):
        search = search.upper()
        self.search   = search.replace("*", ".*")
        self.database = database

    def get_human_genes(self):
        """
        Gets list of :obj:`HumanNode` objects matching the wildcard query.

        Returns:
            `list`: :obj:`HumanNode` objects.
        """
        query   = neoquery.SYMBOL_WILDCARD % (self.database, self.search)
        results = GRAPH.run(query)
        results = results.data()
        list_of_nodes = []
        if results:
            for row in results:
                list_of_nodes.append(HumanNode(row['symbol'], "Human", query=False))
        return list_of_nodes

    def get_planarian_genes(self):
        """
        Gets list of :obj:`PlanarianGene` objects matching the wildcard query.

        Returns:
            `list`: :obj:`PlanarianGene` objects.
        """
        query = neoquery.NAME_WILDCARD % (self.database, self.search)
        results = GRAPH.run(query)
        results = results.data()
        list_of_nodes = []
        if results:
            for row in results:
                list_of_nodes.append(PlanarianGene(row['symbol'], "Smesgene", name=row['name'], query=False))
        return list_of_nodes


# ------------------------------------------------------------------------------
class PlanarianContig(Node):
    """
    Class for planarian nodes.

    Args:
        symbol (str): Node symbol.
        database (str): Label for Neo4j.
        sequence (str): Contig nucleotide sequence.
        orf (str): Open Reading Frame aa sequence.
        name (str): Name of the contig according to its gene annotation.
        gene (:obj:`PlanarianGene`): Gene predicted to have this transcript as a product.
        homolog (:obj:`Homology`): :obj:`Homology` object with human homolog gene.
        important (bool): Bool indicating if Node should be marked on graph visualization. 
            Defaults to `False`.
        degree (int): Integer with the degree (number of connections) of the node.
        query (bool): Flat to indicate if database should be queried. Defaults to `False`.

    Attributes:
        symbol (str): Node symbol.
        database (str): Label for Neo4j.
        sequence (str): Contig nucleotide sequence.
        orf (str): Open Reading Frame aa sequence.
        orflength (int): Length of Open Reading Frame.
        gccount (float): % of GC in contig sequence.
        gene_ontologies (`list`): List of `GeneOntology` objects that its HumanNode has 
            annotated.
        name (str): Name of the contig according to its gene annotation.
        gene (:obj:`PlanarianGene`): Gene predicted to have this transcript as a product.
        homolog (:obj:`Homology`): :obj:`Homology` object with human homolog gene.
        important (bool): Bool indicating if Node should be marked on graph visualization. 
            Defaults to `False`.
        degree (int): Integer with the degree (number of connections) of the node.
        allowed_databases (`dict`): Class attribute, dictionary with names of neo4j 
            labels for planarian genes.
    """
    allowed_databases = ALL_DATABASES

    def __init__(self, symbol, database,
                 sequence=None, name=None, gene=None,
                 orf=None, homolog=None, important=False,
                 degree=None, query=True):
        super(PlanarianContig, self).__init__(symbol, database)
        self.sequence = sequence
        self.orf = orf
        self.homolog = homolog
        self.important = important
        self.degree = degree
        self.gccont = None
        self.length = None
        self.orflength = None
        self.gene_ontologies = []
        self.name = name
        self.gene = gene

        if self.symbol.startswith("_"):
            self.symbol = "dd_Smed_v6" + self.symbol

        if sequence is None and query:
            self.__query_node()
            self.get_gene_name()

    def get_gene_name(self):
        """
        Gets gene name if possible and loads `gene` and `name` attributes.
        """
        if self.gene is None:
            query = neoquery.GET_GENE % (self.database, self.symbol)
            results = GRAPH.run(query)
            results = results.data()
            if results:
                self.gene = results[0]['genesymbol']
                if results[0]['name']:
                    self.name = results[0]['name']
            else:
                self.gene = None
                self.name = None
        return self 

    def get_genes(self):
        """
        Gets Genes to which this contig maps.

        Returns:
            `list`: List of :obj:`PlanarianGene` objects that this contig is 
                associated with.
        """
        query = neoquery.GET_GENES_QUERY % (self.database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            return [ 
                PlanarianGene(
                    res['symbol'], 
                    'Smesgene', 
                    name=res['name'], 
                    start=res['start'], 
                    end=res['end'], 
                    strand=res['strand'], 
                    sequence=res['sequence'],
                    query=False
                ) 
                for res in results
            ]
        else:
            return []


    def get_summary(self):
        """
        Fills attribute values that are not mandatory, with a summary of several
        features of the node. Fills attributes "length" and "orflength".
        """
        self.length    = len(self.sequence)
        self.orflength = len(self.orf)


    def __query_node(self):
        """
        Gets node from neo4j and fills sequence, orf, length and homology attributes.

        Raises:
            NodeNotFound: If node is not in database.
        """
        query = neoquery.PREDNODE_QUERY % (self.database, self.symbol)

        results = GRAPH.run(query)
        results = results.data()

        if results:
            for row in results:
                # Add node
                self.symbol         = row["symbol"]
                self.sequence       = row['sequence']
                self.orf            = row["orf"]
                self.length         = row['length']

                # Add homolog
                human_node = HumanNode(row['human'], "Human", query=False)
                self.homolog = Homology(
                    prednode   = self,
                    human      = human_node,
                    blast_cov  = row['blast_cov'],
                    blast_eval = row['blast_eval'],
                    nog_brh    = row['nog_brh'],
                    pfam_sc    = row['pfam_sc'],
                    nog_eval   = row['nog_eval'],
                    blast_brh  = row['blast_brh'],
                    pfam_brh   = row['pfam_brh']
                )
        else:
            logging.info("NOTFOUND")
            # Maybe node does not have an homolog
            query = neoquery.PREDNODE_NOHOMOLOG_QUERY % (self.database, self.symbol)
            results = GRAPH.run(query)
            results = results.data()

            if results:
                self.symbol = results[0]['symbol']
                self.sequence = results[0]['sequence']
                self.orf = results[0]['orf']
                self.length = results[0]['length']
                self.homolog = None
            else:
                raise exceptions.NodeNotFound(self.symbol, self.database)

    def get_all_information(self):
        """
        Fills all attributes of PlanarianContig by querying the database
        """
        self.__query_node()

    def get_homolog(self):
        """
        Tries to get the homologous human gene of this planarian transcript
        """
        self.__query_node()

    def to_jsondict(self):
        """
        This function takes a node object and returns a dictionary with the necessary
        structure to convert it to json and be read by cytoscape.js

        Returns:
            `dict`: Dictionary with serialized PlanarianContig.

                .. code-block:: python

                        {
                            'data': 
                                {
                                    'id': 'contig id',
                                    'name': 'contig name',
                                    'database': 'contig database',
                                    'homolog': 'human homolog symbol',
                                    'degree': int,
                                    'colorNode': '#404040',
                                },
                            'classes': 'null or important'
                            
                        } 
                        
        """
        element                     = {}
        element['data']             = {}
        element['data']['id']       = self.symbol
        element['data']['name']     = self.symbol
        element['data']['database'] = self.database
        if self.homolog is not None:
            element['data']['homolog']  = self.homolog.human.symbol
        if self.degree is not None:
            element['data']['degree']   = self.degree
        if self.important:
            element['data']['colorNODE'] = "#404040"
            element['classes'] = 'important'
        else:
            element['data']['colorNODE'] = "#404040"
        return element

    def get_neighbours_shallow(self):
        """
        Method to get adjacent nodes (and their degree) in the graph without 
        homology information and only with path_length and probability for the interaction information.
        It also retrieves the degree of the neighbour nodes.
        Fills attribute neighbours, which will be a list of PredInteraction objects.
        Used by NetExplorer add_connection/expand
        """
        query = neoquery.NEIGHBOURS_QUERY_SHALLOW % (self.database, self.database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                parameters = {}
                # Homology object
                human_node = HumanNode(row['human'], "Human", query=False)
                thomolog  = Homology(human = human_node)
                # Node Object
                target = PlanarianContig(
                    symbol   = row['target'],    database = self.database,
                    homolog  = thomolog,         degree = row['tdegree'],
                    query=False
                )

                # Add prednode to homology object
                target.homolog.prednode = target

                # Interaction Object
                interaction = PredInteraction(
                    source_symbol = self.symbol,
                    target        = target,
                    database      = self.database,
                    query         = False,
                    parameters    = { 
                        'path_length': int(row['path_length']), 
                        'int_prob': round(float(row['int_prob']), 3)
                    } 
                )
                # Add interaction to list of neighbours
                self.neighbours.append(interaction)
        else:
            self.neighbours = None
            self.degree     = 0
        return self.neighbours

    def path_to_node(self, target, plen):
        """
        Given a target node object, this method finds all the shortest paths to 
        that node of length plen. If there aren't any, it returns None.
        
        Args:
            target (PlanarianContig): Target gene in the graph.
            plen (int): Path length to consider. All paths from `self` to `target
                will be of length = `plen`.

        Returns:
            Union([Pathway, None]): Pathway between `self` and `target` or None 
            if no pathway exists. 
        """
        query = neoquery.PATH_QUERY % (self.database, plen, target.database, self.symbol, target.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            paths = []
            for path in results:
                nodes_in_path  = [ PlanarianContig(node, self.database, query=False) for node in path['symbols']]
                relationships  = []
                path_graph_obj = GraphCytoscape()
                for idx, val in enumerate(path['int_prob']):
                    parameters = {}
                    parameters['int_prob']    = path['int_prob'][idx]
                    parameters['path_length'] = path['path_length'][idx]
                    relationships.append(
                        PredInteraction(
                            database      = self.database,
                            source_symbol = path['symbols'][idx],
                            target        = nodes_in_path[idx + 1],
                            parameters    = parameters
                        )
                    )
                path_graph_obj.add_elements(nodes_in_path)
                path_graph_obj.add_elements(relationships)
                paths.append(Pathway(graph=path_graph_obj))
            return paths
        else:
            # No results
            logging.info("No paths")
            return None

    def get_neighbours(self):
        """
        Method to get the adjacent nodes in the graph and all the information about 
        those connections (including the homology information, etc.).
        Fills attribute neighbours, which will be a list of PredInteraction objects.
        """
        query = neoquery.NEIGHBOURS_QUERY % (self.database, self.database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                parameters = {}
                # Initialize parameters to pass to the PredInteraction object
                parameters = {
                    'int_prob'    : round(float(row['int_prob']), 3),
                    'path_length' : int(row['path_length']),
                    'cellcom_nto' : round(float(row['cellcom_nto']), 3),
                    'molfun_nto'  : round(float(row['molfun_nto']), 3),
                    'bioproc_nto' : round(float(row['bioproc_nto']), 3),
                    'dom_int_sc'  : round(float(row['dom_int_sc']), 3)
                }
                # Homology object
                human_node = HumanNode(row['human'], "Human")
                thomolog  = Homology(
                    human      = human_node,        blast_cov = row['blast_cov'],
                    blast_eval = row['blast_eval'], nog_brh = row['nog_brh'],
                    pfam_sc    = row['pfam_sc'],    nog_eval   = row['nog_eval'],
                    blast_brh  = row['blast_brh'],  pfam_brh   = row['pfam_brh']
                )
                # Node Object
                target = PlanarianContig(
                    symbol   = row['target'],    database = self.database,
                    homolog  = thomolog,         query=False
                )

                # Add prednode to homology object
                target.homolog.prednode = target

                # Interaction Object
                interaction = PredInteraction(
                    source_symbol = self.symbol,
                    target        = target,
                    database      = self.database,
                    parameters    = parameters
                )
                # Add interaction to list of neighbours
                self.neighbours.append(interaction)
        else:
            self.neighbours = None
            self.degree     = 0

        if self.neighbours is not None:
            # Sort interactions by probability
            self.neighbours = sorted(self.neighbours, key=lambda k: k.parameters['int_prob'], reverse=True)
            self.degree     = int(len(self.neighbours))
        return self.neighbours

    def get_expression(self, experiment, sample):
        """
        Gets expression data for a particular node, a particular experiment and a particular sample
        """
        expression = None
        query = neoquery.EXPRESSION_QUERY % (self.database, self.symbol, experiment.id, sample)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                expression = row["exp"]
        else:
            raise exceptions.NoExpressionData(self.symbol, self.database, experiment.id, sample)
        return expression

    def get_graphelements(self, including=None):
        """
        Returns a list of nodes and edges adjacent to the node.
        """
        nodes = []
        edges = []
        added_elements = set()
        if not self.neighbours:
            self.get_neighbours()
        nodes.append(self)
        added_elements.add(self.symbol)
        if self.neighbours:
            for interaction in self.neighbours:
                if including and interaction.target.symbol not in including:
                    continue
                if interaction.target.symbol not in added_elements:
                    added_elements.add(interaction.target.symbol)
                    nodes.append( interaction.target )
                if (interaction.target.symbol, self.symbol) not in added_elements:
                    added_elements.add((self.symbol, interaction.target.symbol))
                    edges.append( interaction )
        return nodes, edges

    def get_geneontology(self):
        """
        Gets Gene Ontologies of the homologous human protein.
        """
        if self.homolog is None:
            self.__query_node()
        
        if self.homolog is not None:
            
            query = neoquery.GO_HUMAN_GET_GO_QUERY % self.homolog.human.symbol
            results = GRAPH.run(query)
            if results:
                for row in results:
                    self.gene_ontologies.append(
                        GeneOntology(accession=row['accession'], domain=row['domain'], name=row['name'], query=False)
                    )
            else:
                self.gene_ontologies = []
        else:
            self.gene_ontologies = []

    def __hash__(self):
        return hash((self.symbol, self.database, self.important))

    def __eq__(self, other):
        return (self.symbol, self.database, self.important) == (other.symbol, other.database, other.important)

    def __str__(self):
        return "%s:%s" % (self.database, self.symbol)

# ------------------------------------------------------------------------------
class oldExperiment(object):
    """
    Legacy class for gene expresssion experiments. Mantained until PlanExp is published.

    Attributes:
        id (str): Experiment identifier.
        url (str): Experiment publication URL.
        reference (str): Formatted publication reference.
        minexp (float): Minimum expression value in whole experiment.
        maxexp (float): Maximum expression value in whole experiment.
        percentiles (`list` of `int`): List of floats indicating the expression value 
            at each percentile (15 in total). 
    
    Args:
        id (str): Experiment identifier.
        url (str, optional): Experiment publication URL. If not passed on creation,
            will query the database to get the data for this experiment.
        reference (str, optional): Formatted publication reference.
    """
    def __init__(self, identifier, url=None, reference=None):
        self.id        = identifier
        self.url         = url
        self.reference   = reference
        self.minexp      = None
        self.maxexp      = None
        self.percentiles = None
        self.gradient    = None
        if self.url is None:
            self.__get_minmax()

    def __get_minmax(self):
        """
        Checks if the specified experiment exists in the database and gets the 
        max, min expression ranges and the reference defined.
        """
        query   = neoquery.EXPERIMENT_QUERY % (self.id)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.maxexp      = results[0]["maxexp"]
            self.minexp      = results[0]["minexp"]
            self.reference   = results[0]["reference"]
            self.url         = results[0]["url"]
            self.percentiles = results[0]["percentiles"]

    def to_json(self):
        """
        Returns a json string with the info about the experiment.

        Returns:
            str: JSON string with the following structure.

                .. code-block:: python

                    {
                        'data': 
                            {
                                'id': 'experiment identifier',
                                'url': 'url of experiment' ,
                                'reference': 'formatted reference',
                                'minexp': float,
                                'maxexp': float,
                                'percentiles': [ float, float, float, ...]

                            }
                    }

        """
        json_dict = {}
        json_dict['id']        = self.id
        json_dict['reference'] = self.reference
        json_dict['url']       = self.url
        json_dict['minexp']    = self.minexp
        json_dict['maxexp']    = self.maxexp
        json_dict['gradient']  = {}
        for tup in self.gradient:
            json_dict['gradient'][tup[0]] = tup[1]
        return json.dumps(json_dict)

    def color_gradient(self, from_color, to_color, comp_type):
        """
        This method returns a color gradient of length bins from "from_color" to "to_color".

        Args:
            from_color (str): Hex value of initial color for gradient.
            to_color (str): Hex value of final color for gradient.
            comp_time (str): "one-sample" or "two-sample", indicating if gradient 
                should be linear ("one-sample") or divergent "two-sample".
        """
        bins         = []
        exp_to_color = []
        range_colors = []
        s_color = Color(from_color)
        e_color = Color(to_color)
        if comp_type == "one-sample":
            # We assign a color to each percentile
            bins = self.percentiles
            range_colors = list(s_color.range_to(e_color, len(bins)))
            range_colors.reverse()
        else:
            # We assign a color to each number from -10 to +10
            white_starting = Color(from_color)
            white_ending   = Color(to_color)
            white_starting.saturation = 0.1
            white_starting.luminance  = 0.9
            white_ending.saturation = 0.1
            white_ending.luminance  = 0.9
            bins = range(-10,+11)
            half_colors = int(math.ceil(len(bins) / 2.0))
            range_colors.extend(list(s_color.range_to(white_starting, half_colors))[1:half_colors])
            range_colors.append(Color("white"))
            range_colors.extend(list(white_ending.range_to(e_color, half_colors))[1:half_colors])
            range_colors.reverse()
        for i in bins:
            exp_to_color.append((i,  range_colors.pop().get_hex()))
        self.gradient = exp_to_color
        return self


# ------------------------------------------------------------------------------
class GraphCytoscape(object):
    """
    Class for a graph object. Holds nodes and edges of any type as long as they have 
    a common interface (symbol attribute and to_jsondict() method).

    Attributes:
        nodes (set): Set of :obj:`Node` objects.
        edges (set): Set of :obj:`PredInteraction` objects.
    """
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def add_elements(self, elements):
        """
        Method that takes a list of node or PredInteraction objects and adds them
        to the graph.

        Args:
            elements (`list` of :obj:`PredInteraction` or :obj:`Node`): List of 
                :obj:`PredInteraction` objects or :obj:`Node` objects to add to the graph.
        
        Raises:
            ValueError: If any element in `elements` is not a :obj:`Node` or a :obj:`PredInteraction`. 
        """
        for element in elements:
            if isinstance(element, Node):
                self.nodes.add( element )
            elif isinstance(element, PredInteraction):
                self.edges.add( element )
            else:
                raise ValueError("Should provide only Node or PredInteraction instances.")

    def is_empty(self):
        """
        Checks if the graph is empty or not.

        Returns:
            bool: True if empty (no nodes or edges), False otherwise.
        """
        if not self.nodes and not self.edges:
            return True
        else:
            return False

    def add_node(self, node):
        """
        Adds a single node to the graph.

        Args:
            node (:obj:`Node`): Node instance to add to the graph.
        """
        self.add_elements([node])
    
    def add_interaction(self, interaction):
        """
        Adds a single interaction to the graph.

        Args:
            node (:obj:`PredInteraction`): PredInteraction instance to add to the graph.
        """
        self.add_elements([interaction])

    def add_graph(self, graph):
        """
        Adds elements of graph to this graph instance.

        Args:
            graph (:obj:`GraphCytoscape`): Graph to be merged.
        """
        if graph.nodes:
            self.add_elements(graph.nodes)
        if graph.edges:
            self.add_elements(graph.edges)
        return self

    def define_important(self, vip_nodes):
        """
        Gets a list/set of nodes and defines them as important.

        Args:
            vip_nodes (`list`): List of :obj:`Node` instances.
        """
        for node in self.nodes:
            if node.symbol in vip_nodes:
                node.important = True
        return self

    def to_json(self):
        """
        Converts the graph to a json string to add it to cytoscape.js.

        Returns:
            str: JSON string with data for this graph for cytoscape.js. 
                Follows the structure (example):

                 .. code-block:: python

                    {
                        "nodes": 
                            [
                                {
                                    "data": 
                                        {
                                            "id": "dd_Smed_v6_11363_0_1", 
                                            "name": "dd_Smed_v6_11363_0_1", 
                                            "database": "Dresden",
                                            "homolog": "LIG4",
                                            "degree": 27,
                                            "colorNODE": "#404040"
                                        }
                                    },
                                {
                                    "data": 
                                        {
                                            "id": "dd_Smed_v6_9219_0_1",
                                            "name": "dd_Smed_v6_9219_0_1", 
                                            "database": "Dresden", 
                                            "homolog": "FAM214A", 
                                            "colorNODE": "#404040"
                                        }, 
                                        "classes": "important"
                                    }, 
                                }
                            ],
                        "edges": 
                            [
                                {
                                    "data": {
                                        "id": "dd_Smed_v6_11363_0_1-dd_Smed_v6_9219_0_1", 
                                        "source": "dd_Smed_v6_9219_0_1", 
                                        "target": "dd_Smed_v6_11363_0_1", 
                                        "pathlength": 1, 
                                        "probability": 0.67, 
                                        "colorEDGE": "#72a555"
                                    }
                                },
                            ]
                    }

        """
        graphelements = {
            'nodes': [node.to_jsondict() for node in self.nodes],
            'edges': [edge.to_jsondict() for edge in self.edges]
        }
        graphelements = json.dumps(graphelements)
        return graphelements

    def filter(self, including):
        """
        Filters nodes and edges from the graph.

        Args:
            including (set): Set of `Node` instances that has to be kept. Only 
                interactions where both nodes are in `including` will be kept.
        """
        nodes_to_keep = []
        edges_to_keep = []
        for node in self.nodes:
            if node.symbol in including:
                nodes_to_keep.append(node)
            else:
                continue
        for edge in self.edges:
            if edge.source_symbol in including and edge.target.symbol in including:
                edges_to_keep.append(edge)
            else:
                continue
        self.nodes = nodes_to_keep
        self.edges = edges_to_keep
        return self

    def get_expression(self, experiment, samples):
        """
        Gets the expression for all the node objects in the graph.
        Returns a dictionary: expression_data[node.symbol][sample]

        Args:
            experiment (str): :obj:`oldExperiment instance.
            samples (list): List of samples for which to get expression.

        Returns:
            `dict` of `dict`: Dictionary with expression data.
                Primary key is node symbol, secondary key is sample name and value 
                is expression value (float).
        """
        node_list     = ",".join(map(lambda x: '"' + x + '"', [node.symbol for node in self.nodes ]))
        node_selector = "[" + node_list + "]"
        expression    = {}
        for sample in samples:
            query = neoquery.EXPRESSION_QUERY_GRAPH % (node_selector, experiment.id, sample)
            results = GRAPH.run(query)
            results = results.data()
            for row in results:
                if row['symbol'] not in expression:
                    expression[row['symbol']] = {}
                expression[row['symbol']][sample] = row['exp']
        return expression

    def get_connections(self):
        """
        Function that looks for the edges between the nodes in the graph and 
        adds them to the attribute `edges`.
        """
        node_q_string = str(list([str(node.symbol) for node in self.nodes]))
        query = neoquery.GET_CONNECTIONS_QUERY % (node_q_string, node_q_string)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            for row in results:
                parameters = {}
                parameters = {
                    'int_prob'    : round(float(row['int_prob']), 3),
                    'path_length' : round(float(row['path_length']), 3),
                    'cellcom_nto' : round(float(row['cellcom_nto']), 3),
                    'molfun_nto'  : round(float(row['molfun_nto']), 3),
                    'bioproc_nto' : round(float(row['bioproc_nto']), 3),
                    'dom_int_sc'  : round(float(row['dom_int_sc']), 3)
                }
                database = [ database for database in row['database'] if database != "PlanarianContig" ][0]
                newinteraction = PredInteraction(
                    database      = database,
                    source_symbol = row['nsymbol'],
                    target        = PlanarianContig(row['msymbol'], database, query=False),
                    parameters    = parameters
                )
                self.add_interaction(newinteraction)
        return self

    def new_nodes(self, symbols, database):
        """
        Takes a list of symbols and returns the necessary GraphCytoscape with Human or PlanarianContig objects

        Args:
            symbols (`list` of `str`): List of strings with gene/contig/pfam/go/kegg symbols.
            database (str): String with database.
        """
        symbols = [ symbol for symbol in symbols if symbol.strip() ]
        for symbol in symbols:
            symbol = symbol.replace(" ", "")
            symbol = symbol.replace("'", "")
            symbol = symbol.replace('"', '')
            node_objects = []
            try:
                gene_search = GeneSearch(symbol, database)
                if database == "Human":
                    node_objects = gene_search.get_human_genes()
                elif database == "Smesgene":
                    node_objects = gene_search.get_planarian_genes()
                elif database == "ALL":
                    node_objects = gene_search.quick_search()
                else:
                    node_objects = gene_search.get_planarian_contigs()
                self.add_elements(node_objects)
            except exceptions.NodeNotFound:
                logging.info("Node not found: {} - {}".format(symbol, database))
                continue
    
    @classmethod
    def get_homologs_bulk(cls, symbols, database):
        """
        Returns a dictionary of homologous genes to the specified
        list of planarian contig symbols from database.

        Args:
            symbols (`list` of `str`): List of node symbols.
            database (`str`): Database string.

        Returns:
            `dict`: Dictionary with homology information. 
                Key is planarian contig symbol, value is human gene symbol.
        """
        if database != "Smesgene":
            query = neoquery.GET_HOMOLOGS_BULK % (database, symbols)
        else:
            query = neoquery.GET_HOMOLOGS_BULK_FROM_GENE % (PlanarianGene.preferred_database, symbols)
        results = GRAPH.run(query)
        results = results.data()
        homologs = {}
        if results:
            for row in results:
                homologs[row['planarian']] = row['human']
        return homologs

    
    
    @classmethod
    def get_genes_bulk(cls, symbols, database):
        """
        Returns a dictionary of planarian genes to the specified
        list of planarian contig symbols from database.

        Args:
            symbols (`list` of `str`): List of node symbols.
            database (`str`): Database string.

        Returns:
            `dict` of `dict`: Dictionary with contig-gene mapping. 
                Primary key is planarian contig symbol, secondary key is either 
                'gene' or 'name', value is gene symbol or gene name respectively.

        """
        if database != "Smesgene":
            query = neoquery.GET_GENES_BULK % (database, symbols)
        else:
            query = neoquery.GET_GENES_BULK_FROM_GENES % (symbols)
        results = GRAPH.run(query)
        results = results.data()
        genes = {}
        if results:
            for row in results:
                genes[row['contig']] = {}
                genes[row['contig']]['gene'] = row['gene']
                genes[row['contig']]['name'] = row['name']
        return genes

    def __str__(self):
        return self.to_json()

    def __bool__(self):
        if self.nodes:
            return True
        else:
            return False
    __nonzero__=__bool__

# ------------------------------------------------------------------------------
class ExperimentList(object):
    """
    Maps a list of experiment objects with all its available samples in the DB.

    Attributes:
        experiments (`set` of `oldExperiment`): Set of oldExperiment instances.
        samples (`dict`): Experiments to sample names mapping. Key is experiment 
            identifier, value is set of sample names (`str`).
        datasets (`dict`): Dictionary with list of datasets for which experiment 
            has data for.

    Args:
        user (`models.user`): User that requests the ExperimentList.


    """
    def __init__(self, user):
        self.experiments = set()
        self.samples     = {}
        self.datasets    = {}
        query   = neoquery.ALL_EXPERIMENTS_QUERY
        # Add all the samples for each experiment
        results = GRAPH.run(query)
        results = results.data()
        added_experiments = set()

        # Check if user is authenticated to get private experiments
        access_to = set()
        if user.is_authenticated:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT auth_user.username, user_exp_permissions.experiment
                    FROM auth_user
                    INNER JOIN user_exp_permissions ON auth_user.id=user_exp_permissions.user_id
                    WHERE auth_user.username = %s;
                """, [user.username])
                rows = cursor.fetchall()
                access_to.update([row[1] for row in rows])
            except Exception:
                pass

        if results:
            for row in results:
                if row['identifier'] not in self.samples:
                    self.samples[ row['identifier'] ] = set()
                self.samples[ row['identifier'] ].update(row['samples'])
                if row['identifier'] not in added_experiments:
                    if row['private'] == 1:
                        if row['identifier'] not in access_to:
                            continue
                    self.experiments.add(oldExperiment( row['identifier'], url=row['url'], reference=row['reference'] ))
                    added_experiments.add(row['identifier'])
                if row['identifier'] not in self.datasets:
                    self.datasets[ row['identifier'] ] = set()
                for item in row['datasets']:
                    item = [ it for it in item if it != "PlanarianContig" ]
                    self.datasets[ row['identifier'] ].update(item)
            for exp in self.samples:
                self.samples[exp] = sorted(self.samples[exp])
            # Sort datasets alphabetically
            for exp in self.datasets:
                self.datasets[exp] = sorted(list(self.datasets[exp]))

    def get_samples(self, experiment):
        """ 
        Returns a set for the given experiment.

        Args:
            experiment (str): Experiment name.
        
        Returns:
            set: Samples for which experiment has expression data for.
        
        Raises:
            ExperimentNotFound: If experiment is not in ExperimentList.

        """
        if experiment in self.samples:
            return self.samples[experiment]
        else:
            raise exceptions.ExperimentNotFound

    def get_datasets(self, experiment):
        """ 
        Returns a set for the given experiment
        
        Args:
            experiment (str): Experiment name.

        Returns:
            list: Dataset names for which experiment has data for.
        
        Raises:
            ExperimentNotFound: If experiment is not in ExperimentList.

        """
        if experiment in self.samples:
            return self.datasets[experiment]
        else:
            raise exceptions.ExperimentNotFound

    def __str__(self):
        final_str = ""
        for exp in self.experiments:
            final_str += "Experiment: %s\n\tsamples: %s\n\tdatasets: %s\n" % (exp, ",".join(self.samples[exp]), ",".join(self.datasets[exp]))
        return final_str


# ------------------------------------------------------------------------------
class Pathway(GraphCytoscape):
    """
    Class for pathways. They are basically GraphCytoscape objects with score property.

    Attributes:
        graph (:obj:`GraphCytoscape): Graphcytoscape object of the pathway.

    Args:
        graph (:obj:`GraphCytoscape): Graphcytoscape object of the pathway.
     
    """
    def __init__(self, graph):
        super(Pathway, self).__init__()
        self.add_graph(graph)

    @property
    def score(self):
        """
        float: Mean score of interactions in pathway.
        """
        computed_score = 0
        if self.edges:
            computed_score = sum(
                [edge.parameters['int_prob'] for edge in self.edges ]
            ) / len(self.edges)
        return computed_score



# ------------------------------------------------------------------------------
class KeggPathway(GraphCytoscape):
    """
    Class for KeggPathways. Encapsulates a GraphCytoscape object in `graphelements`. Will query Kegg on creation.

    Attributes:
        symbol (str): Symbol for Kegg Pathway.
        database (str): Planarian database to which this KeggPathway will be mapped to.
        kegg_url (str): Url to the pathway in Kegg.
        graphelements (:obj:`GraphCytoscape`): GraphCytoscape object that results from 
            looking at the genes and interactions in the Pathway that appear in the 
            neo4j database.
        
    Args:
        symbol (str): Symbol for Kegg Pathway.
        database (str): Planarian database to which this KeggPathway will be mapped to.
    """
    def __init__(self, symbol, database):
        super(KeggPathway, self).__init__()
        self.symbol = symbol
        self.database = database
        self.kegg_url = "http://togows.dbcls.jp/entry/pathway/%s/genes.json" % symbol
        self.add_graph(self.get_graph_from_kegg())

    def get_graph_from_kegg(self):
        """
        Connects to KEGG and extracts the elements of the pathway.

        Returns:
            :obj:`GraphCytoscape`: GraphCytoscape object that results from 
                looking at the genes and interactions in the Pathway that appear in the 
                neo4j database. If Kegg can't be reached or the pathway does not have 
                any equivalent in PlanNET, the :obj:`GraphCytoscape` will be empty.

        """
        r = requests.get(self.kegg_url)
        if r.status_code == 200:
            if r.json():
                gene_list = [gene.split(";")[0] for gene in r.json()[0].values()]
                graphelements = GraphCytoscape()
                graphelements.new_nodes(gene_list, self.database)
                graphelements.get_connections()
                return graphelements
            else:
                return GraphCytoscape()
        else:
            return GraphCytoscape()
                
# ------------------------------------------------------------------------------
class GeneOntology(object):
    """
    Class for GeneOntology nodes.

    Attributes:
        accession (str): GO accession, of the form "GO:...".
        domain (str): GO domain ("molecular function", "cellular component", "biological process").
        name (str): GO name.
        human_nodes (`list` of :obj:`HumanNode`): List of HumanNode instances that 
            have this GO annotated.

    Args:
        accession (str): GO accession, of the form "GO:...".
        domain (str, optional): GO domain ("molecular function", "cellular component", "biological process"). Defaults to None
        name (str, optional): GO name. Defaults to None
        human (`list` of :obj:`HumanNode`, optional): List of HumanNode instances that 
            have this GO annotated. Defaults to False
        query (bool, optional): Flag to query database on creation to retrieve 
            all attributes.

    """
    go_regexp = r"GO:\d{7}"

    def __init__(self, accession, domain=None, name=None, human=False, query=True):
        self.accession = accession
        self.domain = domain
        self.name = name
        self.human_nodes = []
        if query:
            if GeneOntology.is_symbol_valid(self.accession):
                if human:
                    self.get_human_genes()
                else:
                    self.__query_go()
            else:
                raise exceptions.NotGOAccession(self)

    @classmethod
    def is_symbol_valid(cls, symbol):
        """
        Checks if provided symbol is a valid GO accession.

        Args:
            symbol (str): Symbol to check if it's a valid GO accession.
        
        Returns:
            bool: True if valid, false otherwise.
        """
        return re.match(cls.go_regexp, symbol)

    def __query_go(self):
        """
        Query DB and get domain.

        Raises:
            NodeNotFound: If GO does not exist in database.
        """
        query   = neoquery.GO_QUERY % self.accession
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.domain = results[0]['domain']
            self.name   = results[0]['name']
        else:
            raise exceptions.NodeNotFound(self.accession, "Go")

    def get_human_genes(self):
        """
        Gets Human nodes symbols with annotated GO. Fills human_nodes attribute.

        Raises:
            NodeNotFound: If GO does not exist in database.
        """
        query   = neoquery.GO_HUMAN_NODE_QUERY % self.accession
        results = GRAPH.run(query)

        results = results.data()
        if results:
            self.domain = results[0]['domain']
            for row in results:
                self.human_nodes.append(HumanNode(row['symbol'], "Human", query=False))
        else:
            raise exceptions.NodeNotFound(self.accession, "Go")
        return self.human_nodes

    def get_planarian_contigs(self, database):
        """
        Gets planarian contigs whose homolog has the GO annotated. (GO)<-(Human)<-(Contig)

        Args:
            database (str): Database string from which to retrieve the PlanarianContigs.

        Returns:
            list: List of :obj:`PlanarianContig` objects.
        """
        query = neoquery.GO_TO_CONTIG % (database, self.accession)
        results = GRAPH.run(query)
        results = results.data()
        contigs = []
        if results:
            for data in results:
                contig = PlanarianContig(
                    data['symbol'], 
                    database, 
                    query=False)
                contig.homolog = Homology(
                    prednode   = contig,
                    human      = HumanNode(data['human'], "Human", query=False),
                    blast_cov  = data['blast_cov'],
                    blast_eval = data['blast_eval'],
                    nog_brh    = data['nog_brh'],
                    pfam_sc    = data['pfam_sc'],
                    nog_eval   = data['nog_eval'],
                    blast_brh  = data['blast_brh'],
                    pfam_brh   = data['pfam_brh']
                )
                contigs.append(contig)
        return contigs


# ------------------------------------------------------------------------------
class Document(models.Model):
    """
    Class for Documents uploaded to the server.
    """
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


# ------------------------------------------------------------------------------
class GeneSearch(object):
    """
    Class for node/gene searches

    Attributes:
        sterm (str): Term to search.
        database (str): Database to search for sterm.
        sterm_database (str): Database to which sterm belongs to.

    Args:
        sterm (str): Term to search.
        database (str): Database to search for sterm.

    """
    def __init__(self, sterm, database):
        self.sterm = sterm
        self.database = database
        self.sterm_database = None
    
    def infer_symbol_database(self):
        """
        Guesses to which database `sterm` belongs to. Compares the symbol in 
        `sterm` to the valid patterns for each NodeType. Saves result in `sterm_database`.
        """
        datasets = Dataset.objects.all()
        for dataset in datasets:
            if dataset.is_symbol_valid(self.sterm):
                self.sterm_database = dataset.name
        if self.sterm_database is None:
            # Not valid for any database.
            # Check Smesgene, PFAM, GO, Human in that order.
            if PlanarianGene.is_symbol_valid(self.sterm):
                self.sterm_database = "Smesgene"
            elif Domain.is_symbol_valid(self.sterm):
                self.sterm_database = "PFAM"
            elif GeneOntology.is_symbol_valid(self.sterm):
                self.sterm_database = "GO"
            else:
                self.sterm_database = "Human"
        return self
    
    def get_planarian_contigs(self):
        """
        Returns PlanarianContig objects that match sterm independently of the search term used.

        Returns:
            `list` of :obj:`PlanarianContig`: List of :obj:`PlanarianContig` instances. 
                PlanarianContigs retrieved from `sterm`. It is able to work with sterm of the type: 
                'Smesgene', 'PFAM', 'GO', 'Human', 'PlanarianContig'.

        """
        if self.sterm_database is None:
            self.infer_symbol_database()

        planarian_contigs = []
        source_nodes = []
        if self.sterm_database == "Smesgene":
            source_nodes.append(PlanarianGene(self.sterm, self.sterm_database))
        elif self.sterm_database == "PFAM":
            source_nodes.append(Domain(self.sterm))
        elif self.sterm_database == "GO":
            source_nodes.append(GeneOntology(self.sterm))
        elif self.sterm_database == "Human" :
            if "*" in self.sterm:
                source_nodes = WildCard(self.sterm, self.sterm_database).get_human_genes()
            else:
                source_nodes = self._get_human_or_pfam()
            try:
                source_nodes.extend(PlanarianGene.from_gene_name(self.sterm))
            except exceptions.NodeNotFound:
                pass

        else:
            # We already have the planarian contig by identifier,
            # no need to try to retrieve it from neo4j connections.
            planarian_contigs =  [ PlanarianContig(self.sterm, self.sterm_database) ]
            return planarian_contigs

        for snode in source_nodes:
            planarian_contigs.extend(snode.get_planarian_contigs(self.database))

        for pcontig in planarian_contigs:
            if not pcontig.homolog:
                pcontig.get_homolog()
            if not pcontig.name:
                pcontig.get_gene_name()
        return planarian_contigs

    def get_planarian_genes(self):
        """
        Returns PlanarianGene objects that match sterm independently of the search term used.

        Returns:
            `list` of :obj:`PlanarianGene`: List of :obj:`PlanarianGene` instances. 
                PlanarianGene retrieved from `sterm`. It is able to work with sterm of the type: 
                'Smesgene', 'PFAM', 'GO', 'Human', 'PlanarianContig'.
        """
        if self.sterm_database is None:
            self.infer_symbol_database()
        planarian_genes = []
        if self.sterm_database == "Human":
            if "*" in self.sterm:
                human_nodes = WildCard(self.sterm, self.sterm_database).get_human_genes()
            else:
                human_nodes = self._get_human_or_pfam()
            for hnode in human_nodes:
                planarian_genes.extend(hnode.get_planarian_genes(PlanarianGene.preferred_database))
            
            try:
                planarian_genes.extend(PlanarianGene.from_gene_name(self.sterm))
            except exceptions.NodeNotFound:
                pass
            
        elif self.sterm_database == "PFAM":
            planarian_nodes = Domain(self.sterm).get_planarian_contigs(PlanarianGene.preferred_database)
            for contig in planarian_nodes:
                planarian_genes.extend(contig.get_genes())
        elif self.sterm_database == "Smesgene":
            planarian_genes.append(PlanarianGene(self.sterm, self.sterm_database))
        elif self.sterm_database == "GO":
            planarian_nodes = GeneOntology(self.sterm).get_planarian_contigs(PlanarianGene.preferred_database)
            for contig in planarian_nodes:
                planarian_genes.extend(contig.get_genes())
        else:
            # Transcriptome database
            planarian_node = PlanarianContig(self.sterm, self.sterm_database)
            planarian_genes.extend(planarian_node.get_genes())

        for pgene in planarian_genes:
            if not pgene.homolog:
                pgene.get_homolog()
        planarian_genes = list(set(planarian_genes)) # Unique genes only 
        return planarian_genes

    def get_human_genes(self):
        """
        Returns HumanNode objects independently of the search term used.

        Returns:
            `list` of :obj:`HumanNode`: List of :obj:`HumanNode` instances. 
                HumanNode retrieved from `sterm`. It is able to work with sterm of the type: 
                'Human', 'GO'.

        """
        if self.sterm_database is None:
            self.infer_symbol_database()

        human_nodes = []
        if self.sterm_database == "Human":
            if "*" in self.sterm:
                human_nodes = WildCard(self.sterm, self.sterm_database).get_human_genes()
            else:
                human_nodes = [ HumanNode(self.sterm.upper(), self.sterm_database) ]
        elif self.sterm_database == "GO":
            human_nodes = GeneOntology(self.sterm, human=True).human_nodes
        elif self.sterm_database not in set(["PFAM", "Smesgene"]):
            planarian_contig = PlanarianContig(self.sterm, self.sterm_database)
            planarian_contig.get_homolog()
            human_nodes = [ planarian_contig.homolog.human ]
        return human_nodes

    def quick_search(self):
        """
        Retrieves given search term in all databases: PlanarianGene + PlanarianContigs

        Returns:
            `list` of `Node`: List of `Node` of the type :obj:`PlanarianGene` or :obj:`PlanarianContig`.
        """
        all_results = []

        self.infer_symbol_database()

        # Get Planarian Genes
        self.database = "Smesgene"
        all_results.extend(self.get_planarian_genes())


        if self.sterm_database not in set(["Human", "PFAM", "Smesgene", "GO"]):
            # Get only from ONE database (the one the search term belongs to)
            self.database = self.sterm_database
            all_results.append(PlanarianContig(self.sterm, self.sterm_database))
        else:
            # Get from ALL databases.
            datasets = Dataset.objects.all()
            for dataset in datasets:
                try:
                    self.database = dataset.name
                    contigs = self.get_planarian_contigs()
                    if contigs:
                        all_results.extend(contigs)
                except exceptions.NodeNotFound:
                    continue
            self.database = "ALL"
        return all_results

    def _get_human_or_pfam(self):
        """
        Returns a list of HumanNodes or a PFAM nodes (or both) by searching 
        by gene/domain symbol.

        Returns:
            `list` of `Node`: List of `Node` of type :obj:`HumanNode` and/or :obj:`Domain`.
        """
        matching_nodes = []

        try:
            # Human Gene
            human_gene = HumanNode(self.sterm.upper(), self.sterm_database)
            matching_nodes.append(human_gene)
        except exceptions.NodeNotFound:
            pass
        
        try:
            domain = Domain(identifier=self.sterm)
            matching_nodes.append(domain)
        except exceptions.NodeNotFound:
            pass
        return matching_nodes

class PlanarianGene(Node):
    """
    Class for PlanarianGenes (genes from Planmine 3.0 gene annotation)

    Attributes:
        symbol (str): Gene symbol (SMESG...).
        database (str): 'Smesgene'.
        name (str): Gene name (if any).
        start (int): Start coordinate in chromosome.
        end (int): End coordinate in chromosome.
        strand (int): Strand in chromosome (+1: Forward , -1: Reverse)
        sequence (str): Nucleotide sequence of gene.
        homolog (:obj:`HumanNode`): Homologous gene.
        chromosome (str): Chromosome name where gene is located.
        transcription_factors (list of :obj:`TfAnnotation`).
    
    Args:
        symbol (str): Gene symbol (SMESG...).
        database (str): 'Smesgene'.
        name (str, optional): Gene name (if any). Defaults to None.
        start (int): Start coordinate in chromosome. Defaults to None.
        end (int, optional): End coordinate in chromosome. Defaults to None.
        strand (int, optional): Strand in chromosome (+1: Forward , -1: Reverse). Defaults to None.
        sequence (str, optional): Nucleotide sequence of gene. Defaults to None.
        homolog (:obj:`HumanNode`, optional): Homologous gene. Defaults to None.
        chromosome (str, optional): Chromosome name where gene is located. Defaults to None.
        query (bool, optional): Flag to decide if gene should be queried on creation.
            Defaults to False.
    """
    smesgene_regexp = r'SMESG\d+'
    preferred_database = "Smest"
    allowed_databases = set(["Smesgene"])

    def __init__(self, symbol, database, 
                 name=None, start=None, end=None, 
                 strand=None, sequence=None, homolog=None, 
                 chromosome=None, query=True):
        super(PlanarianGene, self).__init__(symbol, database)
        self.name = name
        self.start = start
        self.end = end
        self.strand = strand
        self.sequence = sequence
        self.chromosome = chromosome
        self.homolog = homolog
        self.promoter_motifs = []
        self.enhancer_motifs = []

        if sequence is None and query:
            self.__query_node()
            self.get_homolog()

    @classmethod
    def is_symbol_valid(cls, symbol):
        """
        Checks if symbol is valid

        Args:
            symbol (str): Symbol to check if follows PlanarianGene naming convention.
        
        Returns:
            bool: True if symbol is a valid gene identifier. False otherwise.
        """
        return re.match(cls.smesgene_regexp, symbol.upper())

    @classmethod
    def from_gene_name(cls, name):
        """
        Returns a PlanarianGene by looking for gene name instead of identifier.

        Args:
            name (str): Planarian gene name (e.g.: WNT1)
        
        Returns:
            PlanarianGene object.

        Raises:
            NodeNotFound when planarian gene does not exist.
        """
        query = neoquery.SMESGENE_NAME_QUERY % (name.upper())
        results = GRAPH.run(query)
        results = results.data()
        planarian_genes = []
        if results:
            for result in results:
                planarian_gene = cls(
                    symbol=result['symbol'],
                    database="Smesgene",
                    name=result['name'],
                    sequence=result['sequence'],
                    chromosome=result['chromosome'],
                    strand=result['strand'],
                    start=result['start'],
                    end=result['end'],
                    query=False
                )
                planarian_genes.append(planarian_gene)
            return planarian_genes
        else:
            raise exceptions.NodeNotFound(name, "Smesgene")


    def __query_node(self):
        """
        Queries PlanarianGene to get and fill the attributes from the database.

        Raises:
            NodeNotFound: If gene is not in database.
        """
        query = neoquery.SMESGENE_QUERY % (self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.name = results[0]['name']
            self.sequence = results[0]['sequence']
            self.chromosome = results[0]['chromosome']
            self.strand = results[0]['strand']

            self.start = int(results[0]['start'])
            self.end = int(results[0]['end'])
            
            # Add 2000 nts for good visualization
            self.start -= 5000
            self.end += 5000
        else:
            raise exceptions.NodeNotFound(self.symbol, self.database)


    def get_homolog(self):
        """
        Gets homologous gene of longest transcript associated with this PlanarianGene.
        Fills attribute 'homolog'. Returns the HumanNode object.

        Returns:
            :obj:`HumanNode` or `None`: Homologous :obj:`HumanNode` if there is any, otherwise `None`.
        """
        best_transcript = self.get_best_transcript()
        if best_transcript:
            best_transcript.get_homolog()
            if best_transcript.homolog:
                self.homolog = best_transcript.homolog
            else:
                self.homolog = None
            return self.homolog
        else:
            return None


    def get_best_transcript(self):
        """
        Retrieves the longest transcript of preferred_database.

        Returns:
            :obj:`PlanarianContig`: PlanarianContig from preferred database annotated 
                as being transcribed from this gene.
        """
        best = None
        try:
            best = self.get_planarian_contigs(PlanarianGene.preferred_database)
        except Exception:
            pass
        if best:
            best = best[0]
        return best


    def get_planarian_contigs(self, database=None):
        """
        Returns list PlanarianContig objects of database or all databases that map to
        the PlanarianGene genomic location.
        
        Args:
            database (str, optional): Database from which to retrieve planarian contigs.
                if not defined will get planarian contigs from all databases.

        Returns:
            `list` of :obj:`PlanarianContig`: PlanarianContig objects associated with this
                gene.
        """
        if database is None:
            query = neoquery.SMESGENE_GET_ALL_CONTIGS_QUERY % (self.symbol)
        else:
            query = neoquery.SMESGENE_GET_CONTIGS_QUERY % (database, self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        prednodes = []
        if results:
            for contig in results:
                if 'database' in contig:
                    database = [ database for database in contig['database'] if database != "PlanarianContig"]
                    database = database[0]
                prednode = PlanarianContig(contig['symbol'], database, query=False)
                prednode.length = contig['length']
                prednodes.append(prednode)
        else:
            if database is None:
                database = "All"
        return prednodes

    def get_tf_motifs(self, element_type="promoter"):
        """
        Gets transcription factors associated with any of its transcripts.
        Fills attribute 'transcription_factors'.
        """
        

        query = neoquery.GET_MOTIFS % (self.symbol, element_type)
        results = GRAPH.run(query)
        results = results.data()

        if results:
            for row in results:
                motif_symbol = row['motif_symbol']
                motif_name = row['motif_name']
                motif_url = row['motif_url']
                motif_num = row['motif_num']
                tf_name = row['tf_name']
                domain = row['domain']
                motif_start = row['motif_start']
                motif_end = row['motif_end']
                motif_chromosome = row['motif_chromosome']
                motif_score = row['motif_score']
                motif_sequence = row['motif_sequence']
                
                motif = TfMotif(
                    symbol = motif_symbol,
                    database = "Tf_motif",
                    name=motif_name,
                    url=motif_url,
                    number=motif_num,
                    tf_name=tf_name,
                    domain=domain,
                    query=False
                )
                annotation = MotifAnnotation(
                    motif=motif,
                    start=motif_start,
                    end=motif_end,
                    chromosome=motif_chromosome,
                    score=motif_score,
                    sequence=motif_sequence,
                    distance=self.distance_to_motif(motif_start, motif_end)
                )

                if element_type == "promoter":
                    self.promoter_motifs.append(annotation)
                elif element_type == "enhancer":
                    self.enhancer_motifs.append(annotation)
                    print(self.enhancer_motifs)
                else:
                    raise ValueError("element_type must be 'promoter' or 'enhancer'!")
    
    def distance_to_motif(self, motif_start, motif_end):
        
        if self.strand == "1":
            seq_tss = self.start + 5000
        else:
            seq_tss = self.end - 5000
            
        if int(motif_end) < int(seq_tss):
            distance = int(motif_end) - int(seq_tss) + 1
        else:
            distance = int(motif_start) - int(seq_tss) + 1
        
        if self.strand == "1":
            return distance
        else:
            return -distance

    def __hash__(self):
        return hash((self.symbol))

    def __eq__(self, other):
        return self.symbol == other.symbol


class MotifAnnotation(object):
    """
    Class for Transcription factor annotation. It contains the information of a 
    particular annotation in the genome for a transcription factor.

    Attributes:
        tf (:obj:`TranscriptionFactor`): Transcription factor to which annotation refers to.
        transcript (:obj:`PlanatianContig`): Transcript from which TSS was computed (if any).
        score (float): Score as reported by HOMER.
        sequence (str): Predicted binding sequence.
        offset (int): Offset as reported by HOMER.
    """
    def __init__(self, motif, start, end, chromosome, score, sequence, distance):
        self.motif = motif
        self.start = start
        self.end = end
        self.chromosome = chromosome
        self.score = round(float(score), 2)
        self.sequence = sequence
        self.distance = distance


class TfMotif(Node):
    """
    Class for Transcription Factors in PlanNET

    Attributes:
        symbol (str): Full unique symbol of tf.
        database (str): 'Tf'.
        name (str): Tf short name.
        homer_url (str): URL to Homer TF page.
        logo_url (str): URL to Homer logo image.
        identifier (int): Homer TF identifier (optional).
    """

    allowed_databases = set(["Tf_motif"])
    def __init__(self, symbol, database, 
                 name=None, url=None, tf_name=None, 
                 domain=None, number=None, query=True):
        super(TfMotif, self).__init__(symbol, database)
        self.symbol = symbol
        self.name = name
        self.url = url
        self.number = number
        self.tf_name = tf_name
        self.domain = domain


        if query:
            self.__query_node()
    
    def __query_node(self):
        query = neoquery.MOTIF_QUERY % (self.symbol)
        results = GRAPH.run(query)
        results = results.data()
        if results:
            self.symbol = results[0]['symbol']
            self.name = results[0]['name']
            self.url = results[0]['url']
            self.number = results[0]['number']
            self.tf_name = results[0]['tf_name']
            self.domain = results[0]['domain']
        else:
            raise exceptions.NodeNotFound(self.symbol, self.database)




# To avoid import errors
from NetExplorer.models.mysql_models import *
from NetExplorer.models import neo4j_queries as neoquery
from NetExplorer.models import exceptions