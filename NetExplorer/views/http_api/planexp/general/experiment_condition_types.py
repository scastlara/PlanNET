from ....helpers.common import *

def experiment_condition_types(request):
    """
    Gets Condition-ConditionType mappings for a given experiment.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.

    Response:
        * **GET + AJAX**:
           * **str**: JSON with list of ConditionType names.
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        conditions = Condition.objects.filter(experiment__name=exp_name)
        ctypes = ConditionType.objects.filter(condition__in=conditions).distinct()
        ctypes = list(ctypes)
        ctypes.sort(key= lambda i: (i.is_interaction, i.name))

        return HttpResponse(json.dumps([ ctype.name for ctype in ctypes ]), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')