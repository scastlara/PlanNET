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
        self.title  = str()
        self.ylab   = str()
        self.trace_names = list()
        self.units = dict()

    def add_group(self, group):
        if group not in self.groups_set:
            self.groups.append(group)
            self.groups_set.add(group)
        
        for trace in self.traces:
            if group not in trace:
                trace[group] = list()
        
        if not self.traces:
            self.traces.append(dict())

    def add_value(self, value, group, trace=0):
        if group not in self.traces[trace]:
            self.add_group(group)
        self.traces[trace][group].append(value)

    def add_trace(self, trace_idx):
        self.traces.append(dict())
        # Clone groups from other traces
        for group in self.traces[0].keys():
            self.traces[trace_idx][group] = list()

    def add_trace_name(self, trace_idx, name):
        if len(self.trace_names) <= trace_idx:
            self.trace_names.append(name)
        else:
            self.trace_names[trace_idx] = name

    def add_title(self, title):
        self.title = title

    def add_ylab(self, ylab):
        self.ylab = ylab
    
    def is_empty(self):
        empty = True
        for trace in self.traces:
            for condition, expression in trace.items():
                if sum(expression):
                    empty = False
                    break

        return empty
    
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
        for trace_idx, trace in enumerate(self.traces):
            trace_data = dict()
            x = list()
            y = list()
            if len(self.trace_names) > trace_idx:
                trace_data['name'] = self.trace_names[trace_idx]
            for group in self.groups:
                x.append(group)
                
                y.append(trace[group][0])
            trace_data['x'] = x
            trace_data['y'] = y
            trace_data['type'] = 'bar'
            theplot['data'].append(trace_data)
        theplot['layout'] = dict()
        if len(self.traces) > 1:
            theplot['layout']['barmode'] = "group"
        
        if self.title:
            theplot['layout']['title'] = self.title
        if self.ylab:
            theplot['layout']['yaxis'] = dict()
            theplot['layout']['yaxis']['title'] = self.ylab
        
        if self.units:
            for axis, units in self.units.items():
                axis_name = axis + 'axis'
                theplot['layout'][axis_name] = dict()
                theplot['layout'][axis_name]['title'] = units
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
        
        if self.title:
            theplot['layout']['title'] = self.title
        
        
        theplot['data'] = data_list


        """
        for trace_idx, trace in enumerate(self.traces):
            trace_data = dict()
            trace_data['type'] = 'violin'
            trace_data['box'] = {'visible': True}

            x = list()
            y = list()
            if len(self.trace_names) > trace_idx:
                trace_data['name'] = self.trace_names[trace_idx]
            for group in sorted(self.traces[trace_idx]):
                values = self.traces[trace_idx][group]
                values = self.jitter_and_round(values)
                for value in values:
                    x.append(str(group))
                    y.append(value)

            trace_data['x'] = x
            trace_data['y'] = y
            theplot['data'].append(trace_data)
        theplot['layout'] = dict()
        if len(self.traces) > 1:
            theplot['layout']['violinmode'] = "group"
        if self.title:
            theplot['layout']['title'] = self.title
        if self.ylab:
            theplot['layout']['yaxis'] = dict()
            theplot['layout']['yaxis']['title'] = self.ylab
        if self.units:
            for axis, units in self.units.items():
                axis_name = axis + 'axis'
                theplot['layout'][axis_name] = dict()
                theplot['layout'][axis_name]['title'] = units
        """
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

    



