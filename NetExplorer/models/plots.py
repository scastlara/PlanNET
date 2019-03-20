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
    
    def __init__(self):
        '''Class that handles the creation of plots for PlanExp.

        Attributes:
            None
        
        '''
        pass

    def __create_violin(self, **kwargs):
        '''

        '''
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
        plot = HeatmapPlot()

        if kwargs['ctype'] != "Samples":
            # Each column corresponds to a condition
            condition_expression = ExpressionAbsolute.get_condition_expression(
                kwargs['experiment'], 
                kwargs['dataset'], 
                kwargs['conditions'], 
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
        plot = LinePlot()

        condition_expression = ExpressionAbsolute.get_condition_expression(
            kwargs['experiment'], 
            kwargs['dataset'], 
            kwargs['conditions'], 
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
        plot = BarPlot()
        condition_expression = ExpressionAbsolute.get_condition_expression(
            kwargs['experiment'], 
            kwargs['dataset'], 
            kwargs['conditions'], 
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
        plot = NewScatterPlot()
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
        plot = NewScatterPlot()
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
        plot = NewScatterPlot()
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
            sample_expression, gene_conditions = ExpressionAbsolute.get_sample_expression(
                kwargs['experiment'],
                kwargs['dataset'],
                kwargs['conditions'],
                kwargs['genes'])
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
            print(sample_mean_expression)
            plot = self.__create_tsne_multiple(
                cell_positions, 
                sample_names, 
                sample_condition, 
                sample_mean_expression)
        plot.compute_color_limits()
        return plot


    def create_plot(self, plot_name, **kwargs):
        '''Method for creating plots.

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
            plot (`GenExpPlot`): Can be of subclass (`ViolinPlot`, `ScatterPlot`, 
                `BarPlot`, `HeatmapPlot`, or `LinePlot`).

        '''
        required_args = ['experiment', 'dataset', 'conditions', 'genes', 'ctype']
        for req_arg in required_args:
            try:
                assert(req_arg in kwargs)
            except AssertionError:
                raise TypeError("crate_plot() required arguments: %s" % ", ".join(required_args))

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
class GenExpPlot(object):
    """
    Class for Plotly barplots and violins.
    traces = [
        0 : {
            group1: [ values ],
            group2: [ values ],
            ...
        },
        1 :
            ...
    ]
    """
    def __init__(self):
        self.traces = list()
        self.traces_set = set()
        self.groups = list()
        self.groups_set = set()
        self.title = str()
        self.ylab = str()
        self.xlab = str()
        self.trace_names = list()
     

    def is_empty(self):
        if self.traces[0].x and self.traces[0].y:
            return False
        else:
            return True




# ------------------------------------------------------------------------------
class BarPlot(GenExpPlot):
    """
    Class for Plotly bar plots.
    Each bar (group) consists of only one value.
    """
    def __init__(self):
        super(BarPlot, self).__init__()

    def plot(self):
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
class ViolinPlot(GenExpPlot):
    """
    Class for Plotly violinplots.
    Each violin (group) is made of multiple values.
    Class for Plotly barplots.
    traces = [
        0 : {
            group1: [ values ],
            group2: [ values ],
            ...
        },
        1 :
            ...
    ]
    """
    def __init__(self):
        super(ViolinPlot, self).__init__()
    

    def jitter_and_round(self, values, jitter=0.01):
        newvalues = list()
        for idx, value in enumerate(values):
            value = round(value, 3)
            if idx % 2 == 0:
                newvalues.append(value + jitter)
            else:
                newvalues.append(value - jitter)
        return newvalues

    def is_empty(self):
        if self.traces[0].x and self.traces[0].y:
            return False
        else:
            return True


    def plot(self):
        theplot = dict()
        theplot['data'] = list()
        theplot['layout'] = dict()
        data_list = list()

        for trace in self.traces:
             trace_dict = { 'x': trace.x, 'y': self.jitter_and_round(trace.y), 'type': trace.type, 'name': trace.name }
             data_list.append(trace_dict)
        
        if len(self.traces) > 1:
            theplot['layout']['violinmode'] = "group"
        
        theplot['data'] = data_list

        return theplot


class HeatmapPlot(object):
    '''
    Class for plotly Heatmaps

        y: genes
        x: clusters
        z: expression mean
        
    '''
    def __init__(self):
        self.x = list()
        self.y = list()
        self.z = list()
        self.type = "heatmap"
    
    def add_conditions(self, conditions):
        try:
            self.x = [ cond.name for cond in list(conditions) ]
        except:
            self.x = [ cond for cond in conditions ]

    def add_gene(self, gene_symbol):
        self.y.append(gene_symbol)

    def add_gene_expression(self, expression):
        self.z.append(expression)

    def is_empty(self):
        if self.x and self.y and self.z:
            return False
        else:
            return True
    
    def plot(self):
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


class LinePlot(GenExpPlot):
    '''
    Class for Plotly linecharts
    '''
    def __init__(self):
        super(LinePlot, self).__init__()
        self.type = "scattergl"


    def plot(self):
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
    
    def is_empty(self):
        
        if self.traces[0].x and self.traces[0].y:
            return False
        else:
            return True


class NewScatterPlot(GenExpPlot):
    def __init__(self):
        super(NewScatterPlot, self).__init__()
        self.type = "scattergl"
        self.cmax = None
        self.cmin = 0
    
    def plot(self):
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
        self.cmax = 0
        try:
            for trace in self.traces:
                max_in_trace = max(trace.color)
                if max_in_trace > self.cmax:
                    self.cmax = max_in_trace
        except:
            return
        


class ScatterPlot(object):
    '''
    Class for Plotly scatterplots
            var data = [
        {
            z: [[1, 20, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
            x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            y: ['Morning', 'Afternoon', 'Evening'],
            type: 'heatmap'
        }
        ];


        Plotly.newPlot('myDiv', data);
    '''
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
        '''
        Adds units to one axis of the plot.

        Args:
            axis: string cointaining 'x' or 'y'.
            units: string for units.
        
        Returns:
            nothing
        '''
        if axis == 'x' or axis == 'y':
            self.units[axis] = units
        else:
            raise ValueError("Axis should be a string containing 'x' or 'y'.")


class PlotlyTrace(object):
    '''
    Class for plotly traces
    '''
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

    



