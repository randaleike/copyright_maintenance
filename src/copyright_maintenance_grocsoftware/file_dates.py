"""@package file_date
Determine the creation date and last modification date of a given file
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

import os
import subprocess
import time
from datetime import datetime

DBG_MSG_NONE = 0
DBG_MSG_MINIMAL = 1
DBG_MSG_VERBOSE = 2
DBG_MSG_VERYVERBOSE = 3
DEBUG_LEVEL = DBG_MSG_NONE

def DebugPrint(messageLevel:int, message:str):
    """Print a debug message to the console if the input message level is
    greater than or equal to the current global debug threshold.

    Args:
        messageLevel (int): Debug level (DBG_MSG_NONE | DBG_MSG_MINIMAL | DBG_MSG_VERBOSE
                            | DBG_MSG_VERYVERBOSE) of the input message.
        message (string): Debug message text.
    """
    if DEBUG_LEVEL >= messageLevel:
        print ("Debug: "+message)


class GetFileSystemYears(object):
    """!
    File system creation and last modification identification class
    """
    def __init__(self, filePath:str):
        """!
        @brief Constructor
        @param filePath (string): Path and file name of the file to query
        """
        self._filePath = filePath

    def _cvtTimestampToYear(self, seconds:float) -> str|None:
        """!
        @brief Convert the input seconds timestamp to the year value
        @param seconds (float) Number of seconds since 01-Jan-1970
        @return str|None - Year value string corresponding to the input seconds or
                           None if there was a conversion error
        """
        try:
            dateStruct = time.localtime(seconds)
            return time.strftime("%Y", dateStruct)

        except OverflowError:
            print("ERROR: Overflow error on conversion of time epoch.")
            return None
        except OSError:
            print("ERROR: OS converstion error of time epoch.")
            return None

    def getFileYears(self)->tuple:
        """!
        @brief Get the file creation year and last modification n year
        @return tuple - creation year string, last modification year string
        """
        try:
            creationTime     = os.path.getctime(self._filePath)
            modificationTime = os.path.getmtime(self._filePath)

            creationYear     = self._cvtTimestampToYear(creationTime)
            modificationYear = self._cvtTimestampToYear(modificationTime)
            return creationYear, modificationYear

        except OSError:
            print("ERROR: OS get file times error of time.")
            return None, None

class GetGitArchiveFileYears(object):
    """!
    File creation and last modification from git archive class
    """
    def __init__(self, filePath:str):
        """!
        @brief Constructor
        @param filePath (string): Path and file name of the file to query
        """
        self._filePath = filePath

    def _getCreationYear(self)->str|None:
        """!
        @brief Get the file creation year from the git archive
        @return str|None - creation year string or None if the git call failed
        """

        # Get the date file was added to the archive
        gitcmd = ["git", "log", "--diff-filter=A", "--format=%aI", self._filePath]

        try:
            gitStart = subprocess.run(gitcmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, check=True)

            startOutput = gitStart.stdout.decode('utf-8')
            if gitStart.returncode != 0:
                print("ERROR: Git creation date failed: "+str(startOutput))
                return None
            else:
                return startOutput[:4]
        except Exception as error:
            print("ERROR: Git creation date command failed for file: "+self._filePath)
            return None

    def _getLastModificationYear(self)->str|None:
        """!
        @brief Get the file last modification year from the git archive
        @return str|None - last modification year string or None if the git call failed
        """

        # Get the date file was last modified in the archive
        gitcmd = ["git", "log", "-1", "--format=%aI", self._filePath]

        try:
            gitMod = subprocess.run(gitcmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, check=True)

            modOutput = gitMod.stdout.decode('utf-8')
            if gitMod.returncode != 0:
                print("ERROR: Git last modification date failed: "+str(modOutput))
                return None
            else:
                return modOutput[:4]
        except:
            print("ERROR: Git last modification date command failed for file: "+self._filePath)
            return None

    def getFileYears(self)->tuple:
        """!
        @brief Get the file creation year and last modification n year
        @return tuple - creation year string, last modification year string
        """
        # Get the date file was added to the archive
        startOutput = self._getCreationYear()

        # Check for error
        if startOutput is not None:
            # Get the date file was last modified in the archive
            modOutput = self._getLastModificationYear()

            # Check for error
            if modOutput is None:
                return None, None
            else:
                return startOutput, modOutput
        else:
            return None, None

class GetFileYears(object):
    """!
    Get the file creation and last modification years for the file
    """
    def __init__(self, filePath:str):
        """!
        @brief Constructor
        @param filePath (string): Path and file name of the file to query
        """
        self._filePath = filePath

    def getFileYears(self)->tuple:
        """Get the file creation year and last modification n year

        Returns:
            tuple creation year string, last modification year string
        """
        if (os.path.exists(self._filePath) and (os.path.isfile(self._filePath))):
            if (os.path.exists(".git") and (os.path.isdir(".git"))):
                return GetGitArchiveFileYears(self._filePath).getFileYears()
            else:
                return GetFileSystemYears(self._filePath).getFileYears()
        else:
            print("ERROR: File: \""+self._filePath+"\" does not exist or is not a file.")
            return None, None
