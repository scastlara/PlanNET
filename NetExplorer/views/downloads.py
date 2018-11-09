from common import *

def downloads(request):
    """
    View for downloads
    """
    response = dict()
    response['databases'] = get_databases(request)
    return render(request, 'NetExplorer/downloads.html', response)
