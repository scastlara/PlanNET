from .common import *

def downloader(request):
    """
    Handles the download of sequence and annotations
    """
    MAX_IDS = 10000
    if 'identifiers' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')
    if 'data' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')
    if 'database' not in request.POST:
        return render(request, 'NetExplorer/downloads.html')

    identifiers = request.POST['identifiers']
    identifiers = re.split(r"[\n\r,;]+", identifiers)
    identifiers = [ symbol.replace(" ", "") for symbol in identifiers ]
    if len(identifiers) > MAX_IDS and not request.user.is_authenticated():
        identifiers = identifiers[0:MAX_IDS]
    database = request.POST['database']
    data = request.POST['data']
    dhandler = DownloadHandler()
    file = dhandler.download_data(identifiers, database, data)
    response = file.to_response()
    return response