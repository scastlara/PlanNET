from ....helpers.common import *

def experiment_summary(request):
    """
    Returns a summary of a selected experiment.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.

    Response:
        * **GET + AJAX**:
           * **str**: JSON with html for summary (template "NetExplorer/experiment_summary.html") and experiment type.

           .. code-block:: javascript

                {
                    "html": str,
                    "exp_type": str
                }

    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        # Get Experiment and Conditions
        experiment = Experiment.objects.get(name=exp_name)
        conditions = Condition.objects.filter(
            experiment__name=exp_name, 
            cond_type__in=ConditionType.objects.filter(is_interaction=0)
        )
        
        condition_list = dict()
        for condition in sorted(conditions, key=lambda x: condition_sort(x)):
            if condition.cond_type.name not in condition_list:
                condition_list[condition.cond_type.name] = []
            condition_list[condition.cond_type.name].append(condition)

        response = dict()
        response_to_render = { 'experiment': experiment, 'conditions': condition_list }
        response['html'] = render_to_string('NetExplorer/experiment_summary.html', response_to_render)
        response['exp_type'] = experiment.exp_type.exp_type
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')