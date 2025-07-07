"""@package comment_tools
@brief Comment block find and generate tools
Scan source files to find comment block(s). Utility to generate new comment blocks
"""

#==========================================================================
# Copyright (c) 2024-2025 Randal Eike
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

import os
import re

class TextFileCommentBlock(object):
    """!
    Identify the start and end of a comment text block

    """
    def __init__(self, input_file):
        """!
        @brief Constructor
        @param input_file (file): Open file object to read and identify the copyright block in.
        """
        ## File offset of the copyright comment block start if found or None if not found
        self.comment_blk_strt_off = None
        ## File offset of the copyright comment block end if found or None if not found
        self.comment_blk_eol_off = None
        ## File to parse and look for the copyright message
        self._input_file = input_file
        ## False until a non-blank line is found
        self._foundtext_start = False

    def _is_current_line_comment_start(self, current_line:str)->bool:
        """!
        @brief Determine if the input current line is the start of a comment block

        @param current_line (string): current line current line of the test file

        @return bool: True if this line is the start of a comment block, else False
        """
        if self._foundtext_start:
            return False
        else:
            start_match = re.search(r'\S', current_line)
            if start_match is not None:
                self._foundtext_start = True
                return True
            else:
                return False

    def _is_current_line_comment_end(self, current_line:str)->bool:
        """!
        @brief Check if the line is the end of a comment block

        @param current_line (string): current line current line of the test file

        @return bool: True if the current line is the end of a comment block, else False
        """
        if self._foundtext_start:
            end_match = re.search(r'\S', current_line)
            if end_match is not None:
                return False
            else:
                self._foundtext_start = False     # Reset text file block start
                return True
        else:
            return False

    def find_next_comment_block(self):
        """!
        @brief Scan the current file from the current location to find a comment block

        @return bool: True if comment block found, else False
        """

        # initialize working variables
        previous_line = ""
        previous_line_off = None

        self.comment_blk_strt_off = None
        self.comment_blk_eol_off = None

        comment_block_found = False
        self.comment_blk_eol_off = None
        while not comment_block_found:
            # Read the test line
            current_line_offset = self._input_file.tell()
            current_line = self._input_file.readline()
            if not current_line:
                # Check for special text file case
                if ((self.comment_blk_strt_off is not None) and
                    (self.comment_blk_eol_off is None)):
                    self.comment_blk_eol_off = previous_line_off + len(previous_line)
                    comment_block_found = True
                break

            # Check for comment block start or end
            if self._is_current_line_comment_start(current_line):
                # Process comment block start
                self.comment_blk_strt_off = current_line_offset
            elif self._is_current_line_comment_end(current_line):
                # Process comment block end
                self.comment_blk_eol_off = current_line_offset + len(current_line)
                comment_block_found = True

            # Move to the next line and return true to continue for each loop
            previous_line = current_line
            previous_line_off = current_line_offset

        # return if we found a comment block
        return comment_block_found

class CommentParams(object):
    """!
    Comment marker definitions and static selection methods
    """
    ##C/C++/Typescript/Javascript comment marker dictionary
    cCommentParms =   {'blockStart': "/*",
                       'blockEnd': "*/",
                       'blockLineStart': "",
                       'singleLine': "//"}
    ##Python comment marker dictionary
    pyCommentParms =  {'blockStart': "\"\"\"",
                       'blockEnd':"\"\"\"",
                       'blockLineStart': "",
                       'singleLine': "#"}
    ##Bash shell comment marker dictionary
    shCommentParms =  {'blockStart': None,
                       'blockEnd': None,
                       'blockLineStart': "#",
                       'singleLine': "#"}
    ##Batch comment marker dictionary
    batCommentParms = {'blockStart': None,
                       'blockEnd': None,
                       'blockLineStart': "REM ",
                       'singleLine': "REM "}

    ##Comment block marker by file extention lookup dictionary
    commentBlockDelim = {'.c':   cCommentParms,
                         '.cpp': cCommentParms,
                         '.h':   cCommentParms,
                         '.hpp': cCommentParms,
                         '.js':  cCommentParms,
                         '.ts':  cCommentParms,
                         '.py':  pyCommentParms,
                         '.sh':  shCommentParms,
                         '.bat': batCommentParms,
                         }

    @staticmethod
    def get_comment_markers(filename:str)->dict|None:
        """!
        @brief Determine the comment marker values from the file name

        @param filename (string): File name

        @return dictionary: commentBlockDelim entry that matches the file extension or
                            None if no extension match is found
        """
        name_ext = os.path.splitext(filename)
        extension = name_ext[1]

        # pylint: disable=locally-disabled, disable=C0201
        if extension in CommentParams.commentBlockDelim.keys():
            return CommentParams.commentBlockDelim[extension]
        else:
            return None


class CommentBlock(object):
    """!
    Identify the start and end of a comment block
    """
    def __init__(self, input_file, comment_markers:dict|None = None):
        """!
        @brief Constructor
        @param input_file (file): Open file object to read and identify the copyright block in.
        @param comment_markers (CommentBlockDelim element): Comment deliminter markers for
                                                            the input file type.
        """
        ## File offset of the copyright comment block start if found or None if not found
        self.comment_blk_strt_off = None
        ## File offset of the copyright comment block end end of line if found
        ## or None if not found
        self.comment_blk_eol_off = None
        ## File offset of the copyright comment block end start of line if found
        ## or None if not found
        self.comment_blk_sol_off = None
        ## File to parse and look for the copyright message
        self._input_file = input_file
        ## Comment block markers typical for the file type
        self.comment_data = comment_markers

    def _is_current_line_comment_start(self, current_line:str)->bool:
        """!
        @brief Determine if the input current line is the start of a comment block

        @param current_line (string): current line current line of the test file

        @return bool: True if this line is the start of a comment block, else False
        """
        if ((self.comment_data is not None) and
            (self.comment_data["blockStart"] is not None)):
            if 0 == current_line.find(self.comment_data["blockStart"]):
                return True
        return False

    def _is_previous_line_comment_start(self, previous_line:str, current_line:str)->bool:
        """!
        @brief Check if the previous line is the start of a comment block

        @param previous_line (string): previous line previous line of the test file
        @param current_line (string): current line current line of the test file

        @return bool: True if the previous line is the start of a comment block, else False
        """
        if (self.comment_data is not None) and (previous_line is not None):
            if ((0 == previous_line.find(self.comment_data["singleLine"])) and
                (0 == current_line.find(self.comment_data["singleLine"]))):
                return True
        return False

    def _is_current_line_comment_end(self, current_line:str)->bool:
        """!
        @brief Check if the line is the end of a comment block

        @param current_line (string): current line current line of the test file

        @return bool: True if the current line is the end of a comment block, else False
        """
        if ((self.comment_data is not None) and
            (self.comment_data["blockEnd"] is not None)):
            if -1 != current_line.find(self.comment_data["blockEnd"]):
                return True
        return False

    def _is_previous_line_comment_end(self, previous_line:str, current_line:str)->bool:
        """!
        @brief Check if the previous line is the end of a comment block

        @param previous_line (string): previous line previous line of the test file
        @param current_line (string): current line current line of the test file

        @return bool: True if the previous line is the end of a comment block, else False
        """
        if (self.comment_data is not None) and (previous_line is not None):
            if ((0 == previous_line.find(self.comment_data["singleLine"])) and
                (0 != current_line.find(self.comment_data["singleLine"]))):
                return True
        return False

    def find_next_comment_block(self)->bool:
        """!
        @brief Scan the current file from the current location to find a copyright comment block

        @return bool: True if comment block found, else False if end of file found before next
                      comment block
        """

        # initialize working variables
        previous_line = ""
        previous_line_off = None
        self.comment_blk_strt_off = None
        self.comment_blk_eol_off = None

        comment_block_found = False

        while not comment_block_found:
            # Read the test line
            current_line_offset = self._input_file.tell()
            current_line = self._input_file.readline()
            if not current_line:
                break

            # Check for comment block start or end
            if self.comment_blk_strt_off is None:
                if self._is_current_line_comment_start(current_line):
                    # Process comment block start
                    self.comment_blk_strt_off = current_line_offset
                elif self._is_previous_line_comment_start(previous_line, current_line):
                    # Process comment block start
                    self.comment_blk_strt_off = previous_line_off
            else:
                if self._is_current_line_comment_end(current_line):
                    # Process comment block end
                    self.comment_blk_sol_off = current_line_offset
                    self.comment_blk_eol_off = current_line_offset + len(current_line)
                    comment_block_found = True
                elif self._is_previous_line_comment_end(previous_line, current_line):
                    # Process comment block end
                    self.comment_blk_sol_off = previous_line_off
                    self.comment_blk_eol_off = previous_line_off + len(previous_line)
                    comment_block_found = True

            # Move to the next line and return true to continue for each loop
            previous_line = current_line
            previous_line_off = current_line_offset

        # return if we found a comment block
        return comment_block_found
