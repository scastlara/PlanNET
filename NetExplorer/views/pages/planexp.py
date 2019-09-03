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

    experiment = request.POST.get("experiment")
    dataset = request.POST.get("dataset")
    graph = request.POST.get("graph-to-send")

    if experiment and dataset:
        # Entry point with everything selected.
        response = {
            'experiments': experiments,
            'experiment': experiment,
            'dataset': dataset,
            'graph': graph
        }
        return render(request, 'NetExplorer/planexp.html', response)
    else:
        # Entry point without selecting anything.
        return render(request, 'NetExplorer/planexp.html', { 'experiments': experiments })