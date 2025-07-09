"""@package upcopyright_maintenancedate_copyright
@brief Scan source files and update copyright years
Scan the source files and update the copyright year in the header section of any modified files
"""

#==========================================================================
# Copyright (c) 2024 Randal Eike
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

import datetime

from copyright_maintenance_grocsoftware.file_dates import get_file_years
from copyright_maintenance_grocsoftware.oscmdshell import get_command_shell

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.copyright_generator import CopyrightGenerator
from copyright_maintenance_grocsoftware.copyright_finder import CopyrightFinder
from copyright_maintenance_grocsoftware.comment_block import CommentBlock
from copyright_maintenance_grocsoftware.comment_block import CommentParams

class CopyrightCommentBlock(CommentBlock):
    """!
    Identify the start and end of a comment blocks and determine if the
    copyright message is in the block(s)
    """
    def __init__(self, input_file,
                 comment_markers:dict = None,
                 copyright_parser = None):
        """!
        @brief Constructor

        @param self(CopyrightCommentBlock) - Object reference
        @param input_file(file) - Open file object to read and identify the copyright block in.
        @param comment_markers(CommentBlockDelim element) - Comment deliminter markers for the
                                                            input file type.
        @param copyright_parser(CopyrightParse object) - Copyright parser object or None if
                                                         default parser is to be used.

        @return pass
        """
        super().__init__(input_file, comment_markers)

        ## Copyright parser object to use for generation
        self._copyright_parser = CopyrightParseEnglish()
        if copyright_parser is not None:
            self._copyright_parser = copyright_parser

        ## File to parse and look for the copyright message
        self.input_file = input_file
        ## List of copyright comment block dictionary entries found
        self._copyright_block_data = []

    def _is_copyright_comment_block(self, comment_blk_strt_off:int,
                                    comment_blk_end_off:int)->tuple:
        """!
        @brief Check if the copyright message is within the current comment block

        @param comment_blk_strt_off (fileoffset): File offset of the comment block start
        @param comment_blk_end_off (fileoffset): File offset of the comment block start


        @return bool: True if copyright message is found, else false
        @return dictionary: {'lineOffset': Starting file offset of the copyright message line,
                             'text': Current copyright text line}
        """
        if (comment_blk_strt_off is not None) and (comment_blk_end_off is not None):
            self.input_file.seek(comment_blk_strt_off)
            copyright_finder = CopyrightFinder(self._copyright_parser)
            status, data = copyright_finder.find_next_copyright_msg(self.input_file,
                                                                    comment_blk_strt_off,
                                                                    comment_blk_end_off)
        else:
            status = False
            data = None
        return status, data

    def _is_find_next_copyright_block(self)->dict:
        """!
        @brief Scan the current file from the current location to find a copyright comment block

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright comment block location data dictionary
                            {'blkStart': copyright comment block starting file offset,
                             'blkEndEOL': copyright comment block ending file offset,
                             'blkEndSOL': copyright comment block ending line start file offset,
                             'copyrightMsgs': list of copyright data dictionaries
                                              [{'lineOffset': Starting file offset of the
                                                              copyright message line,
                                                'text': Current copyright text line}]
                            }
        """
        copyright_block_found = False

        if self.find_next_comment_block():
            # Check if the block is a copyright block
            location_dict = {'blkStart': self.comment_blk_strt_off,
                            'blkEndEOL': self.comment_blk_eol_off,
                            'blkEndSOL': self.comment_blk_sol_off,
                            'copyrightMsgs': []
                            }

            # Check if there are any copyright lines in the block
            start_location = self.comment_blk_strt_off
            while start_location < self.comment_blk_eol_off:
                copyright_line_found, copyright_location = self._is_copyright_comment_block(
                                                             start_location,
                                                             self.comment_blk_eol_off)
                if copyright_line_found:
                    start_location = copyright_location['lineOffset']
                    start_location += len(copyright_location['text'])
                    location_dict['copyrightMsgs'].append(copyright_location)
                    copyright_block_found = True
                else:
                    break

        return copyright_block_found, location_dict

    def find_copyright_blocks(self)->list:
        """!
        @brief Scan the file for the comment block

        @return (list): List of copyright block comment block location dictionaries
                        [{'blkStart': copyright comment block starting file offset,
                          'blkEndEOL': copyright comment block ending file offset,
                          'blkEndSOL': copyright comment block ending line start file offset,
                          'copyrightMsgs': list of copyright data dictionaries
                                           [{'lineOffset': Starting file offset of the
                                                           copyright message line,
                                            'text': Current copyright text line}]
                        }]
        """
        self.input_file.seek(0)
        self._copyright_block_data.clear()

        # Scan the file
        copyright_block_found = True
        while copyright_block_found:
            copyright_block_found, location = self._is_find_next_copyright_block()
            if copyright_block_found:
                self._copyright_block_data.append(location)

        return self._copyright_block_data

def insert_new_copyright_block(input_file, output_filename:str, comment_block_data:dict,
                               comment_marker:dict, new_copyright_msg:str,
                               new_eula:list = None)->bool: # pylint: disable=too-many-arguments
    """!
    @brief Write a new file with the updated copyright message

    @param input_file (file): Existing text file
    @param output_filename (filename string): Name of the file to output updated text to
    @param comment_block_data (dictionary): Comment block locations to update
    @param comment_marker (dictionary): commentBlockDelim object to use for comment block
                                        replacement
    @param new_copyright_msg (string): New copyright message to write to the new file
    @param new_eula (list of strings): New license text to add to the copyright comment block

    @return Bool - True if new file was written, False if an error occured.
    """
    try: # pylint: disable=consider-using-with
        output_file = open(output_filename, mode='wt', encoding="utf-8")

        # Copy the first chunk of the file
        input_file.seek(0)
        if comment_block_data['blkStart'] != 0:
            header = input_file.read(comment_block_data['blkStart'])
            output_file.write(header)

        # Output start of the comment block
        new_line = comment_marker['blockStart']+"\n"
        output_file.write(new_line)

        # Insert the new copyright and licence text
        new_line = comment_marker['blockLineStart']+" "+new_copyright_msg+"\n"
        output_file.write(new_line)

        # Determine if we should update EULA
        if new_eula is not None:
            new_line = comment_marker['blockLineStart']+"\n"
            output_file.write(new_line)

            # Insert new EULA
            for licence_line in new_eula:
                new_line = comment_marker['blockLineStart']+" "+licence_line+"\n"
                output_file.write(new_line)
        else:
            # Copy old EULA
            copyright_location = comment_block_data['copyrightMsgs'][0]
            copyright_end = copyright_location['lineOffset'] + len(copyright_location['text'])
            input_file.seek(copyright_end)
            current_line_offset = copyright_end
            while current_line_offset < comment_block_data['blkEndSOL']:
                new_line = comment_marker['blockLineStart']+" "+input_file.readline()
                output_file.write(new_line)
                current_line_offset = input_file.tell()

        # Output the comment block end
        new_line = comment_marker['blockEnd']+"\n"
        output_file.write(new_line)

        # Copy the remainder of the file
        input_file.seek(comment_block_data['blkEndEOL'])
        while new_line:
            new_line = input_file.readline()
            output_file.write(new_line)

        output_file.close()
        return True

    except OSError:
        print("ERROR: Unable to open file \""+output_filename+"\" for writing as text file.")
        return False

def update_copyright_years(filename:str):
    """!
    @brief Update the copyright years in the copyright message of the input file

    @param filename(string): path and name of file to update
    """
    creation_year_str, modify_year_str = get_file_years(filename)

    if creation_year_str is None:
        print ("None returned from get_file_years() for creation year")
        creation_year = datetime.datetime.now().year
    else:
        creation_year = int(creation_year_str)

    if modify_year_str is None:
        print ("None returned from get_file_years() for modification year")
        modification_year = datetime.datetime.now().year
    else:
        modification_year = int(modify_year_str)

    with open(filename, "rt", encoding="utf-8") as testfile:
        # Get a copyright message parser and comment block parser
        copyright_parser = CopyrightParseEnglish()
        copyright_generator = CopyrightGenerator(copyright_parser)
        comment_processor = CopyrightCommentBlock(testfile,
                                                CommentParams.get_comment_markers(filename),
                                                copyright_parser)
        # Find all copyright comment blocks
        copyright_msg_list = comment_processor.find_copyright_blocks()
        if copyright_msg_list:
            # Process the old message
            old_msg = copyright_msg_list[0]['copyrightMsgs'][-1]['text']
            old_msg = old_msg.rstrip()
            copyright_parser.parse_copyright_msg(old_msg)

            # Get the new message
            msg_changed, new_msg = copyright_generator.get_new_copyright_msg(creation_year,
                                                                             modification_year)
            if msg_changed:
                get_command_shell().stream_edit(filename, old_msg, new_msg)
