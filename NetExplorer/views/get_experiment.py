from common import *

def get_experiment(request):
    """
    View from PlanExp that returns information about a given experiment
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        experiment = Experiment.objects.get(name=exp_name)
        return HttpResponse(experiment.to_json(), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')