from common import *

def about(request):
    """
    View for about
    """
    return render(request, 'NetExplorer/about.html', {'databases': get_databases(request)})
