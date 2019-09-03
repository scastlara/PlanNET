from ..helpers.common import *

def planexp_send_data(request):
    """
    Views for PlanExp send your data.

    Accepts:
        * **POST**
    """

    if request.POST:
        data = {}
        data['user_email'] = request.POST.get("mail-data")
        data['title'] = request.POST.get("title-data")
        data['publication'] = request.POST.get("publication-data")
        data['data_link'] = request.POST.get("link-to-data")
        data['description'] = request.POST.get("description-data")
        data['public_permissions'] = request.POST.get("public-data")
        
        missing = []
        for field, value in data.items():
            if not value:
                missing.append(field)
        if missing:
            missing = [ format_field(field) for field in missing ]
            return render(request, 'NetExplorer/planexp_send_data.html', { 'missing': missing })
        else:
            send_data_email(data)
            return render(request, 'NetExplorer/planexp_send_data.html', { 'ok': True, 'title': data['title'] })
    else:
        return render(request, 'NetExplorer/planexp_send_data.html')

def format_field(field):
    field = field.title()
    field = field.replace("_", " ")
    return field

def send_data_email(data):
    pass