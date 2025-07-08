"""@package copyright_maintenance
@brief Scan source files and find the copyright message

Parse the copyright into it's component parts and
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

class CopyrightFinder():
    """!
    Copyright message finder class
    """
    def __init__(self, parser = None):
        """!
        @brief Constructor

        @param parser (CopyrightParse object) - Copyright parser object to use
                                                or None to use a default parser
        """
        ## Copyright parser object for regex search criteria,
        ## default copyright text and order specification
        self._parser = parser
        if parser is None:
            self._parser = CopyrightParseEnglish()

    def find_next_copyright_msg(self, input_file, start_offset:int,
                                end_offset:int|None = None)->tuple:
        """!
        @brief Scan the current file from the start_offset location to find the next copyright
               message

        @param input_file (file object): File object, open for reading
        @param start_offset (file offset): File offset to begin the scan at.
        @param end_offset (file offset): File offset to end the scan at or None to continue to
                                         end of file

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright message location data dictionary
                            {'lineOffset': file offset of the copy right line,
                             'text': Copyright text line from the file}
        """

        copyright_found = False
        location_dict = None
        input_file.seek(start_offset)

        while not copyright_found:
            # Read the test line
            current_line_offset = input_file.tell()
            current_line = input_file.readline()

            # Check for end of file
            if not current_line:
                break

            # check for search end
            if end_offset is not None:
                if current_line_offset >= end_offset:
                    break

            # Check for match
            if self._parser.is_copyright_line(current_line):
                location_dict = {'lineOffset': current_line_offset, 'text': current_line}
                copyright_found = True

        return copyright_found, location_dict

    def find_copyright_msg(self, input_file)->tuple:
        """!
        @brief Scan the current file from the current location to find a copyright messge

        @param input_file (file object): File object, open for reading

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright message location data dictionary
                            {'lineOffset': file offset of the copy right line,
                             'text': Copyright text line from the file}
        """
        return self.find_next_copyright_msg(input_file, 0, None)

    def find_all_copyright_msg(self, input_file)->tuple:
        """!
        @brief Scan the current file from the current location to find a copyright comment block
        @return bool: True if copyright block is found, else false
        @return list of dictionary: Copyright message location data dictionary
                                    {'lineOffset': file offset of the copy right line,
                                     'text': Copyright text line from the file}
        """
        copyright_dict_list = []
        start_location = 0
        return_status = False
        return_text = None

        while True:
            copyright_found, location_dict = self.find_next_copyright_msg(input_file,
                                                                          start_location,
                                                                          None)
            if copyright_found:
                copyright_dict_list.append(location_dict)
                start_location = location_dict['lineOffset'] + len(location_dict['text'])
            else:
                break

        if copyright_dict_list:
            return_status = True
            return_text = copyright_dict_list
        return return_status, return_text
