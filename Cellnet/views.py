# Create your views here.

from django.shortcuts   import render
from django.shortcuts   import render_to_response
from django.http        import HttpResponse
from django.template    import RequestContext


def cellnet(request):
    '''
    Main view for Cellnet
    '''

    return render(request, 'Cellnet/cellnet.html')
