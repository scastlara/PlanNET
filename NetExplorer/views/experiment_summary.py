from common import *

def experiment_summary(request):
    """
    View from PlanExp that returns information about a given experiment
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        experiment = Experiment.objects.get(name=exp_name)
        conditions = Condition.objects.filter(experiment__name=exp_name)
        condition_list = dict()
        for condition in conditions:
            if condition.cond_type.name not in condition_list:
                condition_list[condition.cond_type.name] = list()
            condition_list[condition.cond_type.name].append(condition)
        response = { 'experiment': experiment, 'conditions': condition_list }
        return render(request, 'NetExplorer/experiment_summary.html', response)
    else:
        return render(request, 'NetExplorer/404.html')