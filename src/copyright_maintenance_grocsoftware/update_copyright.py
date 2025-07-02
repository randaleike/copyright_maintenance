"""@package update_copyright
Scan source files and update copyright years

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

from copyright_maintenance_grocsoftware.file_dates import GetFileYears
from copyright_maintenance_grocsoftware.oscmdshell import GetCommandShell

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightGenerator
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightFinder
from copyright_maintenance_grocsoftware.comment_block import CommentBlock
from copyright_maintenance_grocsoftware.comment_block import CommentParams

DBG_MSG_NONE = 0
DBG_MSG_MINIMAL = 1
DBG_MSG_VERBOSE = 2
DBG_MSG_VERYVERBOSE = 3
DEBUG_LEVEL = DBG_MSG_NONE

def DebugPrint(messageLevel, message):
    """
    @brief Print a debug message to the console if the input message level is
           greater than or equal to the current global debug threshold.

    @param messageLevel (int): Debug level (DBG_MSG_MINIMAL | DBG_MSG_VERBOSE
                                            | DBG_MSG_VERYVERBOSE) of the input message.
    @param message (string): Debug message text.
    """
    if DEBUG_LEVEL >= messageLevel:
        print ("Debug: "+message)

class CopyrightCommentBlock(CommentBlock):
    """!
    Identify the start and end of a comment blocks and determine if the
    copyright message is in the block(s)
    """
    def __init__(self, inputFile,
                 commentMarkers:dict|None = None,
                 copyRightParser = None):
        """!
        @brief Constructor

        @param self(CopyrightCommentBlock) - Object reference
        @param inputFile(file) - Open file object to read and identify the copyright block in.
        @param commentMarkers(CommentBlockDelim element) - Comment deliminter markers for the input file type.
        @param copyRightParser(CopyrightParse object) - Copyright parser object or None if default
                                                        parser is to be used.

        @return pass
        """
        super().__init__(inputFile, commentMarkers)

        if copyRightParser is None:
            self._copyrightParser = CopyrightParseEnglish()
        else:
            self._copyrightParser = copyRightParser

        self.inputFile = inputFile                  ##!< File to parse and look for the copyright message
        self.copyrightBlockData = []                ##!< List of copyright comment block dictionary entries found

    def _isCopyrightCommentBlock(self, commentBlkStrtOff:int|None, commentBlkEndOff:int|None)->tuple:
        """!
        @brief Check if the copyright message is within the current comment block

        @param commentBlkStrtOff (fileoffset): File offset of the comment block start
        @param commentBlkEndOff (fileoffset): File offset of the comment block start


        @return bool: True if copyright message is found, else false
        @return dictionary: {'lineOffset': Starting file offset of the copyright message line,
                             'text': Current copyright text line}
        """
        if (commentBlkStrtOff is not None) and (commentBlkEndOff is not None):
            self.inputFile.seek(commentBlkStrtOff)
            copyrightFind = CopyrightFinder(self._copyrightParser)
            return copyrightFind.findNextCopyrightMsg(self.inputFile, commentBlkStrtOff, commentBlkEndOff)
        else:
            return False, None

    def _isfindNextCopyrightBlock(self)->dict:
        """!
        @brief Scan the current file from the current location to find a copyright comment block

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright comment block location data dictionary
                            {'blkStart': copyright comment block starting file offset,
                             'blkEndEOL': copyright comment block ending file offset,
                             'blkEndSOL': copyright comment block ending line start file offset,
                             'copyrightMsgs': list of copyright data dictionaries
                                              [{'lineOffset': Starting file offset of the copyright message line,
                                                'text': Current copyright text line}]
                            }
        """
        copyrightBlockFound = False

        if self.findNextCommentBlock():
            # Check if the block is a copyright block
            locationDict = {'blkStart': self.commentBlkStrtOff,
                            'blkEndEOL': self.commentBlkEOLOff,
                            'blkEndSOL': self.commentBlkSOLOff,
                            'copyrightMsgs': []
                            }

            # Check if there are any copyright lines in the block
            startLocation = self.commentBlkStrtOff
            while startLocation < self.commentBlkEOLOff:
                copyrightLineFound, copyrightLocation = self._isCopyrightCommentBlock(startLocation, self.commentBlkEOLOff)
                if copyrightLineFound:
                    startLocation = copyrightLocation['lineOffset'] + len(copyrightLocation['text'])
                    locationDict['copyrightMsgs'].append(copyrightLocation)
                    copyrightBlockFound = True
                else:
                    break

        return copyrightBlockFound, locationDict

    def findCopyrightBlocks(self)->list:
        """!
        @brief Scan the file for the comment block

        @return (list): List of copyright block comment block location dictionaries
                        [{'blkStart': copyright comment block starting file offset,
                          'blkEndEOL': copyright comment block ending file offset,
                          'blkEndSOL': copyright comment block ending line start file offset,
                          'copyrightMsgs': list of copyright data dictionaries
                                          [{'lineOffset': Starting file offset of the copyright message line,
                                            'text': Current copyright text line}]
                        }]
        """
        self.inputFile.seek(0)
        self.copyrightBlockData.clear()

        # Scan the file
        copyrightBlockFound = True
        while copyrightBlockFound:
            copyrightBlockFound, location = self._isfindNextCopyrightBlock()
            if copyrightBlockFound:
                self.copyrightBlockData.append(location)

        return self.copyrightBlockData

def InsertNewCopyrightBlock(inputFile, outputFilename:str, commentBlockData:dict,
                            commentMarker:dict, newCopyRightMsg:str, newEula:list|None = None)->bool:
    """!
    @brief Write a new file with the updated copyright message

    @param inputFile (file): Existing text file
    @param outputFilename (filename string): Name of the file to output updated text to
    @param commentBlockData (dictionary): Comment block locations to update
    @param commentMarker (dictionary): commentBlockDelim object to use for comment block replacement
    @param newCopyRightMsg (string): New copyright message to write to the new file
    @param newEula (list of strings): New license text to add to the copyright comment block

    @return Bool - True if new file was written, False if an error occured.
    """
    try:
        outputFile = open(outputFilename, mode='wt', encoding="utf-8")

        # Copy the first chunk of the file
        inputFile.seek(0)
        if commentBlockData['blkStart'] != 0:
            header = inputFile.read(commentBlockData['blkStart'])
            outputFile.write(header)

        # Output start of the comment block
        newLine = commentMarker['blockStart']+"\n"
        outputFile.write(newLine)

        # Insert the new copyright and licence text
        newLine = commentMarker['blockLineStart']+" "+newCopyRightMsg+"\n"
        outputFile.write(newLine)

        # Determine if we should update EULA
        if newEula is not None:
            newLine = commentMarker['blockLineStart']+"\n"
            outputFile.write(newLine)

            # Insert new EULA
            for licenceLine in newEula:
                newLine = commentMarker['blockLineStart']+" "+licenceLine+"\n"
                outputFile.write(newLine)
        else:
            # Copy old EULA
            copyrightLocation = commentBlockData['copyrightMsgs'][0]
            copyrightEnd = copyrightLocation['lineOffset'] + len(copyrightLocation['text'])
            inputFile.seek(copyrightEnd)
            currentLineOffset = copyrightEnd
            while currentLineOffset < commentBlockData['blkEndSOL']:
                newLine = commentMarker['blockLineStart']+" "+inputFile.readline()
                outputFile.write(newLine)
                currentLineOffset = inputFile.tell()

        # Output the comment block end
        newLine = commentMarker['blockEnd']+"\n"
        outputFile.write(newLine)

        # Copy the remainder of the file
        inputFile.seek(commentBlockData['blkEndEOL'])
        while newLine:
            newLine = inputFile.readline()
            outputFile.write(newLine)

        outputFile.close()
        return True

    except:
        print("ERROR: Unable to open file \""+outputFilename+"\" for writing as text file.")
        return False

def UpdateCopyRightYears(fileName:str):
    """!
    @brief Update the copyright years in the copyright message of the input file

    @param fileName(string): path and name of file to update
    """
    fileYearQuery = GetFileYears(fileName)
    creationYrStr, modificationYrStr = fileYearQuery.getFileYears()

    if creationYrStr is None:
        print ("None returned from GetFileYears() for creation year")
        creationYear = datetime.datetime.now().year
    else:
        creationYear = int(creationYrStr)

    if modificationYrStr is None:
        print ("None returned from GetFileYears() for modification year")
        modificationYear = datetime.datetime.now().year
    else:
        modificationYear = int(modificationYrStr)

    DebugPrint(DBG_MSG_MINIMAL, "Creation Year:     "+str(creationYear))
    DebugPrint(DBG_MSG_MINIMAL, "Modification Year: "+str(modificationYear))

    with open(fileName, "rt", encoding="utf-8") as testFile:
        # Get a copyright message parser and comment block parser
        copyrightParser = CopyrightParseEnglish()
        copyrightGen = CopyrightGenerator(copyrightParser)
        commentProcessor = CopyrightCommentBlock(testFile,
                                                CommentParams.getCommentMarkers(fileName),
                                                copyrightParser)
        # Find all copyright comment blocks
        copyrightMsgList = commentProcessor.findCopyrightBlocks()
        if copyrightMsgList:
            # Process the old message
            oldMsg = copyrightMsgList[0]['copyrightMsgs'][-1]['text']
            oldMsg = oldMsg.rstrip()
            copyrightParser.parseCopyrightMsg(oldMsg)

            # Get the new message
            msgChanged, newMsg = copyrightGen.getNewCopyrightMsg(creationYear, modificationYear)
            DebugPrint(DBG_MSG_MINIMAL, "Old copyright: "+oldMsg)
            DebugPrint(DBG_MSG_MINIMAL, "New copyright: "+newMsg)
            DebugPrint(DBG_MSG_MINIMAL, "New copyright changed: "+str(msgChanged))

            if msgChanged:
                GetCommandShell().streamEdit(fileName, oldMsg, newMsg)
