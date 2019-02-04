from .common import *

class ColorProfiles(Enum):
    red = list(Color('#fffafa').range_to('#ff0000', 50))
    blue = list(Color('#f7f8ff').range_to('#0029ff', 50))
    green = list(Color('#f9fff9').range_to('#42d242', 50))
    blue_red = 4
    yellow_blue = 5
    red_green = 6


class ColorGenerator(object):
    '''
    What up
    '''

    def __init__(self,  max_v, min_v, profile="red"):
        self.profile = ColorProfiles[profile]
        self.max = max_v
        self.min = min_v
    
    def map_color(self, value):
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
    

