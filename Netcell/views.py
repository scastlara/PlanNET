# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import json
import tempfile
import os
from rpy2 import robjects
from rpy2.robjects.packages import importr


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
        x, y = [], []
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


def sce_to_json(request):
    '''
    Gets AJAX request with an sce object and returns the jsons for the
    variables cellexp, cellclusts and celllabels
    '''
    if request.is_ajax():
        # Write temp file with SingleCellExperiment RDS
        error = None
        scefile = request.FILES.get("scefile")
        tup = tempfile.mkstemp()    # make a tmp file
        f = os.fdopen(tup[0], 'w')  # open the tmp file for writing
        f.write(scefile.read())     # write the tmp file
        f.close()
        # R code
        importr("SingleCellExperiment")
        sce = None
        try:
            sce = robjects.r['readRDS'](tup[1])
        except Exception:
            error = "Can't read RDS file"

        # Get needed functions
        base = importr('base')
        dollar = base.__dict__["$"]
        colnames = base.__dict__["colnames"]
        rownames = base.__dict__["rownames"]
        expression = list()
        clusters = list()
        celllabels = list()

        # Get clusters and celllabels
        try:
            fact = dollar(sce, "clusters")
            clusters = list(fact)
            celllabels = list(colnames(sce))
        except Exception:
            error = "SCE object should have 'clusters' slot with a List"

        # Get expression
        try:
            assays = robjects.r("assays")
            expdata = dollar(assays(sce), "logcounts")
            expdata = expdata.transpose()
            for cellidx in range(1, len(celllabels)):
                expression.append([expdata.rx(cellidx, i)[0]
                                   for i in range(1, len(rownames(sce) + 1))])
        except Exception:
            error = "Could not retrieve '$logcounts' from SCE object"

        response = json.dumps({
            'cellexp': expression,
            'celllabels': celllabels,
            'cellclust': clusters,
            'error': error
        })

        return HttpResponse(response, mimetype="application/json")
    else:
        render(request, 'NetExplorer/404.html')
