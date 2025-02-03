"""Utility functions and classes to manage colors and color interpolation."""
# Author(s): Davide.De-Marchi@ec.europa.eu
# Copyright © European Union 2024-2025
# 
# Licensed under the EUPL, Version 1.2 or as soon they will be approved by 
# the European Commission subsequent versions of the EUPL (the "Licence");
# 
# You may not use this work except in compliance with the Licence.
# 
# You may obtain a copy of the Licence at:
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12

# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS"
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# 
# See the Licence for the specific language governing permissions and
# limitations under the Licence.
import base64
from PIL import Image, ImageDraw
from io import BytesIO
import math
import random
import colorsys


# Force a value into [valuemin, valuemax]
def Normalize(value,valuemin,valuemax):
    if value > valuemax:
        return valuemax
    elif value < valuemin:
        return valuemin
    return value


# Returns a tuple of the complementary color (opposite color in the color wheel)
def complementaryColor(rgb):
    """
    Given a tuple color (r,g,b) returns the complementary version of the input color (see: `Complementary color meaning <https://www.color-meanings.com/complementary-colors/>`_ and `Color wheel online <https://atmos.style/color-wheel>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        Tuple of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette of a random color followed by its complementary color::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        colcomp  = colors.rgb2hex(colors.complementaryColor(colors.string2rgb(col)))
        display(colors.paletteImage([col, colcomp], interpolate=False))
    
    """
    # Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

    # Change the Hue value to the Hue opposite
    HueValue = HLS[0] * 360
    HLS[0] = ((HueValue + 180) % 360)/360

    # Convert HLS (between 0 and 1) to RGB (base 256)
    return tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(HLS[0], HLS[1], HLS[2])))


# Returs a list of two colors as rgb tuples
def triadicColor(rgb):
    """
    Given a tuple color (r,g,b) returns a list of two split triadic colors (see: `Triadic colors meaning <https://www.color-meanings.com/triadic-colors/>`_ and `Color wheel online <https://atmos.style/color-wheel>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        List of two tuples of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette showing an input random color and the two triadic colors::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        display(colors.paletteImage([col] + [colors.rgb2hex(x) for x in colors.triadicColor(colors.string2rgb(col))], interpolate=False))
    
    """
    # Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

    # Find the first triadic Hue
    FirstTriadicHue = ((HLS[0] * 360 + 120) % 360) / 360

    # Find the second triadic Hue
    SecondTriadicHue = ((HLS[0] * 360 + 240) % 360) / 360

    ColorOutput1 = [FirstTriadicHue,  HLS[1], HLS[2]]
    ColorOutput2 = [SecondTriadicHue, HLS[1], HLS[2]]

    rgb1 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput1[0],ColorOutput1[1],ColorOutput1[2])))
    rgb2 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput2[0],ColorOutput2[1],ColorOutput2[2])))

    return [rgb1, rgb2]


# Returs a list of two colors as rgb tuples
def splitComplementaryColor(rgb):
    """
    Given a tuple color (r,g,b) returns a list of two split complementary colors (see: `Split complementary colors meaning <https://www.color-meanings.com/split-complementary-colors/>`_ and `Color wheel online <https://atmos.style/color-wheel>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        List of two tuples of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette showing an input random color and the two split complementary colors::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        display(colors.paletteImage([col] + [colors.rgb2hex(x) for x in colors.splitComplementaryColor(colors.string2rgb(col))], interpolate=False))
    
    """
    # Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

    # Find the first triadic Hue
    FirstSplitComplementaryHue = ((HLS[0] * 360 + 150) % 360) / 360

    # Find the second triadic Hue
    SecondSplitComplementaryHue = ((HLS[0] * 360 + 210) % 360) / 360

    ColorOutput1 = [FirstSplitComplementaryHue,  HLS[1], HLS[2]]
    ColorOutput2 = [SecondSplitComplementaryHue, HLS[1], HLS[2]]

    rgb1 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput1[0],ColorOutput1[1],ColorOutput1[2])))
    rgb2 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput2[0],ColorOutput2[1],ColorOutput2[2])))

    return [rgb1, rgb2]


# Returs a list of four colors as rgb tuples
def tetradicColor(rgb):
    """
    Given a tuple color (r,g,b) returns a list of four tetradic colors (see: `Tetradic colors meaning <https://www.color-meanings.com/rectangular-tetradic-color-schemes/>`_ and `Color wheel online <https://atmos.style/color-wheel>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        List of four tuples of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette showing an input random color and the three tetradic colors::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        display(colors.paletteImage([col] + [colors.rgb2hex(x) for x in colors.tetradicColor(colors.string2rgb(col))], interpolate=False))
    
    """
    # Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

    # Find the first tetradic Hue
    FirstTetradicHue  = ((HLS[0] * 360 +  30) % 360) / 360

    # Find the second tetradic Hue
    SecondTetradicHue = ((HLS[0] * 360 + 150) % 360) / 360

    # Find the third tetradic Hue
    ThirdTetradicHue  = ((HLS[0] * 360 + 210) % 360) / 360

    # Find the fourth tetradic Hue
    FourthTetradicHue = ((HLS[0] * 360 + 330) % 360) / 360
    
    ColorOutput1 = [FirstTetradicHue,  HLS[1], HLS[2]]
    ColorOutput2 = [SecondTetradicHue, HLS[1], HLS[2]]
    ColorOutput3 = [ThirdTetradicHue,  HLS[1], HLS[2]]
    ColorOutput4 = [FourthTetradicHue, HLS[1], HLS[2]]

    rgb1 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput1[0],ColorOutput1[1],ColorOutput1[2])))
    rgb2 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput2[0],ColorOutput2[1],ColorOutput2[2])))
    rgb3 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput3[0],ColorOutput3[1],ColorOutput3[2])))
    rgb4 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput4[0],ColorOutput4[1],ColorOutput4[2])))

    return [rgb1, rgb2, rgb3, rgb4]


# Returs a list of three colors as rgb tuples
def squareColor(rgb):
    """
    Given a tuple color (r,g,b) returns a list of three square colors (see: `Color wheel online <https://atmos.style/color-wheel>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        List of three tuples of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette showing an input random color and the three tetradic colors::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        display(colors.paletteImage([col] + [colors.rgb2hex(x) for x in colors.squareColor(colors.string2rgb(col))], interpolate=False))
    
    """
    # Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

    # Find the first tetradic Hue
    FirstTetradicHue  = ((HLS[0] * 360 +  90) % 360) / 360

    # Find the second tetradic Hue
    SecondTetradicHue = ((HLS[0] * 360 + 180) % 360) / 360

    # Find the third tetradic Hue
    ThirdTetradicHue  = ((HLS[0] * 360 + 270) % 360) / 360

    ColorOutput1 = [FirstTetradicHue,  HLS[1], HLS[2]]
    ColorOutput2 = [SecondTetradicHue, HLS[1], HLS[2]]
    ColorOutput3 = [ThirdTetradicHue,  HLS[1], HLS[2]]

    rgb1 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput1[0],ColorOutput1[1],ColorOutput1[2])))
    rgb2 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput2[0],ColorOutput2[1],ColorOutput2[2])))
    rgb3 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput3[0],ColorOutput3[1],ColorOutput3[2])))

    return [rgb1, rgb2, rgb3]


# Returs a list of two colors as rgb tuples
def analogousColor(rgb):
    """
    Given a tuple color (r,g,b) returns a list of two analogous colors (see: `Analogous colors meaning <https://www.color-meanings.com/analogous-colors/>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    Returns
    -------
        List of two tuples of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette showing an input random color and the two analogous colors::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        display(colors.paletteImage([col] + [colors.rgb2hex(x) for x in colors.analogousColor(colors.string2rgb(col))], interpolate=False))
    
    """
	# Convert RGB (base 256) to HLS (between 0 and 1 )
    HLS = list(colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255))

	# Find the first analogous Hue
    FirstAnalogousHue = ((HLS[0] * 360 + 30) % 360) / 360

    # Find the second analogous Hue
    SecondAnalogousHue = ((HLS[0] * 360 - 30) % 360) / 360

    ColorOutput1 = [FirstAnalogousHue,  HLS[1], HLS[2]]
    ColorOutput2 = [SecondAnalogousHue, HLS[1], HLS[2]]

    rgb1 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput1[0],ColorOutput1[1],ColorOutput1[2])))
    rgb2 = tuple(map(lambda x: round(x * 255), colorsys.hls_to_rgb(ColorOutput2[0],ColorOutput2[1],ColorOutput2[2])))

    return [rgb1, rgb2]


# Returs a tuple of darker (negative increment) or lighter color (positive increment)
def monochromaticColor(rgb, increment=0.20):
    """
    Given a tuple color (r,g,b) returns a darker (if increment is negative) or lighter (if increment is positive) version of the input color (see: `Monochromatic colors meaning <https://www.color-meanings.com/monochromatic-color-schemes/>`_)

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]

    increment : float, optional
        Increment/decrement in lightness in [-1.0, 1.0] (default is 0.2)

    Returns
    -------
        Tuple of 3 integers representing the output RGB components in the range [0,255]
        
    Example
    -------
    Display a palette of a random color followed by its darker and lighter version::
    
        from vois import colors
        from IPython.display import display
        
        col = colors.randomColor()
        coldarker  = colors.rgb2hex(colors.monochromaticColor(colors.string2rgb(col), increment=-0.25))
        collighter = colors.rgb2hex(colors.monochromaticColor(colors.string2rgb(col), increment=0.25))
        display(colors.paletteImage([col, coldarker, collighter], interpolate=False))
    
    """
	# Convert RGB (base 256) to HSV (between 0 and 1)
    HSV = list(colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255))
    return tuple(map(lambda x: Normalize(round(x * 255),0,255), colorsys.hsv_to_rgb(HSV[0], HSV[1]-increment, HSV[2]+increment)))


# Returns True if the (r,g,b) color id dark
def isColorDark(rgb):
    """
    Returns True if the color (r,g,b) is dark

    Parameters
    ----------
    rgb : tuple
        Tuple of 3 integers representing the RGB components in the range [0,255]
       
    """
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if hsp > 127.5:
        return False
    else:
        return True

# Returns the Multiply blend of two colors strings
def multiply(color1,color2):
    """
    Returns the Multiply blend of two colors strings
    """
    rgb1 = string2rgb(color1)
    rgb2 = string2rgb(color2)
    norm1 = [x/255.0 for x in rgb1]
    norm2 = [x/255.0 for x in rgb2]
    return rgb2hex(tuple([int(255.0*x[0]*x[1]) for x in zip(norm1,norm2)]))


# Returns the Darken blend of two colors strings
def darken(color1,color2):
    """
    Returns the Darken blend of two colors strings
    """
    rgb1 = string2rgb(color1)
    rgb2 = string2rgb(color2)
    return rgb2hex(tuple([min(x[0],x[1]) for x in zip(rgb1,rgb2)]))


# Return a random color in the '#rrggbb' format
def randomColor():
    """
    Returns a random color in the '#rrggbb' format
    """
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return rgb2hex((r,g,b))


# Utility: From (r,g,b) to '#rrggbb'
def rgb2hex(rgb):
    """
    Converts from a color represented as a (r,g,b) tuple to a hexadecimal string representation of the color '#rrggbb'

    Parameters
    ----------
    rgb : tuple of 3 int values
        Input color described by its RGB components as 3 integer values in the range [0,255]
        
    Returns
    -------
        A string containing the color represented as hexadecimals in the '#rrggbb' format
        
    Example
    -------
    Convert a color from (r,g,b) to '#rrggbb'::
    
        from vois import colors
        print( colors.rgb2hex( (255,0,0) ) )
        
    """
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


# Utility: From '#rrggbb' to (r,g,b)
def hex2rgb(color):
    """
    Converts from a hexadecimal string representation of the color '#rrggbb' to a (r,g,b) tuple

    Parameters
    ----------
    color : string
        A string containing the color represented as hexadecimals in the '#rrggbb' format
        
    Returns
    -------
        Tuple of 3 integers representing the RGB components in the range [0,255]
        
    Example
    -------
    Convert a color from '#rrggbb' to (r,g,b)::

        from vois import colors
        print( colors.hex2rgb( '#ff0000' ) )
        
    """
    if color[0] == '#':
        color = color[1:]
    rgb = (int(color[0:2],16), int(color[2:4],16), int(color[4:6],16))
    return rgb


# Utility: From 'rgb(a,b,c)' to (r,g,b)
def text2rgb(color):
    """
    Converts from string representation of the color 'rgb(r,g,b)' to a (r,g,b) tuple

    Parameters
    ----------
    color : string
        A string containing the color represented in the 'rgb(r,g,b)' format
        
    Returns
    -------
        Tuple of 3 integers representing the RGB components in the range [0,255]
        
    Example
    -------
    Convert a color from 'rgb(r,g,b)' to (r,g,b)::
    
        from vois import colors
        print( colors.text2rgb( 'rgb(255,0,0)' ) )
        
    """
    if color[0:4] == 'rgb(':
        rgb = color[4:].replace(')','').split(',')
        if len(rgb) >= 3:
            return ((int(rgb[0]),int(rgb[1]),int(rgb[2])))
           
    return (0,0,0)


# Utility: Convert a color string in '#rrggbb' or in 'rgb(...)' format into a tuple (r,g,b)
def string2rgb(s):
    """
    Converts from string representation of the color 'rgb(r,g,b)' or '#rrggbb' to a (r,g,b) tuple

    Parameters
    ----------
    color : string
        A string containing the color represented in the 'rgb(r,g,b)' format or in the '#rrggbb' format
        
    Returns
    -------
        Tuple of 3 integers representing the RGB components in the range [0,255]
    """
    if s[0] == '#':
        return hex2rgb(s)
    elif s[0:4] == 'rgb(':
        return text2rgb(s)
    return (0,0,0)




# Utility: convert a PIL image into a string containing the image in base64
def image2Base64(img):
    """
    Given a PIL image, returns a string containing the image in base64 format
        
    Parameters
    ----------
    img : PIL image
        Input PIL image
                
    Returns
    -------
    A string containing the image in base64 format

    """
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return 'data:image/png;base64,' + img_str
    

