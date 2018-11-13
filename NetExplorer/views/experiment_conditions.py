from common import *

def experiment_conditions(request):
    """
    View from PlanExp that returns conditions for a given experiment
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        if 'type' in request.GET:
            condition_type = request.GET['type']
            conditions = Condition.objects.filter(experiment__name=exp_name, cond_type__name=condition_type)
        else:
            conditions = Condition.objects.filter(experiment__name=exp_name)

        serialized_conditions = serializers.serialize('json', conditions)
        return HttpResponse(serialized_conditions, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')