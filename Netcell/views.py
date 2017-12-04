# Create your views here.

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http      import HttpResponse
from django.template  import RequestContext
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import json

def netcell(request):
    '''
    Main view for Netcell
    '''
    return render(request, 'Netcell/netcell.html')

'''
def tsneplot(request):
    View for making a TSNE plot
    if request.is_ajax():
        # Go on
        pass
    else:
        pass

    return HttpResponse("", content_type="application/json")
'''

def netcellpca(request):
    '''
    Computes PCA of expression array of arrays
    '''
    if request.is_ajax():
        # Perform PCA
        
        response_data = {}
        response_data['result'] = 'error'
        response_data['message'] = 'Some error message'
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
    else:
        return HttpResponse("ups", mimetype="application/json")
