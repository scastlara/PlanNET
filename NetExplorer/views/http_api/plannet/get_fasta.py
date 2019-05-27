from ...helpers.common import *


def get_fasta(request):
    """
    View that serves FASTA files
    
    Accepts:
        * **GET**

    Args:
        genesymbol (`str`): Identifier of entity for which to download FASTA.
        database (`str`): Database of genesymbol.
        type (`str`): Type of sequence to download ("sequence" or "orf").

    Response:
        * **GET**:
           * **HttpResponse**: Response with a file.
    
    Example:

        .. code-block:: bash

            curl -H "Content-Type: application/json" \\
                 -X GET \\
                 "https:/compgen.bio.ub.edu/PlanNET/get_fasta?genesymbol=SMESG000079934.1&database=Smesgene&type=sequence"
                 
    """

    genesymbol   = request.GET['genesymbol']
    typeseq      = request.GET['type']
    if "database" in request.GET:
        database = request.GET['database']
    else:
        pass # server error!!

    node = None
    try:
        gsearch = GeneSearch(genesymbol, database)
        if database == "Smesgene":
            node = gsearch.get_planarian_genes()[0]
        else:
            node = gsearch.get_planarian_contigs()[0]
    except (exceptions.NodeNotFound, exceptions.IncorrectDatabase) as err:
        pass # server error!

    sequence = str()
    filename = "%s" % node.symbol
    if typeseq == "sequence":
        sequence = textwrap.fill(node.sequence, 70)
        filename = filename + ".fa"
    elif typeseq == "orf":
        sequence = textwrap.fill(node.orf, 70)
        filename = filename + "-orf.fa"

    sequence = ">%s\n" % node.symbol + sequence
    response = HttpResponse(sequence, content_type='text/plain; charset=utf8')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response