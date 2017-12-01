# Create your views here.

from django.shortcuts   import render
from django.shortcuts   import render_to_response
from django.http        import HttpResponse
from django.template    import RequestContext


def netcell(request):
    '''
    Main view for Netcell
    '''

    return render(request, 'Netcell/netcell.html')
