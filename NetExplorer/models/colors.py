from .common import *

class ColorProfiles(Enum):
    # Linear gradients
    red = list(Color('#fffafa').range_to('#ff0000', 50))
    blue = list(Color('#f7f8ff').range_to('#0029ff', 50))
    green = list(Color('#f9fff9').range_to('#42d242', 50))

    # Divergent gradients
    blue_red = list(Color('#1f77b4').range_to('white', 25)) + list(Color('white').range_to("#ff0000", 25))
    yellow_blue = list(Color('#e4a32d').range_to('white', 25)) + list(Color('white').range_to("#0029ff", 25))
    red_green = list(Color('#ff0000').range_to('white', 25)) + list(Color('white').range_to("#42d242", 25))

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
            thecolor = str(self.profile.value[normval])
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
    

