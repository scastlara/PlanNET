from common import *

def experiment_dge_table(request):
    """
    View from PlanExp that returns the HTML of a table comparing two conditions
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        c1_name = request.GET['condition1']
        c2_name = request.GET['condition2']
        dataset_name = request.GET['dataset']
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        condition1 = Condition.objects.get(name=c1_name, experiment=experiment)
        condition2 = Condition.objects.get(name=c2_name, experiment=experiment)
        expression = ExpressionRelative.objects.filter(experiment=experiment, dataset=dataset, condition1=condition1, condition2=condition2).order_by('-fold_change')[:500]
        if not expression:
            # In case condition1 and condition2 are reversed in Database
            expression = ExpressionRelative.objects.filter(
                experiment=experiment, dataset=dataset, 
                condition1=condition2, condition2=condition1).order_by('-fold_change')[:100]
        return render(request, 'NetExplorer/experiment_dge_table.html', { 'expressions' : expression, 'database': dataset })
    else:
        return render(request, 'NetExplorer/404.html')