from .common import *


def planexp(request):
    experiments = Experiment.get_allowed_experiments(request.user)
    return render(request, 'NetExplorer/planexp.html', { 'experiments': experiments })