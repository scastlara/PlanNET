from ....helpers.common import *

def get_possible_comparisons(exp_name):
    '''
    Returns dictionary of possible conditions to compare in DGE table.

    Args:
        exp_name (str): Experiment name
    
    Returns:
        `dict`: Dictionary with comparisons. 
            Only those available for DGE in ExpressionRelative table. Key is 
            condition name, value is `list` with conditions for which "key" has 
            a comparison. 
    '''
    experiment = Experiment.objects.get(name=exp_name)
    exp_relative = ExpressionRelative.objects.filter(experiment=experiment).select_related("condition1", "condition2").values("condition1__name", "condition2__name").distinct()
    
    possible_comparisons = {}
    for exp in exp_relative:
        if exp['condition1__name'] not in possible_comparisons:
            possible_comparisons[exp['condition1__name']] = []
        possible_comparisons[exp['condition1__name']].append(exp['condition2__name'])
        if exp['condition2__name'] not in possible_comparisons:
            possible_comparisons[exp['condition2__name']] = []
        possible_comparisons[exp['condition2__name']].append(exp['condition1__name'])
    return possible_comparisons


def experiment_conditions(request):
    """
    Gets list of conditions for a given experiment and its available comparisons 
    for DGE.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        type (`str`): Condition type name.

    Response:
        * **GET + AJAX**:
           * **str**: JSON with conditions and comparisons.

           .. code-block:: javascript

                {
                    "conditions": ["c1", "c2", "c3"],
                    "comparisons": 
                        {
                            "c1": ["c2"],
                            "c2": ["c1", "c3"],
                            "c3": ["c2"]
                        }
                }
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        if 'type' in request.GET:
            condition_type = request.GET['type']
            conditions = Condition.objects.filter(experiment__name=exp_name, cond_type__name=condition_type)
        else:
            conditions = Condition.objects.filter(experiment__name=exp_name)
        
        response = {}
        response['conditions'] = {}
        response['comparisons'] = get_possible_comparisons(exp_name)

        for cond in sorted(conditions, key=lambda x: condition_sort(x)):
            cond_name = str(cond.name)
            if cond.defines_cell_type and cond.cell_type != "Unknown":
                if cond.name.isdigit():
                    cond_name = str(cond.name) + " (" + cond.cell_type + ")"
                else:
                    cond_name = cond.cell_type
            response['conditions'][cond_name] = cond.cond_type.name
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')