from ..helpers.common import *


def planexp(request):
    """
    Views for PlanExp.

    Accepts:
        * **GET**
        
    Response:
        * **experiments** (`list` of :obj:`Experiment`): List of Experiments to which user has access to.
    
    Hint:
        PlanExp works as an async single-page app (for the most part). See `http_api.planexp` for more information.

    """
    experiments = Experiment.get_allowed_experiments(request.user)
    return render(request, 'NetExplorer/planexp.html', { 'experiments': experiments })