from .common import *

def regulatory_links(request):
    """
    View from PlanExp that returns the HTML of a table comparing two conditions
    """
    if request.is_ajax():
        exp_name = request.GET['experiment']
        dataset_name = request.GET['dataset']
        experiment = Experiment.objects.get(name=exp_name)
        dataset = Dataset.objects.get(name=dataset_name)
        response = dict()

        regulatory_links = RegulatoryLinks.objects.filter(experiment=experiment, dataset=dataset)
        if regulatory_links:
            response_to_render = { 'links' : regulatory_links, 'database': dataset }
            response = render_to_string('NetExplorer/regulatory_links_table.html', response_to_render)
        else:
            response = None

        return HttpResponse(response, content_type="application/html")
    else:
        return render(request, 'NetExplorer/404.html')