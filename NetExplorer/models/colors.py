from .common import *

class ColorProfiles(Enum):
    # Linear gradients
    red = list(Color('#fffafa').range_to('#ff0000', 50))
    blue = list(Color('#f7f8ff').range_to('#0029ff', 50))
    green = list(Color('#f9fff9').range_to('#42d242', 50))

    # Divergent gradients
    blue_white = list(Color('#1f77b4').range_to('#f7f8ff', 25)) 
    white_red  = list(Color('#fffafa').range_to("#ff0000", 25))
    blue_red = blue_white[0:-1] + [Color('white')] + white_red[1:25]

    yellow_white = list(Color('#e4a32d').range_to('#fff7ea', 25))
    yellow_blue = yellow_white[0:-1] + [Color('white')] + list(reversed(blue_white))[1:25]

    white_green = list(Color('#f9fff9').range_to('#42d242', 25))
    red_green = list(reversed(white_red))[0:-1] + [Color('white')] + white_green[1:25]

class ColorGenerator(object):
    '''
    Generates a color gradient given a maximum value and a minimum value, using
    min-max normalization in a 0-50 scale.
    Contains color profiles:
        red
        blue
        green
        blue_red
        yellow_blue
        red_green
    '''

    def __init__(self,  max_v, min_v, profile="red"):
        self.profile = ColorProfiles[profile]
        self.max = max_v
        self.min = min_v
    
    def map_color(self, value):
        '''
        Assigns a color to the provided value by using the max and min attributes as
        the scale and normalizing the provided value using min-max normalization.
        
        Returns the hex value of the computed color.
        '''
        thecolor = "#000000"
        if value != "NA":
            normval = int(self.__normalize(value))
            thecolor = str(self.profile.value[normval].hex)
        return thecolor
    
    def __normalize(self, x):
        '''
        Min-Max normalization for normalizing values to 0-50 scale.
        '''
        x = float(x)
        normval = float()
        if x >= self.max:
            normval = float(1)
        elif x <= self.min:
            normval = float(0)
        else:
            normval = (x - self.min) / (self.max - self.min)
        return normval * 49
    
    def __generate_intervals(self):
        '''
        Generates interval values for the gradient.
        '''
        step = ( abs(self.max - self.min) ) / 50
        intervals = [ self.min ]
        while intervals[-1] < self.max:
            intervals.append( round( (intervals[-1] + step), 5) )
        return intervals


    def get_color_legend(self):
        '''
        Returns html of legend for the color gradient
        '''
        html = [ "<div class='grid-container grid-legend-contaiener'></div>" ]
        intervals = list(reversed(self.__generate_intervals()))
        for color_idx, color in enumerate(reversed(self.profile.value)):
            html.append("<div class='grid-item grid-legend info-tooltip' title='%s to %s' style='background-color: %s'> </div>" % (intervals[color_idx + 1], intervals[color_idx], color.hex) )
        html.append("</div>")
        return "\n".join(html)
    

