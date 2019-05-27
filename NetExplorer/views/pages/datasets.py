from ..helpers.common import *

def datasets(request):
    """
    Datasets view that contains information about the datasets in PlanNET.

    Accepts:
        * **GET**

    Response:
        * **databases** (`list` of `Dataset`): List of datasets to which user has access to.

    Template:
        * **NetExplorer/datasets.html**
    """
    datasets = Dataset.get_allowed_datasets(request.user)
    return render(request, 'NetExplorer/datasets.html', {'databases': datasets})