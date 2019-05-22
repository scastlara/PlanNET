from ..helpers.common import *

def logout(request):
    """
    Logout view
    """
    django_logout(request)
    return render(request, 'NetExplorer/index.html')