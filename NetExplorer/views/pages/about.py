from ..helpers.common import *

def about(request):
    """
    About page.

    Accepts:
        * **GET**

    Response:
        * **databases** (`list` of `Dataset`): List of datasets to which user has access to.

    Template:
        * **NetExplorer/about.html**
    """
    return render(request, 'NetExplorer/about.html', {'databases': Dataset.get_allowed_datasets(request.user)})
