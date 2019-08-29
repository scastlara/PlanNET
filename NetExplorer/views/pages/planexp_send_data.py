from ..helpers.common import *


def planexp_send_data(request):
    """
    Views for PlanExp send your data.

    Accepts:
        * **GET**
    """
    return render(request, 'NetExplorer/planexp_send_data.html')