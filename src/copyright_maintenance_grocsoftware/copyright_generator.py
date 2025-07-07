"""@package copyright_tools
Scan source files and find the copyright message, parse the copyright into it's component parts and
generate updates copyright text
"""
#==========================================================================
# Copyright (c) 2025 Randal Eike
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of self software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and self permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#==========================================================================

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish

class CopyrightGenerator(object):
    """!
    @brief Copyright message generator

    This class is used to generate new copyright message values based
    on a previously parsed copyright message and new dates or completely
    new copyright messages if a previously parsed message is unavailable.
    """
    def __init__(self, parser = None):
        """!
        @brief Constructor
        """
        ## Copyright parser object for parsed data, default copyright text and order specification
        self.parser = parser
        if parser is None:
            self.parser = CopyrightParseEnglish()

    @staticmethod
    def _is_multi_year(create_year:int, last_modify_year:int|None)->bool:
        """!
        Determine if this is a multi or single year message

        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file or None

        @return bool - True if last_modify_year is not None and last_modify_year != create_year
        """
        if last_modify_year is not None:
            if last_modify_year != create_year:
                return True
            else:
                return False
        else:
            return False

    def _get_new_copyright_msg(self, create_year:int, last_modify_year:int|None = None)->tuple:
        """
        @brief Determine if a new copyright message is required and return if message changed
               and the new copyright message

        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        copyright_year_list = self.parser.get_copyright_dates()

        # Convert match text to year integers
        current_start_year = int(copyright_year_list[0])

        # Don't move copyright forward
        if current_start_year < create_year:
            start_year = current_start_year
        else:
            start_year = create_year

        # Test if input is multiyear or current is multiyear
        if ((CopyrightGenerator._is_multi_year(create_year, last_modify_year)) or
            (len(copyright_year_list) > 1)):

            # Convert match text to year integers
            current_modify_year = int(copyright_year_list[-1])
            if last_modify_year is None:
                if create_year > current_modify_year:
                    last_modify_year = create_year
                else:
                    last_modify_year = current_modify_year

            # Check for change
            if ((current_start_year == start_year) and
                (current_modify_year == last_modify_year)):
                # No need to change return the old line
                new_copyright_msg = self.parser.get_copyright_text()
                msg_changed = False
            else:
                # Generate the new message
                new_copyright_msg = self.parser.build_new_copyright_msg(start_year,
                                                                        last_modify_year,
                                                                        True)
                msg_changed = True
        else:
            if ((len(copyright_year_list) == 1) and
                (start_year == current_start_year)):
                # No need to change return the old line
                new_copyright_msg = self.parser.get_copyright_text()
                msg_changed = False
            else:
                # Update with a new line
                new_copyright_msg = self.parser.build_new_copyright_msg(start_year,
                                                                        last_modify_year,
                                                                        True)
                msg_changed = True

        return msg_changed, new_copyright_msg

    def _get_default_copyright_msg(self, create_year:int, last_modify_year:int|None = None)->tuple:
        """!
        @brief Generate a new multiyear copyright message using default values

        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        new_copyright_msg =  self.parser.create_copyright_msg("None", create_year, last_modify_year)
        return True, new_copyright_msg

    def get_new_copyright_msg(self, create_year:int, last_modify_year:int|None = None)->tuple:
        """!
        @brief Determine if a new copyright message is required and return if message changed
               and the new copyright message

        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file or None

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        if self.parser.is_copyright_text_valid():
            return self._get_new_copyright_msg(create_year, last_modify_year)
        else:
            return self._get_default_copyright_msg(create_year, last_modify_year)

    def create_copyright_transition(self, create_year:int, transition_year:int,
                                    last_modify_year:int, new_owner:str)->tuple:
        """!
        @brief Modify the old copyright message to end with the transition year input and
               create a new copyright message with the transition year and new owner

        @param create_year (integer): File creation date
        @param transition_year (integer): Last year of first message, first year of new message
        @param last_modify_year (integer): Last modification date of the file
        @param new_owner (string): Owner for the new message

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        @return string : New owner copyright message
        """
        msg_changed, original_copyright = self._get_new_copyright_msg(create_year, transition_year)
        self.parser.replace_owner(new_owner)
        new_copyright_msg = self.parser.build_new_copyright_msg(transition_year,
                                                                last_modify_year,
                                                                True)
        return msg_changed, original_copyright, new_copyright_msg

    def add_copyright_owner(self, create_year:int, last_modify_year:int, new_owner:str)->tuple:
        """!
        @brief Modify the old copyright message to end with the transition year input and
               create a new copyright message with the transition year and new owner

        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file
        @param new_owner (string): Owner for the new message

        @return bool: True is the copyright dates changed, else false
        @return string : New owner copyright message
        """
        if self.parser.add_owner(new_owner):
            new_copyright_msg = self.parser.build_new_copyright_msg(create_year,
                                                                    last_modify_year,
                                                                    True)
            return True, new_copyright_msg
        else:
            return False, None

    def create_new_copyright(self, owner:str, create_year:int,
                             last_modify_year:int|None = None)->str:
        """!
        @brief Create a new copyright message from scratch

        @param owner (string): Owner for the new message
        @param create_year (integer): File creation date
        @param last_modify_year (integer): Last modification date of the file

        @return string : New owner copyright message
        """
        return self.parser.create_copyright_msg(owner, create_year, last_modify_year)
