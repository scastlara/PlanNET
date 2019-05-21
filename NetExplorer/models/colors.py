from .common import *

class ColorProfiles(Enum):
    """
    ColorProfiles enum.
    Stores the following color profiles:
        LINEAR GRADIENTS:
            - red: 50 colors form white to red.
            - blue: 50 colors from white to blue.
            - green: 50 colors from white to blue.
        DIVERGENT GRADIENTS:
            - blue_white: 25 colors from blue to white.
            - white_red: 25 colors from white to red.
            - blue_red: 50 colors from blue to white to red.
            - yellow_white: 25 colors from yellow to white.
            - yellow_blue: 50 colors from yellow to white to blue.
            - white_green: 25 colors from white to green.
            - red_green: 50 colors from red to white to green.
    """
    # Linear gradients
    red = list(Color('#fffafa').range_to('#ff0000', 50))
    blue = list(Color('#f7f8ff').range_to('#0029ff', 50))
    green = list(Color('#f9fff9').range_to('#42d242', 50))

    # Divergent gradients
    blue_white = list(Color('#1f77b4').range_to('#f7f8ff', 25)) 
    white_red  = list(Color('#fffafa').range_to("#ff0000", 25))
    blue_red = blue_white[0:-1] + [Color('white'), Color('white')] + white_red[1:25]

    yellow_white = list(Color('#e4a32d').range_to('#fff7ea', 25))
    yellow_blue = yellow_white[0:-1] + [Color('white'), Color('white')] + list(reversed(blue_white))[1:25]

    white_green = list(Color('#f9fff9').range_to('#42d242', 25))
    red_green = list(reversed(white_red))[0:-1] + [Color('white'), Color('white')] + white_green[1:25]


class ColorGenerator(object):
    """
    Generates a color gradient given a maximum value and a minimum value, using
    min-max normalization in a 0-50 scale.
    
    Attributes:
        profile (ColorProfiles): Color profile enum element.
        max (float): Maximum value to generate color gradient.
        min (float): Minimum value to generate color gradient.

    Args:
        max_v (float): Maximum value to generate color gradient.
        min_v (float): Minimum value to generate color gradient.
        profile (string): Valid color profile string, see ColorProfiles
            for a list of the valid color profiles.

    """

    def __init__(self,  max_v, min_v, profile="red"):
        self.profile = ColorProfiles[profile]
        self.max = max_v
        self.min = min_v
    
    def map_color(self, value):
        """
        Assigns a color to the provided value by using the max and min attributes as
        the scale and normalizing the provided value using min-max normalization.
        
        Args:
            value (float): Value to transform to a color in the generated gradient
                between min and max attributes.
        
        Returns:
            string: hex color value.
        """
        thecolor = "#000000"
        if value != "NA":
            normval = int(self.__normalize(value))
            thecolor = str(self.profile.value[normval].hex)
        return thecolor
    
    def __normalize(self, x):
        """
        Min-Max normalization for normalizing values to 0-50 scale.

        Args:
            x (float): value to normalize to a min-max scale using min-max
                normalization.
        Returns:
            float: normalized value.
        """
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
        """
        Generates interval values for the gradient.

        Returns:
            `list` of `float`: List of 50 floats defining the intervals for 
                the gradient.
        """
        step = ( abs(self.max - self.min) ) / 50
        intervals = [ self.min ]
        while intervals[-1] < self.max:
            intervals.append( round( (intervals[-1] + step), 5) )
        return intervals


    def get_color_legend(self, units=None):
        """
        Returns html of legend for the color gradient.

        Args:
            units (str): Units for the values in the legend.
        
        Returns:
            str: html string with the legend for the generated color gradient.
        """
        html = [ "<div class='grid-container grid-legend-contaiener'></div>" ]
        intervals = list(reversed(self.__generate_intervals()))
        if len(intervals) == 1:
            # Empty legend because no expression for any genes
            return "\n"
        for color_idx, color in enumerate(reversed(self.profile.value)):
            title = "%s to %s" % (intervals[color_idx + 1], intervals[color_idx])
            if units is not None:
                title += " (%s)" % str(units)
            html.append("<div class='grid-item grid-legend info-tooltip' title='%s' style='background-color: %s'> </div>" % (title, color.hex) )
        html.append("</div>")
        return "\n".join(html)
    

