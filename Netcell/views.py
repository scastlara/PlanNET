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
        dims = int(request.POST['reducedDims'])
        perp = int(request.POST['perplexity'])
        cellexp = request.POST.getlist('cellexp[]')
        cellexp = [[float(number) for number in group.split(",")] for group in cellexp]
        if dims < len(cellexp[0]):
            # Dimensions smaller than sample dimensions (num of genes)
            # Perform pca
            pca = PCA(n_components=dims)
            pca.fit(cellexp)
            cellexp = pca.transform(cellexp)
        else:
            # Don't do pca
            pass

        # Perform tSNE
        tsne = TSNE(n_components=2, perplexity=perp)
        tsne_coords = tsne.fit_transform(cellexp)
        x, y = [],[]
        for el in tsne_coords:
            x.append(el[0])
            y.append(el[1])
        x = str(x)
        y = str(y)

        # Build JSON response
        response_data = {}
        response_data['x'] = x
        response_data['y'] = y
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
    else:
        return HttpResponse("ups", mimetype="application/json")
