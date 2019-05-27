from ....helpers.common import *


def get_dataset_regexes(request):
    """
    Returns Dataset regexes.
    
    Accepts:
        * **GET**

    Response:
        * **GET**:
           * **str**: 

           .. code-block:: javascript

                {
                    "html": str,
                    "exp_type": str
                }

    """
    regexes = Dataset.objects.all().values('name', 'identifier_regex')
    prefix_default_length = 10 # Default length of contig identifier prefix

    results = list()
    for result in regexes:
        if result['name'] == "Dresden":
            results.append((result['identifier_regex'], result['name'], 13))
        else:
            results.append((result['identifier_regex'], result['name'], prefix_default_length))
       
    # CUSTOM LENGTHS
    # These are arbitrary, and I chose them because I think they 
    # are best.
    results.append( ('^SMESG', 'Smesgene', 11) )
    results.append( ('^PF\\d+', 'Pfam', 4) )
    results.append( ('^GO:', 'Go', 7) )
    results.append( ('^_', 'Dresden', 3) )

    return HttpResponse(json.dumps(results), content_type="application/json")