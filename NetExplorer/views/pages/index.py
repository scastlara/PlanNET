from ..helpers.common import *

def index(request):
    """
    Index view for PlanNET.

    Accepts:
        * **GET**

    Template:
        * **NetExplorer/index.html**
    """

    return render(request, 'NetExplorer/index.html')