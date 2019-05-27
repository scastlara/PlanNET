from ....helpers.common import *

def experiment_dataset(request):
    """
    Retrieves datasets for which an experiment has data.
    
    Accepts:
        * **GET + AJAX**

    Args:
        experiment (`str`): Experiment name.
        
    Response:
        * **GET + AJAX**:
           * **str**: JSON with serialized :obj:`Dataset` s.

    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        experiment = Experiment.objects.get(name=exp_name)
        datasets = ExperimentDataset.objects.filter(experiment=experiment).values('dataset')
        datasets = Dataset.objects.filter(id__in=datasets)
        serialized_datasets = serializers.serialize('json', datasets)
        return HttpResponse(serialized_datasets, content_type="application/json")
    else:
        return render(request, 'NetExplorer/404.html')