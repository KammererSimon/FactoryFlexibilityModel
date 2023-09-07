# This is a helper class to simplify the usage of color values. It stores a color both in rgba and hex format.

import logging
import re


class color:
    def __init__(self, color_value):
        """
        This function initializes a color specification object using the value handed over as color.
        """

        # check if color is given in hex or rgba-format and set values properly
        if self.__is_valid_rgb_hex(color_value):
            self.hex = color_value
            self.rgba = self.__hex_to_rgba(color_value, 1)

        elif self.__is_valid_rgba(color_value):
            self.hex = self.__rgba_to_hex(color_value)
            self.rgba = color_value

        # if given color value is invalid: use black
        else:
            logging.warning(
                f"Given value is not a valid color specifier! Color is set to default. ({color_value})"
            )
            self.hex = "#000000"
            self.rgba = [0, 0, 0, 1]

        self.tuple = tuple(self.rgba)

    def __is_valid_rgb_hex(self, value):
        """
        This function takes an input and analyzes if it is a valid color-string
        :param value: -> any user input
        :return: [boolean] -> True, if value is a valid colorstring
        """

        if isinstance(value, str):
            pattern = r"^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"
            return bool(re.match(pattern, value))
        else:
            return False

    def __is_valid_rgba(self, value):
        """
        This function takes an input and analyzes if it is a valid color in rgba-array format
        :param value: -> any user input
        :return: [boolean] -> True, if value is a valid rgba-color array
        """

        if len(value) != 4:
            return False
        return all(0 <= x <= 1 for x in value)

    def __hex_to_rgba(self, string, alpha=1.0):
        """
        This function takes a hex-colorstring in '#FFFFFF' - format and converts it into a rbga-value
        :param string: [string] -> #FFFFFF - type colorstring
        :param alpha: [float] -> alpha value of the color between 0..1
        :return: [[r,g,b,a]] -> array with values between 0..1 for red, green, blue and alpha
        """

        #   delete "#"
        string = string.lstrip("#")

        #   make sure that the strig has 6 letters
        if len(string) == 3:
            string = "".join([x * 2 for x in string])
        elif len(string) != 6:
            return None

        # make hex -> decimal conversion
        r, g, b = (int(string[i : i + 2], 16) for i in (0, 2, 4))

        # return values
        return [x / 255.0 for x in (r, g, b)] + [alpha]

    def __rgba_to_hex(self, value):
        """
        This function takes a color as an rgba-array and converts it into a hex-string format
        :param value: [string] -> [r, g, b, a] array with values between 0 and 1
        :return: [string] -> '#FFFFFF'
        """

        r, g, b = (int(x * 255) for x in value[:3])
        return f"#{r:02x}{g:02x}{b:02x}"
