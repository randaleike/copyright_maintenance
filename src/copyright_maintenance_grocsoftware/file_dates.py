"""@package copyright_maintenance
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

DBG_MSG_NONE = 0
DBG_MSG_MINIMAL = 1
DBG_MSG_VERBOSE = 2
DBG_MSG_VERYVERBOSE = 3
DEBUG_LEVEL = DBG_MSG_NONE

def debug_print(message_level:int, message:str):
    """!
    Print a debug message to the console if the input message level is
    greater than or equal to the current global debug threshold.

    @param message_level (int): Debug level (DBG_MSG_NONE | DBG_MSG_MINIMAL | DBG_MSG_VERBOSE
                                | DBG_MSG_VERYVERBOSE) of the input message.
    @param message (string): Debug message text.
    """
    if DEBUG_LEVEL >= message_level:
        print ("Debug: "+message)


class GetFileSystemYears():
    """!
    File system creation and last modification identification class
    """
    def __init__(self, file_path:str):
        """!
        @brief Constructor
        @param file_path (string): Path and file name of the file to query
        """
        self._file_path = file_path

    def cvt_timestamp_to_year(self, seconds:float) -> str:
        """!
        @brief Convert the input seconds timestamp to the year value
        @param seconds (float) Number of seconds since 01-Jan-1970
        @return str - Year value string corresponding to the input seconds or
                           None if there was a conversion error
        """
        try:
            local_date_struct = time.localtime(seconds)
            return time.strftime("%Y", local_date_struct)

        except OverflowError:
            print("ERROR: Overflow error on conversion of time epoch.")
            return None
        except OSError:
            print("ERROR: OS converstion error of time epoch.")
            return None

    def get_file_years(self)->tuple:
        """!
        @brief Get the file creation year and last modification n year
        @return tuple - creation year string, last modification year string
        """
        try:
            creation_time     = os.path.getctime(self._file_path)
            modification_time = os.path.getmtime(self._file_path)

            creation_year     = self.cvt_timestamp_to_year(creation_time)
            modification_year = self.cvt_timestamp_to_year(modification_time)
            return creation_year, modification_year

        except OSError:
            print("ERROR: OS get file times error of time.")
            return None, None

class GetGitArchiveFileYears():
    """!
    File creation and last modification from git archive class
    """
    def __init__(self, file_path:str):
        """!
        @brief Constructor
        @param file_path (string): Path and file name of the file to query
        """
        ## Path/file name of the file to process
        self._file_path = file_path

    def get_creation_year(self)->str:
        """!
        @brief Get the file creation year from the git archive
        @return str - creation year string or None if the git call failed
        """

        # Get the date file was added to the archive
        gitcmd = ["git", "log", "--diff-filter=A", "--format=%aI", self._file_path]

        try:
            git_start = subprocess.run(gitcmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, check=True)

            start_output = git_start.stdout.decode('utf-8')
            if git_start.returncode != 0:
                print("ERROR: Git creation date failed: "+str(start_output))
                ret_str = None
            else:
                ret_str = start_output[:4]
            return ret_str
        except subprocess.CalledProcessError:
            print("ERROR: Git creation date command failed for file: "+self._file_path)
            return None

    def get_last_modification_year(self)->str:
        """!
        @brief Get the file last modification year from the git archive
        @return str - last modification year string or None if the git call failed
        """

        # Get the date file was last modified in the archive
        gitcmd = ["git", "log", "-1", "--format=%aI", self._file_path]

        try:
            gitmod = subprocess.run(gitcmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, check=True)

            mod_output = gitmod.stdout.decode('utf-8')
            if gitmod.returncode != 0:
                print("ERROR: Git last modification date failed: "+str(mod_output))
                ret_str = None
            else:
                ret_str = mod_output[:4]
            return ret_str
        except subprocess.CalledProcessError:
            print("ERROR: Git last modification date command failed for file: "+self._file_path)
            return None

    def get_file_years(self)->tuple:
        """!
        @brief Get the file creation year and last modification n year
        @return tuple - creation year string, last modification year string
        """
        # Get the date file was added to the archive
        start_output = self.get_creation_year()
        create_yr = None
        last_mod_yr = None

        # Check for error
        if start_output is not None:
            # Get the date file was last modified in the archive
            mod_output = self.get_last_modification_year()

            # Check for error
            if mod_output is not None:
                create_yr = start_output
                last_mod_yr = mod_output

        return create_yr, last_mod_yr

def get_file_years(file_path:str)->tuple:
    """!
    @brief Get the file creation year and last modification n year
    @param file_path {string} Path/Filename of file to fetch years from
    @return tuple - creation year string, last modification year string
    """
    create_yr = None
    last_mod_yr = None

    if (os.path.exists(file_path) and (os.path.isfile(file_path))):
        if (os.path.exists(".git") and (os.path.isdir(".git"))):
            create_yr, last_mod_yr = GetGitArchiveFileYears(file_path).get_file_years()
        else:
            create_yr, last_mod_yr =  GetFileSystemYears(file_path).get_file_years()
    else:
        print("ERROR: File: \""+file_path+"\" does not exist or is not a file.")
    return create_yr, last_mod_yr
