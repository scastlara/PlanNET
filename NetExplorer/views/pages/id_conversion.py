from ..helpers.common import *

def id_conversion(request):
    if not request.POST:
        return render(request, 'NetExplorer/id_conversion.html',{'databases':  Dataset.get_allowed_datasets(request.user)})
    else:
        query_identifiers = request.POST.get("query-identifiers")
        to_database = request.POST.get("database-to")
        by_database = request.POST.get("database-by")

        if not query_identifiers or not to_database or not by_database:
            return render(request, 'NetExplorer/id_conversion.html',{'databases':  Dataset.get_allowed_datasets(request.user), 'error_msg': "Invalid query"})
        else:
            query_identifiers = re.split(r"\n|,|\s+", query_identifiers)
            query_identifiers = [ query_identifier for query_identifier in query_identifiers if query_identifier ]
            id_converter = IDConverter(query_identifiers)
            results = id_converter.convert(to_database, by_database)
            print(results)
            results = {
                'databases': Dataset.get_allowed_datasets(request.user),
                'results': results
            }

            return render(request, 'NetExplorer/id_conversion.html', results)