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
    def __init__(self, inputFile):
        """!
        @brief Constructor
        @param inputFile (file): Open file object to read and identify the copyright block in.
        """
        ## File offset of the copyright comment block start if found or None if not found
        self.commentBlkStrtOff = None
        ## File offset of the copyright comment block end if found or None if not found
        self.commentBlkEOLOff = None
        ## File to parse and look for the copyright message
        self._inputFile = inputFile
        ## False until a non-blank line is found
        self._foundtextStart = False

    def _isCurrentLineCommentStart(self, currentLine:str)->bool:
        """!
        @brief Determine if the input current line is the start of a comment block

        @param currentLine (string): current line current line of the test file

        @return bool: True if this line is the start of a comment block, else False
        """
        if self._foundtextStart:
            return False
        else:
            startMatch = re.search(r'\S', currentLine)
            if startMatch is not None:
                self._foundtextStart = True
                return True
            else:
                return False

    def _isCurrentLineCommentEnd(self, currentLine:str)->bool:
        """!
        @brief Check if the line is the end of a comment block

        @param currentLine (string): current line current line of the test file

        @return bool: True if the current line is the end of a comment block, else False
        """
        if self._foundtextStart:
            endMatch = re.search(r'\S', currentLine)
            if endMatch is not None:
                return False
            else:
                self._foundtextStart = False     # Reset text file block start
                return True
        else:
            return False

    def findNextCommentBlock(self):
        """!
        @brief Scan the current file from the current location to find a comment block

        @return bool: True if comment block found, else False
        """

        # initialize working variables
        previousLine = ""
        previousLineOffset = None

        self.commentBlkStrtOff = None
        self.commentBlkEOLOff = None

        commentBlockFound = False
        self.commentBlkEOLOff = None
        while not commentBlockFound:
            # Read the test line
            currentLineOffset = self._inputFile.tell()
            currentLine = self._inputFile.readline()
            if not currentLine:
                # Check for special text file case
                if ((self.commentBlkStrtOff is not None) and
                    (self.commentBlkEOLOff is None)):
                    self.commentBlkEOLOff = previousLineOffset + len(previousLine)
                    commentBlockFound = True
                break

            # Check for comment block start or end
            if self._isCurrentLineCommentStart(currentLine):
                # Process comment block start
                self.commentBlkStrtOff = currentLineOffset
            elif self._isCurrentLineCommentEnd(currentLine):
                # Process comment block end
                self.commentBlkEOLOff = currentLineOffset + len(currentLine)
                commentBlockFound = True

            # Move to the next line and return true to continue for each loop
            previousLine = currentLine
            previousLineOffset = currentLineOffset

        # return if we found a comment block
        return commentBlockFound

class CommentParams(object):
    """!
    Comment marker definitions and static selection methods
    """
    ##C/C++/Typescript/Javascript comment marker dictionary
    cCommentParms =   {'blockStart': "/*", 'blockEnd': "*/", 'blockLineStart': "", 'singleLine': "//"}
    ##Python comment marker dictionary
    pyCommentParms =  {'blockStart': "\"\"\"", 'blockEnd':"\"\"\"", 'blockLineStart': "", 'singleLine': "#"}
    ##Bash shell comment marker dictionary
    shCommentParms =  {'blockStart': None, 'blockEnd': None, 'blockLineStart': "#", 'singleLine': "#"}
    ##Batch comment marker dictionary
    batCommentParms = {'blockStart': None, 'blockEnd': None, 'blockLineStart': "REM ", 'singleLine': "REM "}

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
    def getCommentMarkers(filename:str)->dict|None:
        """!
        @brief Determine the comment marker values from the file name

        @param filename (string): File name

        @return dictionary: commentBlockDelim entry that matches the file extension or
                            None if no extension match is found
        """
        nameExt = os.path.splitext(filename)
        extension = nameExt[1]

        # pylint: disable=locally-disabled, disable=C0201
        if extension in CommentParams.commentBlockDelim.keys():
            return CommentParams.commentBlockDelim[extension]
        else:
            return None


class CommentBlock(object):
    """!
    Identify the start and end of a comment block
    """
    def __init__(self, inputFile, commentMarkers:dict|None = None):
        """!
        @brief Constructor
        @param inputFile (file): Open file object to read and identify the copyright block in.
        @param commentMarkers (CommentBlockDelim element): Comment deliminter markers for the input file type.
        """
        ## File offset of the copyright comment block start if found or None if not found
        self.commentBlkStrtOff = None
        ## File offset of the copyright comment block end end of line if found or None if not found
        self.commentBlkEOLOff = None
        ## File offset of the copyright comment block end start of line if found or None if not found
        self.commentBlkSOLOff = None
        ## File to parse and look for the copyright message
        self._inputFile = inputFile
        ## Comment block markers typical for the file type
        self.commentData = commentMarkers

    def _isCurrentLineCommentStart(self, currentLine:str)->bool:
        """!
        @brief Determine if the input current line is the start of a comment block

        @param currentLine (string): current line current line of the test file

        @return bool: True if this line is the start of a comment block, else False
        """
        if ((self.commentData is not None) and
            (self.commentData["blockStart"] is not None)):
            if 0 == currentLine.find(self.commentData["blockStart"]):
                return True
        return False

    def _isPreviousLineCommentStart(self, previousLine:str, currentLine:str)->bool:
        """!
        @brief Check if the previous line is the start of a comment block

        @param previousLine (string): previous line previous line of the test file
        @param currentLine (string): current line current line of the test file

        @return bool: True if the previous line is the start of a comment block, else False
        """
        if (self.commentData is not None) and (previousLine is not None):
            if ((0 == previousLine.find(self.commentData["singleLine"])) and
                (0 == currentLine.find(self.commentData["singleLine"]))):
                return True
        return False

    def _isCurrentLineCommentEnd(self, currentLine:str)->bool:
        """!
        @brief Check if the line is the end of a comment block

        @param currentLine (string): current line current line of the test file

        @return bool: True if the current line is the end of a comment block, else False
        """
        if ((self.commentData is not None) and
            (self.commentData["blockEnd"] is not None)):
            if -1 != currentLine.find(self.commentData["blockEnd"]):
                return True
        return False

    def _isPreviousLineCommentEnd(self, previousLine:str, currentLine:str)->bool:
        """!
        @brief Check if the previous line is the end of a comment block

        @param previousLine (string): previous line previous line of the test file
        @param currentLine (string): current line current line of the test file

        @return bool: True if the previous line is the end of a comment block, else False
        """
        if (self.commentData is not None) and (previousLine is not None):
            if ((0 == previousLine.find(self.commentData["singleLine"])) and
                (0 != currentLine.find(self.commentData["singleLine"]))):
                return True
        return False

    def findNextCommentBlock(self)->bool:
        """!
        @brief Scan the current file from the current location to find a copyright comment block

        @return bool: True if comment block found, else False if end of file found before next
                      comment block
        """

        # initialize working variables
        previousLine = ""
        previousLineOffset = None
        self.commentBlkStrtOff = None
        self.commentBlkEOLOff = None

        commentBlockFound = False

        while not commentBlockFound:
            # Read the test line
            currentLineOffset = self._inputFile.tell()
            currentLine = self._inputFile.readline()
            if not currentLine:
                break

            # Check for comment block start or end
            if self.commentBlkStrtOff is None:
                if self._isCurrentLineCommentStart(currentLine):
                    # Process comment block start
                    self.commentBlkStrtOff = currentLineOffset
                elif self._isPreviousLineCommentStart(previousLine, currentLine):
                    # Process comment block start
                    self.commentBlkStrtOff = previousLineOffset
            else:
                if self._isCurrentLineCommentEnd(currentLine):
                    # Process comment block end
                    self.commentBlkSOLOff = currentLineOffset
                    self.commentBlkEOLOff = currentLineOffset + len(currentLine)
                    commentBlockFound = True
                elif self._isPreviousLineCommentEnd(previousLine, currentLine):
                    # Process comment block end
                    self.commentBlkSOLOff = previousLineOffset
                    self.commentBlkEOLOff = previousLineOffset + len(previousLine)
                    commentBlockFound = True

            # Move to the next line and return true to continue for each loop
            previousLine = currentLine
            previousLineOffset = currentLineOffset

        # return if we found a comment block
        return commentBlockFound
