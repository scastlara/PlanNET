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

        ctypes_dge = ConditionType.objects.filter(pk__in=ExpressionRelative.objects.filter(experiment=Experiment.objects.get(name=exp_name)).values('cond_type').distinct())
        ctypes_dge = list(ctypes_dge)
        ctypes_dge.sort(key= lambda i: (i.is_interaction, i.name))

        json_response = {
            'ctypes': [ ctype.name for ctype in ctypes ],
            'ctypes_dge': [ ctype.name for ctype in ctypes_dge ]
        }

        return HttpResponse(json.dumps(json_response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')