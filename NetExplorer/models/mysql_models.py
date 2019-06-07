from .common import *
from django_mysql.models import Model
from django.db.models import Avg

# MODELS
# ------------------------------------------------------------------------------
class Dataset(models.Model):
    """
    Model that describes the table for storing information about 
    the transcriptome Datasets available in PlanExp and PlanNET.

    Attributes:
        name: Name of the dataset.
        year: Year of publication (if available).
        citation: Citation string to be shown on the website.
        url: Url to the publication.
        n_contigs: Number of contigs (transcripts) in this dataset.
        n_ints: Number of predicted interactions for this dataset.
        identifier_regex: Regular expression of the identifiers used 
            for this dataset.
        public: Boolean to define if it is a public dataset (`True`) or private (`False`).
    """
    name = models.CharField(max_length=50)
    year = models.IntegerField(max_length=4)
    citation = models.CharField(max_length=512)
    url = models.URLField(max_length=200)
    n_contigs = models.IntegerField(max_length=1000000)
    n_ints = models.IntegerField(max_length=2000000)
    identifier_regex = models.CharField(max_length=200)
    public = models.BooleanField()

    def is_symbol_valid(self, symbol):
        """
        Checks if a given symbol belongs to Dataset based on 
        the symbol naming convention.

        Args:
            symbol (str): String of an identifier to check if it
                matches the regex for this dataset.
        
        Returns:
            bool: `True` if symbol belongs to this Dataset, 
                otherwise `False`.
        """
        if re.match(self.identifier_regex, symbol):
            return True
        else:
            return False

    @classmethod
    def get_allowed_datasets(cls, user):
        """
        Classmethod that returns QuerySet of allowed datasets for a given user.

        Args:
            user (User): User object.
        
        Returns:
            `list` of `Dataset`: List of Dataset objects sorted by year 
                to which `user` has permissions to.
        """
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
    """
    Table with user permissions to Datasets.

    Attributes:
        user: ForeignKey to User.
        dataset: ForeignKey to Dataset.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    def __str__(self):
       return self.user.username + " [access to] " + self.dataset.name


# ------------------------------------------------------------------------------
class ExperimentType(models.Model):
    """
    Table with experiment types in PlanExp.

    Attributes:
        exp_type: Name of the experiment type.
        description: Description of the experiment type.
    """
    exp_type = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
       return self.exp_type


# ------------------------------------------------------------------------------
class Experiment(models.Model):
    """
    Table with RNA-seq and scRNA-seq Experiment information.

    Attributes:
        name: Name of the experiment.
        description: Description of the experiment.
        citation: Citation string of experiment publication.
        url: Url of the publication.
        exp_type: Foreign Key to the corresponding ExperimentType.
        public: Boolean to define if it is a public experiment (`True`) or private (`False`).
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    citation = models.CharField(max_length=512)
    url = models.URLField(max_length=200)
    exp_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)
    public = models.BooleanField()

    @classmethod
    def get_allowed_experiments(cls, user):
        """
        Returns QuerySet of allowed experiments for a given user.

        Args:
            user (User): User for which to retrieve allowed experiments.

        Returns:
            QuerySet: QuerySet of allowed experiments to which user has 
                permission to.
        """
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
        """
        Returns json string with info about experiment.

        Returns:
            str: JSON string of serialized Experiment. Contains:
                - 'name'
                - 'description'
                - 'citation'
                - 'url'
                - 'type'
        """
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


    def is_one_sample(self, ctype=None, conditions=None):
        '''
        Checks if there is only one sample per condition in experiment.

        Args:
            ctype (`str`): ConditionType name.
            conditions (`list` of `Condition`): List of conditions for Experiment.
        
        Returns:
            bool: True if experiment has only one sample per condition. False otherwise.

        Raises:
            ValueError: If neither 'ctype' nor 'conditions' is provided.
        '''
        if ctype is not None:
            conditions = Condition.objects.filter(
                experiment__name=self.name, 
                cond_type=ConditionType.objects.get(name=ctype))

        if conditions is not None:
            samples_in_condition = SampleCondition.objects.filter(experiment=self, condition=conditions[0]).count()
        else:
            raise ValueError("Can't determine if Experiment is one_sample without a 'ctype' or 'conditions'")

        if samples_in_condition == 1:
            return True
        else:
            return False


    def __str__(self):
       return self.name

# ------------------------------------------------------------------------------
class ExperimentDataset(models.Model):
    """
    Table with Datasets available for a particular experiment.
    
    Attributes:
        dataset: Foreign Key to Dataset.
        experiment: Foreign Key to Experiment.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
       return self.experiment.name + ' - ' + self.dataset.name


# ------------------------------------------------------------------------------
class UserExperimentPermission(models.Model):
    """
    Table with user permissions to experiments in PlanExp.

    Attributes:
        user: Foreign Key to User.
        experiment: Foreign Key to Experiment.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
       return self.user.username + " [access to] " + self.experiment.name


# ------------------------------------------------------------------------------
class ConditionType(models.Model):
    """
    Types of conditions for a PlanExp experiment.
    1 Batch (technical condition).
    2 Experimental condition.
    3 Cluster.

    Attributes:
        name: Condition Type name.
        description: Description for condition type.
        is_interaction: Bool to define if it results from an interaction 
            of other condition types.
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    is_interaction = models.BooleanField(default=False)

    def __str__(self):
       return self.name


# ------------------------------------------------------------------------------
class Condition(models.Model):
    """
    Table with PlanExp experiment conditions. Technical conditions, 
    Experimental conditions, Clusters, etc. will be stored here.

    Attributes:
        name: Name of condition.
        experiment: Foreign Key to Experiment.
        cond_type: Foreign Key to ConditionType.
        defines_cell_type: Boolean field indicating if condition defines 
            cell types (e.g.: cluster).
        cell_type: If defines_cell_type is True, then cell_type stores 
            the name of the cell type this condition defines.
        description: Description of the Condition.
        
    Attributes:
        max_expression: Maximum expression value in this condition (defaults to `None`).
        min_expression: Minimum expression value in this condition (default to 0).

    """
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
    
    def __get_max_expression(self):
        """
        Gets max expression of samples in this particular condition.
        Assigns it to self.max_expression and returns it.
        """
        
        n_samples = SampleCondition.objects.filter(condition=self).count()
        self.max_expression = ExpressionCondition.objects.filter(
            experiment=self.experiment,
            condition=self
        ).aggregate(Max('sum_expression'))
        
        self.max_expression = self.max_expression['sum_expression__max'] / n_samples
        self.max_expression = round(self.max_expression, 3)
        return self.max_expression
        
    def get_color(self, dataset, value, profile="red", max_v=None):
        """
        Returns expression color for a given expression value. 
        Will use one of the saved color profiles 'red', 'green' or 'blue'.

        If max_v is provided, the color will be determined using a scale from 0 to max_v. 
        Otherwise, max_v will be computed as the maximum expression value for a 
        particular experiment + condition.
        """
        if max_v is None:
            # Compute max expression for the whole experiment
            if self.max_expression is None:
                # Compute only once
                self.__get_max_expression()
        else:
            # Max expression is provided.
            self.max_expression = max_v
        color_gradient = colors.ColorGenerator(self.max_expression, self.min_expression, profile)
        return color_gradient.map_color(value)

    def get_color_legend(self, profile="red", units=None):
        """
        Returns html of color gradient generated for expression in Condition
        """
        if self.max_expression is None:
            self.__get_max_expression()
        color_gradient = colors.ColorGenerator(self.max_expression, self.min_expression, profile)
        return color_gradient.get_color_legend(units)


    @classmethod
    def get_samples_per_condition(cls, experiment, ctype):
        """Method for getting the number of samples per condition of ctype.

            Args:
                experiment (str): Experiment name.
                ctype (str): Condition type. 

            Returns:
                sc_dict (`dict`): Dictionary with conditions and samples mapping.
                    Keys are condition ids (`int`) values are number of samples (`int`) in that condition.

        """
        condition_expression = dict()
        conditions_ctype = Condition.objects.filter(
            experiment=experiment,
            cond_type_id=ConditionType.objects.get(name=ctype)
        )
        sample_condition = SampleCondition.objects.filter(
            experiment=experiment,
            condition__in=conditions_ctype
        ).values('condition').annotate(nsample=Count('sample'))
        sc_dict = { sc['condition'] : sc['nsample'] for sc in sample_condition }
        return sc_dict

# ------------------------------------------------------------------------------
class Sample(models.Model):
    """
    Table for storing samples.

    Attributes:
        experiment: Foreign Key to experiment to which sample belongs to.
        sample_name: Sample name.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample_name  = models.CharField(max_length=50)

    def __str__(self):
       return self.sample_name + " - " + self.experiment.name


# ------------------------------------------------------------------------------
class SampleCondition(models.Model):
    """
    Table with Conditions to which each sample belongs.

    Attributes:
        experiment: Foreign Key to Experiment.
        sample: Foreign Key to Sample.
        condition: Foreign Key to Condition.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)

    def __str__(self):
       return self.experiment.name + " - " + self.sample.sample_name + " - " + self.condition.name

# ------------------------------------------------------------------------------
class ExpressionAbsolute(Model):
    """
    Stores expression for a particular gene in a particular sample. 
    Only stores NON-ZERO values.

    Attributes:
        experiment: Foreign Key to Experiment to which sample belongs to.
        sample: Foreign Key to Sample.
        dataset: Foreign Key to Dataset to which gene_symbol belongs to.
        gene_symbol: String with gene symbol.
        expression_value: Float with the expression value for gene_symbol in sample.
        units: Units in which expression_value are stored (usually logCPM).
    """
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
    def get_sample_expression(cls, experiment, dataset, conditions, genes, only_expressed=False):
        """
        Method for getting gene expression in all samples.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
            only_expressed (bool): Flag, return only expression for samples with expression > 0?
        
        Returns:
            (`dict`, `dict`): Two dictionaries. 
                
                * **1st:** Key is gene symbol (`str`), value is vector of expression in each sample (`list` of `float`), sorted by condition. 
                
                * **2nd:** Key is gene_symbol (`str`), value is vector with conditions for each sample (`list` of `int`), same order as `list` in 1st dictionary.

                .. code-block:: python

                    dict1 = {
                        'gene1': [ float, float, float, ...],
                        ...
                    }
                    dict2 = {
                        'gene1': [ int, int, int, ...],
                        ...
                    }

        """
        sample_expression = defaultdict(list)
        gene_conditions = defaultdict(list)
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT `NetExplorer_samplecondition`.`sample_id`, 
                   `NetExplorer_expressionabsolute`.`gene_symbol`,   
                   `NetExplorer_expressionabsolute`.`expression_value`
            FROM  `NetExplorer_expressionabsolute`
            INNER JOIN NetExplorer_samplecondition ON NetExplorer_expressionabsolute.sample_id = NetExplorer_samplecondition.sample_id
            WHERE `NetExplorer_expressionabsolute`.`experiment_id` = %s
            AND   `NetExplorer_samplecondition`.experiment_id = %s
            AND   `NetExplorer_samplecondition`.condition_id IN (%s)
            AND   `NetExplorer_expressionabsolute`.`gene_symbol` IN (%s);
            """ %
            (
                experiment.id, 
                experiment.id, 
                ', '.join([ "'%s'" % condition.id for condition in conditions ]), 
                ', '.join([ "'%s'" % gene for gene in genes ])
            )
        )
        data = cursor.fetchall()
        datadict = defaultdict(lambda: defaultdict(float))
        for row in data:
            datadict[row[1]][row[0]] = row[2]
        
        for condition in conditions:
            samples = SampleCondition.objects.filter(
                experiment=experiment, 
                condition=condition
            ).order_by('sample').values_list('sample', flat=True)
            for gene in genes:
                gcounter = 0 # keeps track of the number of times this gene appears in this condition.
                             # because Plotly is buggy, if there isn't at least TWO samples with an expression
                             # value for this gene, no violin plot will be displayed (if plotting violins).
                             # As such, if there is less than 2 samples per gene in this condition, we will need
                             # to add them as zero...
                if gene in datadict:
                    for sample in samples:
                        if sample in datadict[gene]:
                            gcounter += 1
                            sample_expression[gene].append(datadict[gene][sample])
                            gene_conditions[gene].append(condition.name)
                        else:
                            if not only_expressed:
                                sample_expression[gene].append(0)
                                gene_conditions[gene].append(condition.name)
                else:
                    for sample in samples:
                        if not only_expressed:
                            sample_expression[gene].append(0)
                            gene_conditions[gene].append(condition.name)

                if only_expressed:
                    if gcounter < 2:
                        for i in range(0, 2):
                            sample_expression[gene].append(0)
                            gene_conditions[gene].append(condition.name)

        return sample_expression, gene_conditions

    @classmethod
    def get_mean_expression(cls, experiment, dataset, conditions, genes):
        """
        Returns mean gene expression for samples with expression > 0 for all provided genes.
        
        Example:
            For genes A and B, will get a value for each cell in experiment where 
            both genes are expressed > 0. Each value will be the mean expression 
            (A + B) / 2 for each sample.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
        
        Returns:
           `dict`: Dictionary with mean expession for condition.
                Key is sample name (`str`), value is 
                mean expression (`float`) for each gene in `genes`. 
                Only samples with expression for all genes in `genes`.
        """

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

    @classmethod
    def get_expressing_samples_in_conditions(cls, experiment, ctype, conditions, genes):
        """
        Returns dictionary with sample ids (from conditions) and the genes each one
        of them express.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            ctype (`ConditionType`): Condition type name.
            conditions (`list` of `str`): Condition names from which to retrieve 
                samples.
            genes (`list` of `str`): List of gene symbols for which we want to know 
                if samples in `conditions` express or not.
        
        Returns:
            `dict` of `list`: Dictionary with sample ids as keys, and a list of 
                gene symbols as values. Each sample will point to a list of genes that they
                express.
        """

        sql = """
            SELECT NetExplorer_expressionabsolute.sample_id, 
                   gene_symbol, 
                   NetExplorer_condition.name, 
                   NetExplorer_samplecondition.condition_id 
            FROM NetExplorer_expressionabsolute 
            INNER JOIN NetExplorer_samplecondition ON `NetExplorer_samplecondition`.`sample_id` = `NetExplorer_expressionabsolute`.`sample_id` 
            INNER JOIN NetExplorer_condition ON NetExplorer_condition.id = NetExplorer_samplecondition.condition_id 
            WHERE NetExplorer_expressionabsolute.experiment_id=%s 
            AND NetExplorer_condition.cond_type_id = %s 
            AND gene_symbol IN (%s)
            AND NetExplorer_condition.name IN (%s);
        """ % (experiment.id, ctype.id, ', '.join([ "'%s'" % gene for gene in genes ]), ', '.join([ "'%s'" % condition for condition in conditions ]))
        cursor = connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        genes_in_sample = defaultdict(list)
        
        for row in data:
            genes_in_sample[row[0]].append(row[1])
        return genes_in_sample
        




# ------------------------------------------------------------------------------
class ExpressionCondition(models.Model):
    """
    Table that stores the sum of expression values in a particular condition.
    Note that we store the sum, and not the mean, because the 0 values of expression 
    are not stored in ExpressionAbsolute, and thus can't be computed without taking into 
    account the number of samples in each condition separately.

    Attributes:
        experiment: Foreign Key to Experiment.
        gene_symbol: Gene symbol.
        condition: Foreign Key to Condition.
        sum_expression: The sum of expression values for gene_symbol in all 
            samples that belong to condition.

    To create it:

    .. code-block:: sql

        CREATE TABLE NetExplorer_expressioncondition
        SELECT `NetExplorer_expressionabsolute`.`experiment_id`,
            `NetExplorer_samplecondition`.`condition_id`, 
            `NetExplorer_expressionabsolute`.`gene_symbol`,   
                SUM(`NetExplorer_expressionabsolute`.`expression_value`) AS sum_expression
        FROM  `NetExplorer_expressionabsolute`
        INNER JOIN NetExplorer_samplecondition ON NetExplorer_expressionabsolute.sample_id = NetExplorer_samplecondition.sample_id
        GROUP BY `NetExplorer_samplecondition`.`condition_id`, 
                `NetExplorer_expressionabsolute`.`gene_symbol`, 
                `NetExplorer_expressionabsolute`.`experiment_id`;

    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    gene_symbol = models.CharField(max_length=50)
    condition =  models.ForeignKey(Condition, on_delete=models.CASCADE)
    sum_expression = models.FloatField()

    @classmethod
    def get_condition_expression(cls, experiment, dataset, conditions, ctype, genes):
        """Method for getting gene expression in a set of conditions.

        Args:
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
        
        Returns:
            `dict`: Dictionary with expression for each condition.
                Key is gene symbol (`str`), value is vector of expression in each condition (`list` of `float`), 
                in the same order as `conditions`.
        """

        condition_expression = dict()
        sc_dict = Condition.get_samples_per_condition(experiment, ctype)    

        cexpression = cls.objects.filter(
            experiment=experiment,
            gene_symbol__in=genes
        ).values('gene_symbol', 'condition', 'sum_expression')

        datadict = defaultdict(lambda: defaultdict(float))
        for row in cexpression:
            datadict[ row['condition'] ][ row['gene_symbol'] ] = row[ 'sum_expression' ]

        for condition in conditions:
            cid = condition.id
            samples_in_condition = sc_dict[condition.id]
            if cid  in datadict:
                for gene in genes:
                    if gene not in condition_expression:
                        condition_expression[gene] = list()

                    if gene in datadict[cid]:
                        condition_expression[gene].append(datadict[cid][gene] / samples_in_condition)
                    else:
                        condition_expression[gene].append(0)
            else:
                for gene in genes:
                    if gene not in condition_expression:
                        condition_expression[gene] = list()
                    condition_expression[gene].append(0)
        return condition_expression


# ------------------------------------------------------------------------------
class CellPlotPosition(models.Model):
    """
    Table with Cell position in a 2-dimensional space,
    usually computed with t-SNE. 

    Attributes:
        experiment: Foreign Key to Experiment.
        sample: Foreign Key to Sample.
        dataset: Foreign Key to Dataset.
        x_position: Float with x-axis coordinate.
        y_position: Float with y-axis coordinate.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    x_position = models.FloatField()
    y_position = models.FloatField()


# ------------------------------------------------------------------------------
class ExpressionRelative(models.Model):
    """
    Table for storing comparisons of expression between two conditions.
    Only stores significant results.

    Attributes:
        experiment: Foreign Key to Experiment.
        condition1: Foreign Key to Condition.
        condition2: Foreign Key to Condition.
        cond_type: Foreign Key to ConditionType.
        dataset: Foreign Key to Dataset.
        gene_symbol: String with gene symbol.
        fold_change: Float with log2(Fold Change).
        pvalue: Float with adjusted p-value.
    """
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
    """
    Table with genes that appear in a particular experiment.
    Useful for deciding if a gene has expression == 0.
        If gene is in ExperimentGene but not in ExpressionAbsolute: expression == 0.
        If gene is not in ExperimentGene: expression == "NA"

    Attributes:
        experiment: Foreign Key to Experiment.
        gene_symbol: String with gene symbol.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    gene_symbol =  models.CharField(max_length=50)

    def __str__(self):
        name_str = self.experiment.name + " - "
        name_str += self.gene_symbol
        return name_str


# ------------------------------------------------------------------------------
class RegulatoryLinks(models.Model):
    """
    Class for regulatory links predicted for a SingleCell Experiment.

    Attributes:
        experiment: Foreign Key to Experiment.
        dataset: Foreign Key to Dataset.
        group: Integer from 1 to 10 that indicates to which group of 
            links it belongs to, ordered from best (1) to worse (10). 
            Each group has 100 links.
        regulator: Gene symbol of the regulator gene.
        target: Gene symbol of the target gene.
        source: String indicating if the regulator was selected by 
            PFAM domain or by GO term.
        score: Score of the regulatory link as reported by GENIE3.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    group = models.IntegerField(max_length=10, default=1)
    regulator = models.CharField(max_length=50)
    target = models.CharField(max_length=50)
    source = models.CharField(max_length=20)
    score = models.FloatField()


# ------------------------------------------------------------------------------
class ClusterMarkers(models.Model):
    """
    Class for cluster marker genes.

    Attributes:
        experiment: Foreign Key to Experiment.
        dataset: Foreign Key to Dataset.
        condition: Foreign Key to Condition.
        gene_symbol: String with gene symbol.
        auc: Area under the curve of the marker used as a classifier.
        avg_diff: Average difference in expression of the marker between this condition 
            and all the others.
    """
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    gene_symbol = models.CharField(max_length=50)
    auc = models.FloatField()
    avg_diff = models.FloatField()



