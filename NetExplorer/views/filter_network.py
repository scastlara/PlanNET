from .common import *

def filter_network(request):
    '''
    Filters network in PlanExp according to the specified conditions.
    '''
    if request.is_ajax():
        experiment = request.GET.get('experiment')
        dataset = request.GET.get('dataset')
        inclusive_flag = request.GET.get('inclusive_flag')
        conditions = json.loads(request.GET.get('conditions'))
        min_exp = request.GET.get('min_exp')
        node_ids = json.loads(request.GET.get('node_ids'))

        if not conditions or not node_ids:
            return HttpResponse("", content_type="application/json")
        
        condition_gene_sets = [] # List of sets
        experiment = Experiment.objects.get(name=experiment)
        for condition in conditions:
            mean_exp_genes = ExpressionCondition.objects.filter(
                experiment = experiment,
                gene_symbol__in = node_ids,
                condition = Condition.objects.get(name=condition, experiment=experiment),
                sum_expression__gte=0
            ).values_list("gene_symbol", flat=True)
            condition_gene_sets.append(set(mean_exp_genes))

        if inclusive_flag == "inclusive":
            # Genes expressed in at least one condition
            list_of_genes = list(condition_gene_sets[0].union(*condition_gene_sets[1:]))
        else:
            # Genes expressed in ALL conditions
            list_of_genes = list(condition_gene_sets[0].intersection(*condition_gene_sets[1:]))
        return HttpResponse(json.dumps(list_of_genes), content_type="application/json")
    else:
        return HttpResponse("", content_type="application/json")