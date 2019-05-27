from ...helpers.common import *


@csrf_exempt
def downloader(request):
    """
    Handles download of data from PlanNET/downloads
    
    Accepts:
        * **POST**

    Args:
        identifiers (`list`): Identifiers for which to download data.
        database (`str`): Database for which we want data.
        data (`str`): What to download. 
            Can be ['contig', 'orf', 'homology', 'pfam', 'go', 'interactions'].

    Response:
        * **HttpResponse**: Response with a file.
    
    Example:

        .. code-block:: bash

            curl -X POST \\
                 --data "identifiers=dd_Smed_v6_740_0_1&database=Dresden&data=contig" \\
                 "https://compgen.bio.ub.edu/PlanNET/downloader"
                 
    """
    databases = Dataset.get_allowed_datasets(request.user)
    if 'identifiers' not in request.POST:
        return render(request, 'NetExplorer/downloads.html', { 'databases': databases })
    if 'database' not in request.POST or not request.POST['database']:
        return render(request, 'NetExplorer/downloads.html', { 'databases': databases, 'error': 'database' })
    if 'data' not in request.POST or not request.POST['data']:
        return render(request, 'NetExplorer/downloads.html', { 'databases': databases, 'error': 'data' })

    identifiers = request.POST['identifiers']
    identifiers = re.split(r"[\n\r,;]+", identifiers)
    identifiers = [ symbol.replace(" ", "") for symbol in identifiers ]
    identifiers = [ re.sub("[\'\"]", "", symbol) for symbol in identifiers ]
    database = request.POST['database']
    data = request.POST['data']
    dhandler = downloaders.DownloadHandler()
    the_file = dhandler.download_data(identifiers, database, data)
    response = the_file.to_response()
    return response