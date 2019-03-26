from .common import *
from django_mysql.models import Model
from django.db.models import Avg

# MODELS
# ------------------------------------------------------------------------------
class Dataset(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField(max_length=4)
    citation = models.CharField(max_length=512)
    url = models.URLField(max_length=200)
    n_contigs = models.IntegerField(max_length=1000000)
    n_ints = models.IntegerField(max_length=2000000)
    identifier_regex = models.CharField(max_length=200)
    public = models.BooleanField()

    def is_symbol_valid(self, symbol):
        '''
        Checks if a given symbol belongs to database based on 
        the symbol naming convention.
        '''
        if re.match(self.identifier_regex, symbol):
            return True
        else:
            return False

    @classmethod
    def get_allowed_datasets(cls, user):
        '''
        Returns QuerySet of allowed datasets for a given user
        '''
        public_datasets = cls.objects.filter(public=True).order_by('-year')
        if not user.is_authenticated:
            # Return only public datasets
            return public_datasets
        else:
            # user is authenticated, return allowed datasets
            restricted_allowed = cls.objects.filter(userdatasetpermission__user=user).order_by('-year')
            all_allowed = public_datasets | restricted_allowed
            return all_allowed
    
    def __str__(self):
       return self.name


# ------------------------------------------------------------------------------
class UserDatasetPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    def __str__(self):
       return self.user.username + " [access to] " + self.dataset.name


# ------------------------------------------------------------------------------
class ExperimentType(models.Model):
    exp_type = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
       return self.exp_type


# ------------------------------------------------------------------------------
class Experiment(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    citation = models.CharField(max_length=512)
    url = models.URLField(max_length=200)
    exp_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)
    public = models.BooleanField()

    @classmethod
    def get_allowed_experiments(cls, user):
        '''
        Returns QuerySet of allowed experiments for a given user
        '''
        public_experiments = cls.objects.filter(public=True).order_by('name')
        if not user.is_authenticated:
            # Return only public datasets
            return public_experiments
        else:
            # user is authenticated, return allowed datasets
            restricted_allowed = cls.objects.filter(userexperimentpermission__user=user).order_by('name')
            all_allowed = public_experiments | restricted_allowed
            return all_allowed

    def to_json(self):
        '''
        Returns json string with info about experiment
        '''
        json_dict = {
            'name': self.name,
            'description': self.description,
            'citation': self.citation,
            'url': self.url,
            'type': self.exp_type.exp_type
        }
        conditions = Condition.objects.filter(experiment__name=self.name)
        json_dict['conditions'] = dict()
        for cond in conditions:
            if cond.cond_type.name not in json_dict['conditions']:
                json_dict['conditions'][cond.cond_type.name] = list()
            json_dict['conditions'][cond.cond_type.name].append( 
                (cond.name, cond.defines_cell_type, cond.cell_type, cond.description) 
            )
        json_string = json.dumps(json_dict)
        return json_string

    def __str__(self):
       return self.name

# ------------------------------------------------------------------------------
class ExperimentDataset(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
       return self.experiment.name + ' - ' + self.dataset.name


# ------------------------------------------------------------------------------
class UserExperimentPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
       return self.user.username + " [access to] " + self.experiment.name


# ------------------------------------------------------------------------------
class ConditionType(models.Model):
    '''
    1 Batch (technical condition).
    2 Experimental condition.
    3 Cluster.
    '''
    name = models.CharField(max_length=50)
    description = models.TextField()
    is_interaction = models.BooleanField(default=False)

    def __str__(self):
       return self.name


# ------------------------------------------------------------------------------
class Condition(models.Model):
    '''
    Technical conditions, Experimental conditions, Clusters, and Cells will be stored here.
    '''
    name = models.CharField(max_length=50)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    cond_type = models.ForeignKey(ConditionType, on_delete=models.CASCADE)
    defines_cell_type = models.BooleanField()
    cell_type = models.CharField(max_length=50)
    description = models.TextField()
    max_expression = None
    min_expression = 0

    def __str__(self):
       return self.name + " - " + self.experiment.name
    
    def __get_max_expression(self, dataset):
        '''
        Gets max expression of samples in this particular condition.
        Assigns it to self.max_expression and returns it.
        '''
        samples = SampleCondition.objects.filter(condition=self).values_list('sample', flat=True)

        self.max_expression = ExpressionAbsolute.objects.filter(
            experiment=self.experiment,
            dataset=dataset,
            sample__in=list(samples)
        ).aggregate(Max('expression_value'))

        self.max_expression = self.max_expression['expression_value__max']

        self.max_expression = round(self.max_expression, 3)
        return self.max_expression
        
    def get_color(self, dataset, value, profile="red", max_v=None):
        '''
        Returns expression color for a given expression value. 
        Will use one of the saved color profiles 'red', 'green' or 'blue'.

        If max_v is provided, the color will be determined using a scale from 0 to max_v. 
        Otherwise, max_v will be computed as the maximum expression value for a 
        particular experiment + condition.
        '''
        if max_v is None:
            # Compute max expression for the whole experiment
            if self.max_expression is None:
                # Compute only once
                self.__get_max_expression(dataset)
        else:
            # Max expression is provided.
            self.max_expression = max_v
        color_gradient = colors.ColorGenerator(self.max_expression, self.min_expression, profile)
        return color_gradient.map_color(value)

    def get_color_legend(self, profile="red", units=None):
        '''
        Returns html of color gradient generated for expression in Condition
        '''
        if self.max_expression is None:
            self.__get_max_expression()
        color_gradient = colors.ColorGenerator(self.max_expression, self.min_expression, profile)
        return color_gradient.get_color_legend(units)



# ------------------------------------------------------------------------------
class Sample(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample_name  = models.CharField(max_length=50)

    def __str__(self):
       return self.sample_name + " - " + self.experiment.name


# ------------------------------------------------------------------------------
class SampleCondition(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)

    def __str__(self):
       return self.experiment.name + " - " + self.sample.sample_name + " - " + self.condition.name

# ------------------------------------------------------------------------------
class ExpressionAbsolute(Model):
    '''
    This table will store the expression value for each condition (for a given experiment and a given gene). 
    Keep in mind that a 'Condition' can be a Technical-Condition (0), Experimental-Condition (2), Cluster (3) or a Cell (4).
    In the case of 0, 1, 2, and 3 the expression will be the MEAN expression for that gene in those samples.
    In the case of 4 (a cell), the expression will be the actual expression in that particular cell. 
    The cell will have an entry in the 'Condition' table, just like any condition, linking it to a particular experiment.

    This is a django-mysql Model, which is an extension of the default models.Model class. Includes use_index() method.
    '''
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    gene_symbol = models.CharField(max_length=50)
    expression_value = models.FloatField()
    units = models.CharField(max_length=25)

    def __str__(self):
        name_str = self.experiment.name + " - "
        name_str += str(self.sample.sample_name) + " - "
        name_str += str(self.gene_symbol) + ": "
        name_str += str(self.expression_value) + " "
        name_str += self.units
        return name_str

    @classmethod
    def get_condition_expression(cls, experiment, dataset, conditions, ctype, genes):
        '''Method for getting gene expression in a set of conditions.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
        
        Returns:
            condition_expression (`dict` of `str`: `list`): Key is gene symbol, value 
                is vector of expression in each condition, in the same order as `condition`.
        '''
        condition_expression = dict()

        conditions_ctype = Condition.objects.filter(
            experiment=experiment,
            cond_type_id=ConditionType.objects.get(name=ctype)
        )

        sample_condition = SampleCondition.objects.filter(
            experiment=experiment,
            condition__in=conditions_ctype
        ).select_related('condition').select_related('sample').values('sample', 'sample__sample_name', 'condition')
        
        sc_dict = defaultdict(lambda: list())
        for sc in sample_condition:
            sc_dict[sc['condition']].append(sc['sample'])
        
        expression = cls.objects.filter(
            experiment=experiment, dataset=dataset,
            gene_symbol__in=list(genes)
        ).select_related('sample').values(
            'sample', 
            'gene_symbol', 
            'expression_value')

        exp_dict = defaultdict(lambda: defaultdict(float))
        for exp in expression:
            exp_dict[exp['sample']][exp['gene_symbol']] = exp['expression_value']
        
        for condition in conditions:
            samples_in_condition = sorted(sc_dict[condition.id])
            exp_in_condition = defaultdict(float)
            for sample in samples_in_condition:
                if sample in exp_dict:
                    for gene, expval in exp_dict[sample].items():
                        exp_in_condition[gene] += expval
            
            for gene in genes:
                if gene not in condition_expression:
                    condition_expression[gene] = list()

                if gene not in exp_in_condition:
                    condition_expression[gene].append(0)
                else:
                    condition_expression[gene].append(exp_in_condition[gene]/len(samples_in_condition))
        return condition_expression

        
    @classmethod
    def get_sample_expression(cls, experiment, dataset, conditions, genes, only_expressed=False):
        '''Method for getting gene expression in all samples.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
            only_expressed (bool): Flag, return only expression for samples with expression > 0?
        
        Returns:
            sample_expression (`dict` of `str`: `list`): Key is gene symbol, value 
                is vector of expression in each sample, sorted by condition.
            
            gene_conditions (`dict` of `str`: `list`): Key is gene_symbol, value is
                vector with samples for which gene has expression, same order as `list`
                in sample_expression[gene].

        '''
        sample_expression = dict()
        genes_found = set()
        gene_conditions = dict()
        for condition in conditions:
            samples = SampleCondition.objects.filter(
                experiment=experiment, 
                condition=condition
            ).order_by('sample').values_list('sample', flat=True)
            expression = ExpressionAbsolute.objects.filter(
                experiment=experiment,   dataset=dataset, 
                sample__in=list(samples), gene_symbol__in=list(genes)
            ).values('gene_symbol', 'sample', 'expression_value')
            
            genes_found = set()
            gene_expression_dict = dict()
            for exp in expression:
                genes_found.add(exp['gene_symbol'])
                if exp['gene_symbol'] not in gene_expression_dict:
                    gene_expression_dict[exp['gene_symbol']] = dict()
                gene_expression_dict[exp['gene_symbol']][exp['sample']] = exp['expression_value']

            # Add missing genes
            genes_missing = set(genes).difference(genes_found)
            for missing in genes_missing:
                if missing not in gene_expression_dict:
                    gene_expression_dict[missing] = dict()

            # Add missing cells
            for gene, sample_exp in gene_expression_dict.items():
                gcounter = 0
                if gene not in sample_expression:
                    sample_expression[gene] = list()
                    
                for sample in samples:
                    if sample not in sample_exp:
                        if not only_expressed:
                            sample_expression[gene].extend([0])
                            if gene not in gene_conditions:
                                gene_conditions[gene] = list()
                            gene_conditions[gene].append(condition.name)
                    else:
                        if gene not in gene_conditions:
                            gene_conditions[gene] = list()
                        sample_expression[gene].extend([ sample_exp[sample] ])
                        gene_conditions[gene].append(condition.name)
                        gcounter += 1

                if only_expressed:
                    if gcounter < 2:
                        missing = 2 - gcounter 
                        for i in range(0, missing):
                            sample_expression[gene].append(0)
                            if gene not in gene_conditions:
                                gene_conditions[gene] = list()
                            gene_conditions[gene].append(condition.name)

        return sample_expression, gene_conditions

    @classmethod
    def get_mean_expression(cls, experiment, dataset, conditions, genes):
        '''Return mean gene expression for samples with expression > 0 for all genes.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
        
        Returns:
            celldict (`dict` of `str`: `float`): Key is sample name, value is 
                mean expression for all `genes`. Only samples with expression for all
                genes in `genes`.
        '''

        celldict = dict()
        for condition in conditions:
            samples = SampleCondition.objects.filter(
                experiment=experiment, 
                condition=condition
            ).select_related('sample').order_by('sample').values('sample', 'sample__sample_name')

            sample_names = { sample['sample']: sample['sample__sample_name'] for sample in samples }
            samples = [ sample['sample'] for sample in samples ]

            #print(samples)
            # Get cells with num of genes with expression > 0 == len(gene_symbols)
            filtered_cells = list(ExpressionAbsolute.objects.filter(
                experiment=experiment,   
                dataset=dataset, 
                sample__in=list(samples), 
                gene_symbol__in=genes).values('sample').annotate(
                gcount=Count('gene_symbol'), 
                expmean=Avg('expression_value')).filter(gcount = len(genes)))

            if not filtered_cells:
                continue

            for cell in filtered_cells:
                celldict[ sample_names[cell['sample']] ] = cell['expmean']
        return celldict
            




# ------------------------------------------------------------------------------
class CellPlotPosition(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    x_position = models.FloatField()
    y_position = models.FloatField()


# ------------------------------------------------------------------------------
class ExpressionRelative(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    condition1 = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='condition1_expressionrelative_set')
    condition2 = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='condition1_expressionrelative_setsubcondition')
    cond_type = models.ForeignKey(ConditionType, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    gene_symbol = models.CharField(max_length=50)
    fold_change = models.FloatField()
    pvalue = models.FloatField()

    def __str__(self):
        name_str = self.experiment.name + " - "
        name_str += self.condition1.name + " vs "
        name_str += self.condition2.name + " - "
        name_str += str(self.gene_symbol) + ": "
        name_str += str(self.fold_change) + " "
        name_str += "(p=" + str(self.pvalue) + ")"
        return name_str


# ------------------------------------------------------------------------------
class ExperimentGene(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    gene_symbol =  models.CharField(max_length=50)

    def __str__(self):
        name_str = self.experiment.name + " - "
        name_str += self.gene_symbol
        return name_str

# ------------------------------------------------------------------------------
class RegulatoryLinks(models.Model):
    '''
    Class for regulatory links predicted for a SingleCell Experiment
    '''
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    group = models.IntegerField(max_length=10, default=1)
    regulator = models.CharField(max_length=50)
    target = models.CharField(max_length=50)
    source = models.CharField(max_length=20)
    score = models.FloatField()

# ------------------------------------------------------------------------------
class ClusterMarkers(models.Model):
    '''
    Class for cluster marker genes
    '''
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    gene_symbol = models.CharField(max_length=50)
    auc = models.FloatField()
    avg_diff = models.FloatField()



