from .common import *


COLORS = [
    '#1f77b4',  
    '#ff7f0e',  
    '#2ca02c',  
    '#d62728',  
    '#9467bd',  
    '#8c564b',  
    '#e377c2',  
    '#7f7f7f',  
    '#bcbd22',  
    '#17becf'
]


class PlotCreator(object):
    """
    Class that handles the creation of plots for PlanExp.
    """

    def __init__(self):
        pass

    def __create_violin(self, **kwargs):
        """
        Creates a violin plot.

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`ViolinPlot`: Violin plot instance.
        """
        plot = ViolinPlot()
        condition_list = list()

        sample_expression, gene_conditions = ExpressionAbsolute.get_sample_expression(
            kwargs['experiment'],
            kwargs['dataset'], 
            kwargs['conditions'], 
            kwargs['genes'],
            only_expressed=kwargs['only_toggle']
        )

        if not kwargs['only_toggle']:
            for condition in kwargs['conditions']:
                samples = SampleCondition.objects.filter(
                    experiment=kwargs['experiment'], 
                    condition=condition
                ).values_list('sample', flat=True)
                condition_list.extend([ condition.name for sample in samples ])

        for gene in kwargs['genes']:
            # Single Factor. Simple Line Chart.
            plot.traces.append(PlotlyTrace(name=gene))
            if not kwargs['only_toggle']:
                plot.traces[-1].x = condition_list
            else:
                plot.traces[-1].x = gene_conditions[gene]
            plot.traces[-1].y = sample_expression[gene]
            plot.traces[-1].type = "violin"
        
        return plot

    
    def __create_heatmap(self, **kwargs):
        """
        Creates a heatmap plot.

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`HeatmapPlot`: Heatmap plot instance.
        """

        plot = HeatmapPlot()

        if kwargs['ctype'] != "Samples":
            # Each column corresponds to a condition
            condition_expression = ExpressionCondition.get_condition_expression(
                kwargs['experiment'], 
                kwargs['dataset'], 
                kwargs['conditions'], 
                kwargs['ctype'],
                kwargs['genes']
            )
            plot.add_conditions(kwargs['conditions'])
        else:
            # Each column corresponds to a sample
            condition_expression, gene_conditions = ExpressionAbsolute.get_sample_expression(
                kwargs['experiment'], 
                kwargs['dataset'], 
                kwargs['conditions'], 
                kwargs['genes']
            )
            all_samples = list()
            for condition in kwargs['conditions']:
                samples = SampleCondition.objects.filter(
                    experiment=kwargs['experiment'], 
                    condition=condition
                ).order_by('sample').values_list('sample', flat=True)
                all_samples.extend([ condition.name + " - " + str(i) for i in range(len(list(samples))) ])
            plot.add_conditions(all_samples)

        for gene in kwargs['genes']:
            plot.add_gene(gene)
            plot.add_gene_expression(condition_expression[gene]) 
        
        return plot


    def __create_linechart(self, **kwargs):
        """
        Creates a linechart plot.

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`LinePlot`: Line chart plot instance.
        """

        plot = LinePlot()

        condition_expression = ExpressionCondition.get_condition_expression(
            kwargs['experiment'], 
            kwargs['dataset'], 
            kwargs['conditions'], 
            kwargs['ctype'],
            kwargs['genes']
        )

        conditions = [ condition.name for condition in kwargs['conditions'] ]
        group_idxs = dict()
        time_idxs = list()
        if " - " in conditions[0]:
            # Interaction Factor. Multiple Subplots.
            for c_idx, condition in enumerate(conditions):
                c1, c2 = condition.split(" - ")
                if c1 not in set(time_idxs):
                    time_idxs.append(c1)
                if c2 not in group_idxs:
                    group_idxs[c2] = list()
                group_idxs[c2].append(c_idx)
        
        if not group_idxs:
            for gene in kwargs['genes']:
                # Single Factor. Simple Line Chart.
                plot.traces.append(PlotlyTrace(name=gene))
                plot.traces[-1].x = conditions
                plot.traces[-1].y = condition_expression[gene]
                plot.traces[-1].type = "scatter"
        else:
            # Interaction Factor. Multiple Subplots.
            subplot_i = 1
            for group_name, group_i in group_idxs.items():
                for gene in kwargs['genes']:
                    plot.traces.append(PlotlyTrace(name=gene))
                    plot.traces[-1].x = time_idxs
                    plot.traces[-1].y = [ condition_expression[gene][i] for i in group_i ]
                    plot.traces[-1].xaxis = "x" + str(subplot_i)
                    plot.traces[-1].yaxis = "y" + str(subplot_i)
                    plot.traces[-1].type = "scatter"
                    plot.traces[-1].subplot_title = group_name
                    plot.traces[-1].legend_group = gene
                subplot_i += 1
        return plot
    

    def __create_bar(self, **kwargs):
        """
        Creates a bar plot.

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`BarPlot`: Bar plot instance.
        """

        plot = BarPlot()
        condition_expression = ExpressionCondition.get_condition_expression(
            kwargs['experiment'], 
            kwargs['dataset'], 
            kwargs['conditions'], 
            kwargs['ctype'],
            kwargs['genes']
        )

        for gene in kwargs['genes']:
            # Single Factor. Simple Line Chart.
            plot.traces.append(PlotlyTrace(name=gene))
            plot.traces[-1].x = [ condition.name for condition in kwargs['conditions'] ]
            plot.traces[-1].y = condition_expression[gene]
            plot.traces[-1].type = "bar"
        return plot
    
    
    def __create_coexpression(self, **kwargs):
        """
        Creates a co-expression plot, a plot where x and y axis are expression values 
        for two genes, and each point is a cell.

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`ScatterPlot`: ScatterPlot plot instance with co-expression plot.
        """


        plot = ScatterPlot()
        sample_expression, gene_conditions = ExpressionAbsolute.get_sample_expression(
            kwargs['experiment'], 
            kwargs['dataset'], 
            kwargs['conditions'], 
            kwargs['genes']
        )
        
        # Add first condition to done_condition
        done_condition = set()
        plot.xlab = kwargs['genes'][0]
        plot.ylab = kwargs['genes'][1]
        for idx, condition in enumerate(gene_conditions[ kwargs['genes'][0] ]):
            if condition not in done_condition:
                plot.traces.append(PlotlyTrace(name=condition))
                plot.traces[-1].type = "scattergl"
                done_condition.add(condition)
            plot.traces[-1].x.append(sample_expression[ kwargs['genes'][0] ][idx])
            plot.traces[-1].y.append(sample_expression[ kwargs['genes'][1] ][idx])
        return plot


    def __create_tsne_simple(self, genes, cell_positions, sample_names, sample_condition, sample_expression):
        """
        Creates a t-SNE plot with one (or none) gene expression mapped onto it.

        Args:
            genes (`list` of `str`): List of gene symbols.
            cell_positions (`dict`): Dictionary with cell positions in t-SNE space. 
                Key is cell/sample name, value is tuple with (x, y) positions (float, float).
            sample_names (`list` of `str`): List of sample names.
            sample_condition (`dict`): Dictionary with sample-condition relationships. 
                Key is cell/sample name, value is condition identifier (int).
            sample_expression (`dict`):  Key is gene symbol (`str`), value is vector of 
                expression in each sample (`list` of `float`), sorted by condition. 
        
        Warning:
            `sample_expression` values have to be in the same order as `sample_names`! 
            We sort them by sample identifier using `order('sample')` in Django models.

        Returns:
            :obj:`ScatterPlot`: ScatterPlot plot instance.
        """

        plot = ScatterPlot()
        done_condition = set()
        for idx, sample_name in enumerate(sample_names):
            condition = sample_condition[sample_name]
            if condition not in done_condition:
                plot.traces.append(PlotlyTrace(name=condition))
                plot.traces[-1] = PlotlyTrace(name=condition)
                plot.traces[-1].type = "scattergl"
                done_condition.add(condition) 
            plot.traces[-1].x.append(cell_positions[sample_name][0])
            plot.traces[-1].y.append(cell_positions[sample_name][1])
            plot.traces[-1].names.append(sample_name)
            if sample_expression:
                # We also wanto to store gene expression as color
                plot.traces[-1].color.append(sample_expression[genes[0]][idx])
        return plot


    def __create_tsne_multiple(self, cell_positions, sample_names, sample_condition, sample_mean_expression):
        """
        Creates a t-SNE plot withmore than one gene expression mapped onto it.

        Args:
            genes (`list` of `str`): List of gene symbols.
            cell_positions (`dict`): Dictionary with cell positions in t-SNE space. 
                Key is cell/sample name, value is tuple with (x, y) positions (float, float).
            sample_names (`list` of `str`): List of sample names.
            sample_condition (`dict`): Dictionary with sample-condition relationships. 
                Key is cell/sample name, value is condition identifier (int).
            sample_mean_expression (`dict`): Dictionary with mean expession for condition.
                Key is sample name (`str`), value is mean expression (`float`) 
                for each gene in `genes` in that cell.

        Returns:
            :obj:`ScatterPlot`: ScatterPlot plot instance.
        """

        plot = ScatterPlot()
        done_condition = set()
        for sample_name in sample_names:
            condition = sample_condition[sample_name]
            if sample_name in sample_mean_expression:
                if condition not in done_condition:
                    plot.traces.append(PlotlyTrace(name=condition))
                    plot.traces[-1] = PlotlyTrace(name=condition)
                    plot.traces[-1].type = "scattergl"
                    done_condition.add(condition)
                plot.traces[-1].x.append(cell_positions[sample_name][0])
                plot.traces[-1].y.append(cell_positions[sample_name][1])
                plot.traces[-1].names.append(sample_name)
                plot.traces[-1].color.append(sample_mean_expression[sample_name])

        return plot


    def __create_tsne(self, **kwargs):
        """
        Creates either a simple t-SNE (zero or one gene) or a multiple t-SNE (>1 gene).

        Args:
            **kwargs: Arbitrary keyword arguments passed from create_plot.

        Returns:
            :obj:`ScatterPlot`: Scatter plot t-SNE visualization.
        """

        # Get cell positions
        cell_positions = CellPlotPosition.objects.filter(
            experiment=kwargs['experiment'], 
            dataset=kwargs['dataset']
        ).select_related('sample').values('sample__sample_name', 'x_position', 'y_position')

        cell_positions = { cell['sample__sample_name'] : (cell['x_position'], cell['y_position']) for cell in cell_positions }
        
        sample_names = list()
        sample_condition = dict()
        for condition in kwargs['conditions']:
            samples = SampleCondition.objects.filter(
                experiment=kwargs['experiment'], 
                condition=condition
            ).order_by('sample').values_list('sample__sample_name', flat=True)
            
            sample_names.extend(samples)
            for sample_name in samples:
                sample_condition[sample_name] = condition.name

        if len(kwargs['genes']) < 2:
            if len(kwargs['genes']) > 0:
                sample_expression, gene_conditions = ExpressionAbsolute.get_sample_expression(
                    kwargs['experiment'],
                    kwargs['dataset'],
                    kwargs['conditions'],
                    kwargs['genes'])
            else:
                sample_expression, gene_conditions = None, None
            plot = self.__create_tsne_simple(
                kwargs['genes'], 
                cell_positions, 
                sample_names, 
                sample_condition, 
                sample_expression)
        else:
            sample_mean_expression = ExpressionAbsolute.get_mean_expression(
                kwargs['experiment'],
                kwargs['dataset'],
                kwargs['conditions'],
                kwargs['genes'])
            plot = self.__create_tsne_multiple(
                cell_positions, 
                sample_names, 
                sample_condition, 
                sample_mean_expression)
        plot.compute_color_limits()
        return plot


    def create_plot(self, plot_name, **kwargs):
        """Method for creating plots.

        Args:
            plot_name (str): Name of the plot. 
                Can be (`violin`, `tsne`, `coexpression`, `bar`, `heatmap` or `line`)
            experiment (str): Experiment in PlanExp.
            dataset (str): Dataset in PlanExp.
            conditions (`list` of `Condition`): Conditions (previously sorted) to use 
                for the plot.
            genes (`list` of `str`): Genes to plot. Can be empty depending on the plot.
            ctype (str): Condition type of `conditions`.
            only_toggle (bool, optional): Plot only samples with expression > 0. Used only
                for plot `violin`.
        
        Returns:
            plot (`GeneExpPlot`): Can be of subclass (`ViolinPlot`, `ScatterPlot`, 
                `BarPlot`, `HeatmapPlot`, or `LinePlot`).

        """
        required_args = ['experiment', 'dataset', 'conditions', 'genes', 'ctype']
        for req_arg in required_args:
            try:
                assert(req_arg in kwargs)
            except AssertionError:
                raise TypeError("create_plot() required arguments: %s" % ", ".join(required_args))

        if plot_name == "violin":
            plot = self.__create_violin(**kwargs)
        elif plot_name == "heatmap":
            plot = self.__create_heatmap(**kwargs)
        elif plot_name == "line":
            plot = self.__create_linechart(**kwargs)
        elif plot_name == "bar":
            plot = self.__create_bar(**kwargs)
        elif plot_name == "coexpression":
            plot = self.__create_coexpression(**kwargs)
        elif plot_name == "tsne":
            plot = self.__create_tsne(**kwargs)
        else:
            raise ValueError("Incorrect plot_name: %s - Plot name must be 'violin', 'tsne', coexpression', 'bar', heatmap' or 'line'." % str(plot_name))
        
        return plot


# ------------------------------------------------------------------------------
class GeneExpPlot(object):
    """
    Parent class for Plotly barplots and violins.
    
    Attributes:
        traces (`list` of :obj:`PlotlyTrace`): List of plotly traces that define 
            the data to be plotted.
        title (`str`): Title for plot.
        xlab(`str`): Label for plot x-axis.
        ylab(`str`): Label for plot y-axis.
        trace_names (`list` of `str`): Name for traces, if any.
    """

    def __init__(self):
        self.traces = list()
        self.title = str()
        self.xlab = str()
        self.ylab = str()
        self.trace_names = list()
     
    def is_empty(self):
        """
        Checks if plot is empty by looking at its traces.

        Returns:
            bool: True if empty, False otherwise.
        """

        if self.traces:
            if self.traces[0].x and self.traces[0].y:
                return False
            else:
                return True
        else:
            return True
    
    def plot(self):
        """
        Method to be provided by child classes to convert plot to JSON string for 
        plotting.
        """
        raise NotImplementedError("GeneExpPlot is a parent class and cannot be plotted!")


# ------------------------------------------------------------------------------
class BarPlot(GeneExpPlot):
    """
    Class for Plotly bar plots where each bar (group) consists of only one value. 
    Inherits from GenExpPlot.
    """
    def __init__(self):
        super(BarPlot, self).__init__()

    def plot(self):
        """
        Converts plot to a JSON string ready to be drawn by Plotly.js.

        Returns:
            str: JSON string with plot data for Plotly.js.
        """

        theplot = dict()
        theplot['data'] = list()
        theplot['layout'] = dict()
        data_list = list()

        for trace in self.traces:
             trace_dict = { 'x': trace.x, 'y':trace.y, 'type': trace.type, 'name': trace.name }
             data_list.append(trace_dict)
        
        if len(self.traces) > 1:
            theplot['layout']['barmode'] = "group"
        
        if self.title:
            theplot['layout']['title'] = self.title
        theplot['data'] = data_list

        return theplot


# ------------------------------------------------------------------------------
class ViolinPlot(GeneExpPlot):
    """
    Class for Plotly violinplots. Each violin (group) is made of multiple values. 
    Inherits from GenExpPlot.
    """

    def __init__(self):
        super(ViolinPlot, self).__init__()

    def jitter_and_round(self, values, jitter=0.01):
        """
        Jitters the y-values of the Violin plot so that Plotly can plot them 
        because Plotly.js is buggy as hell, and if the standard deviation is 
        equal to zero it will REFUSE to plot the violin.

        Args:
            values (`list` of `float`): Values to be jittered.
            jitter (`float`): How much to jitter the y-values. 
        """

        newvalues = list()
        for idx, value in enumerate(values):
            value = round(value, 3)
            if idx % 2 == 0:
                newvalues.append(value + jitter)
            else:
                newvalues.append(value - jitter)
        return newvalues

    def plot(self):
        """
        Converts plot to a JSON string ready to be drawn by Plotly.js.

        Returns:
            str: JSON string with plot data for Plotly.js.
        """
        theplot = dict()
        theplot['data'] = list()
        theplot['layout'] = dict()
        data_list = list()

        for trace in self.traces:
            trace_dict = { 
                 'x': trace.x, 
                 'y': self.jitter_and_round(trace.y), 
                 'type': trace.type, 
                 'name': trace.name 
            }
            data_list.append(trace_dict)
        
        if len(self.traces) > 1:
            theplot['layout']['violinmode'] = "group"
        
        theplot['data'] = data_list

        return theplot


class HeatmapPlot(object):
    """
    Class for plotly Heatmaps. They are not GeneExpPlot because they function 
    very differently.

    Attributes:
        x (`list` of `str`): x-values for data (condition names).
        y (`list` of `str`): y-values for data (gene names).
        z (`list` of `list`): z-values for data (expression that will be 
            mapped to color). Each element of `z` corresponds to a list 
            with expression values for one gene. `z` is a 2-D matrix where 
            rows are genes (same order as `y`) and columns are conditions (same 
            order as `x`).
        type (`str`): Defines type for Plotly ("heatmap").

    Warning:
        add_gene and add_gene_expression should be used syncronously. Each time 
        a gene is added, all gene_expressions will be added for THAT gene. 
        Those should be added in the same order as the provided conditions in the 
        `add_condition` call previously. See the example for more information.
    
    Example:

        .. code-block:: python

            # Data to be added
            genes = ["A", "B"]
            expressions = [
                [2.5, 3.5, 4.5], # for A
                [1, 3, 1] # for B
            ]
            conditions = ["c1", "c2", "c3"]
            
            # Initialize the plot
            the_plot = HeatMapPlot()
            theplot.add_conditions(conditions)
            
            # Add genes and expression
            for gene, expression in zip(genes, expressions):
                theplot.add_gene(gene)
                theplot.add_gene_expression(expression)

    """

    def __init__(self):
        self.x = list()
        self.y = list()
        self.z = list()
        self.type = "heatmap"
    
    def add_conditions(self, conditions):
        """
        Adds conditions to x-axis.

        Args:
            conditions (`list` of :obj:`Condition` or `str`): Conditions to be added.
        """
        try:
            self.x = [ cond.name for cond in list(conditions) ]
        except:
            self.x = [ cond for cond in conditions ]

    def add_gene(self, gene_symbol):
        """
        Adds gene symbol to y-axis.
        
        Args:
            gene_symbol (`str`): Gene symbol to be added to y-axis.
        """
        self.y.append(gene_symbol)

    def add_gene_expression(self, expression):
        """
        Adds gene expression to z-axis.

        Args:
            expression (`float`): Expression value to be added to the LAST gene.

        """
        self.z.append(expression)

    def is_empty(self):
        """
        Checks if plot is empty by looking at its traces.

        Returns:
            bool: True if empty, False otherwise.
        """
        if self.x and self.y and self.z:
            return False
        else:
            return True
    
    def plot(self):
        """
        Converts plot to a JSON string ready to be drawn by Plotly.js.

        Returns:
            str: JSON string with plot data for Plotly.js.
        """
        theplot = dict()
        theplot['data'] = list()

        theplot['layout'] = {
            'margin': {
                'l': 250,
                'r': 20,
                'b': 150,
                't': 20,
                'pad': 4
        }}

        data_dict = dict()
        data_dict['x'] = self.x
        data_dict['y'] = self.y
        data_dict['z'] = self.z
        data_dict['type'] = "heatmap"
        theplot['data'].append(data_dict)
        return theplot


class LinePlot(GeneExpPlot):
    """
    Class for Plotly linecharts. Inherits from GenExpPlot.

    Attributes:
        type (`str`): Type for Plotlyjs (scattergl).
    """
    def __init__(self):
        super(LinePlot, self).__init__()
        self.type = "scattergl"


    def plot(self):
        """
        Converts plot to a JSON string ready to be drawn by Plotly.js.

        Returns:
            str: JSON string with plot data for Plotly.js.
        """
        theplot = dict()
        theplot['data'] = list()

        theplot['layout'] = {
            'margin': {
                'l': 250,
                'r': 20,
                'b': 150,
                't': 20,
                'pad': 4
        }}

        data_list = list()
        num_subplots = set()
        subplots = set()
        annotations = list()
        i_colors = 0
        added_genes = dict()
        max_expression = max([ max(trace.y) for trace in self.traces ])

        for trace in self.traces:
            trace_dict = { 'x': trace.x, 'y': trace.y, 'type': trace.type, 'name': trace.name }
            if trace.xaxis is not None:
                trace_dict['xaxis'] = trace.xaxis
                trace_dict['yaxis'] = trace.yaxis
                num_subplots.add(trace.xaxis)
                if trace.subplot_title not in subplots:
                    subplots.add(trace.subplot_title)
                    annotations.append({
                        'text': trace.subplot_title, 
                        'align': 'center',
                        'showarrow': False,
                        'xref': trace.xaxis,
                        'yref': trace.yaxis,
                        'y': max_expression
                    })
                if trace.name not in added_genes:
                    if i_colors >= 10:
                        i_colors = 0
                    added_genes[trace.name] = COLORS[i_colors]
                    i_colors += 1
                trace_dict['line'] = dict()
                trace_dict['line']['color'] = added_genes[trace.name]
                if trace.xaxis != "x1":
                    trace_dict['showlegend'] = False
                trace_dict['legendgroup'] = trace.legend_group    
            data_list.append(trace_dict)
        

        num_subplots = len(num_subplots)
        if num_subplots:
            theplot['layout']['grid'] = { 'rows': num_subplots, 'columns': 1, 'pattern': 'independent', 'roworder': 'top to bottom'}
            theplot['layout']['height'] = 300 * num_subplots
            theplot['layout']['annotations'] = annotations
        theplot['data'] = data_list
        return theplot


class ScatterPlot(GeneExpPlot):
    """
    Class for scatter plots. Inherits from GenExpPlot.

    Attributes:
        type (`str`): Type for Plotlyjs (scattergl).
        cmax (`float`): Maximum value to compute color gradient. Defaults to None.
        cmin (int): Minimum value to compute color gradient. Defaults to 0.
    """
    def __init__(self):
        super(ScatterPlot, self).__init__()
        self.type = "scattergl"
        self.cmax = None
        self.cmin = 0
    
    def plot(self):
        """
        Converts plot to a JSON string ready to be drawn by Plotly.js.

        Returns:
            str: JSON string with plot data for Plotly.js.
        """
        theplot = dict()
        theplot['data'] = list()
        theplot['layout'] = dict()
        
        if self.cmax is None:
            self.compute_color_limits()

        for trace in self.traces:
            trace_dict = { 
                'x': trace.x, 'y': trace.y, 
                'type': trace.type, 'name': trace.name, 
                'mode': 'markers' 
            }
            if trace.names:
                trace_dict['text'] = trace.names
            if trace.color:
                trace_dict['marker'] = { 'color': list(trace.color), 'cmin': self.cmin, 'cmax': self.cmax }
                trace_dict['color'] = trace.color
            theplot['data'].append(trace_dict)
            
        if self.xlab:
            theplot['layout']['xaxis'] = dict()
            theplot['layout']['xaxis']['title'] = self.xlab
        
        if self.ylab:
            theplot['layout']['yaxis'] = dict()
            theplot['layout']['yaxis']['title'] = self.ylab
        
        return theplot
    
    def compute_color_limits(self):
        """
        Computes color limits according to stored trace values and fills `cmax` 
        attribute.

        Raises:
            EmptyPlotError: raised when no values are found in traces.
        """
        self.cmax = 0
        try:
            for trace in self.traces:
                max_in_trace = max(trace.color)
                if max_in_trace > self.cmax:
                    self.cmax = max_in_trace
        except:
            return
        

class PlotlyTrace(object):
    """
    Class for plotly traces.

    Attributes:
        name (str): 
    """
    def __init__(self, name):
        self.name = name
        self.order = int()
        self.x = list()
        self.y = list()
        self.names = list()
        self.mode = 'markers'
        self.type = 'scattergl'
        self.color = list()
        self.xaxis = None
        self.yaxis = None
        self.subplot_title = None
        self.legend_group = None



class VolcanoPlot(object):
    """
    Class for Plotly volcano scatterplots. Legacy code that should be converted 
    to ScatterPlot at some point.
            var data = [
        {
            z: [[1, 20, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
            x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            y: ['Morning', 'Afternoon', 'Evening'],
            type: 'heatmap'
        }
        ];


        Plotly.newPlot('myDiv', data);
    """
    def __init__(self):
        self.traces = dict()
        self.limits = { 'x': list(), 'y': list()}
        self.units = dict()
        self.cmin = 0
        self.cmax = None
    
    def add_trace(self, name):
        if name not in self.traces:
            self.traces[name] = PlotlyTrace(name)
            self.traces[name].order = len(self.traces)
    
    def add_x(self, trace_name, x):
        if trace_name in self.traces:
            self.traces[trace_name].x.append(x)
        else:
            raise(KeyError("Trace %s not found in ScatterPlot!" % trace_name))

    def add_y(self, trace_name, y):
        if trace_name in self.traces:
            self.traces[trace_name].y.append(y)
    
    def add_name(self, trace_name, name):
        if trace_name in self.traces:
            self.traces[trace_name].names.append(name)

    def set_limits(self, axis, start, end):
        if axis == 'x' or axis == 'y':
            self.limits[axis] =[start, end]
        else:
            raise ValueError("Axis should be 'x' or 'y'.")

    def plot(self):
        theplot = dict()
        theplot['data'] = list()
        theplot['layout'] = dict()
        for trace_name in sorted(self.traces.keys(), key=lambda n: self.traces[n].order):
            trace = self.traces[trace_name]
            trace_data = dict()
            if str(trace_name).isdigit():
                trace_data['name'] = 'Cluster ' + str(trace.name)
            else:
                trace_data['name'] = str(trace.name)
            trace_data['x'] = trace.x
            trace_data['y'] = trace.y
            trace_data['type'] = trace.type
            trace_data['mode'] = trace.mode
            if trace.color:
                trace_data['marker'] = { 'color': list(trace.color), 'cmin': self.cmin, 'cmax': self.cmax }
            if trace.names:
                trace_data['text'] = trace.names
            theplot['data'].append(trace_data)
        theplot['layout'] = {'xaxis': dict(), 'yaxis': dict()}
        if self.units:
            for axis, units in self.units.items():
                axis_name = axis + 'axis'
                theplot['layout'][axis_name]['title'] = units
        
        return theplot
    
    def add_color_to_trace(self, trace_name, colors):
        if trace_name in self.traces:
            self.traces[trace_name].color = colors
            maxc = max(colors)
            if self.cmax is None:
                self.cmax = maxc
            if maxc > self.cmax:
                self.cmax = maxc
        else:
            raise(KeyError("Trace %s not found in ScatterPlot!" % trace_name))

    def add_units(self, axis, units):
        """
        Adds units to one axis of the plot.

        Args:
            axis: string cointaining 'x' or 'y'.
            units: string for units.
        
        Returns:
            nothing
        """
        if axis == 'x' or axis == 'y':
            self.units[axis] = units
        else:
            raise ValueError("Axis should be a string containing 'x' or 'y'.")





