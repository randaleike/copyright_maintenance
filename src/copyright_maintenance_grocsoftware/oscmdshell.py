"""@package utility
Common utility functions
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

import platform
import subprocess

class LinuxShell:
    """!
    @brief Linux shell version
    """
    def streamEdit(self, inputFileName:str, searchregx:str, replaceregx:str, outputFileName:str|None = None)->bool:
        """!
        @brief Inline stream editor function

        @param inputFileName (string): Filepath and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for
        @param replaceregx (regex string): Regx string describing the replacement string
        @param outputFileName (string|None): Filepath and name of the output file or None to
                                        force inline change

        @return bool - True if replacement was successful, False if there was an error
        """
        subprocCmdList = []

        subprocCmdList.append("sed")
        if outputFileName is None:
            subprocCmdList.append("-i")
            outFile = None
        else:
            try:
                outFile = open(outputFileName, 'wt', encoding='utf-8')
            except:
                print("ERROR: Output file creation "+outputFileName+" failed")
                return False

        subprocCmdList.append(r"s/"+searchregx+"/"+replaceregx+"/g")
        subprocCmdList.append(inputFileName)

        try:
            sedProc = subprocess.run(subprocCmdList, stdout=outFile, encoding='utf-8', check=True)
            if outFile is not None:
                outFile.close()
            return True

        except Exception as error:
            #print("ERROR: Stream edit failed "+str(error))
            print("ERROR: Stream edit '"+inputFileName+"' replace '"+searchregx+"' with '"+replaceregx+"' failed.")
            if outFile is not None:
                outFile.close()
            return False

    def seachFile(self, inputFileName:str, searchregx:str)->tuple:
        """!
        @brief String search within a file

        @param inputFileName (string): Filepath and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for

        @return bool - True if found, False if there was an error
        @return string list - matching string(s) or None if there was an error
        """
        subprocCmdList = []
        subprocCmdList.append("grep")
        subprocCmdList.append(searchregx)
        subprocCmdList.append(inputFileName)

        try:
            check = subprocess.run(subprocCmdList, encoding='utf-8', stdout=subprocess.PIPE, check=True)
            grepRet = check.stdout
            return True, grepRet

        except Exception as error:
            #print("ERROR: File text search failed "+str(error))
            print("ERROR: File text search '"+inputFileName+"' for '"+searchregx+"' failed.")
            return False, None

class WindowsPowerShell:
    """!
    @brief Windows shell version
    """
    def __init__(self):
        """!
        @brief Default constructor
        """
        ## Windows version used to determine the correct tool and sequence
        self._windowsVersion = platform.release()

    def streamEdit(self, inputFileName:str, searchregx:str, replaceregx:str, outputFileName:str|None = None)->bool:
        """!
        @brief Inline stream editor function

        @param inputFileName (string): Filepath and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for
        @param replaceregx (regex string): Regx string describing the replacement string
        @param outputFileName (string): Filepath and name of the output file or None to
                                        force inline change

        @return bool - True if replacement was successful, False if there was an error
        """
        subprocCmdList = []

        replaceCmd = "-replace \'"
        replaceCmd+= searchregx
        replaceCmd+= "\', \'"
        replaceCmd+= replaceregx
        replaceCmd+= "\'"

        if outputFileName is None:
            outFileCmd = " | Out-File -encoding ASCII "+inputFileName
        else:
            outFileCmd = " | Out-File -encoding ASCII "+outputFileName

        if self._windowsVersion < 10:
            cmdtext = "\"(gc "
            cmdtext+= inputFileName
            cmdtext+= ") "+replaceCmd+outFileCmd
            cmdtext+= "\""

            subprocCmdList.append("powershell")
            subprocCmdList.append("-Command")
            subprocCmdList.append(cmdtext)
        else:
            cmdtext = "(Get-Content "
            cmdtext+= inputFileName
            cmdtext+= ") "+replaceCmd+outFileCmd
            subprocCmdList.append(cmdtext)

        try:
            subprocess.run(subprocCmdList, encoding='utf-8', check=True)
            return True

        except Exception as error:
            #print("ERROR: Stream edit failed "+str(error))
            print("ERROR: Stream edit '"+inputFileName+"' replace '"+searchregx+"' with '"+replaceregx+"' failed.")
            return False

    def seachFile(self, inputFileName:str, searchregx:str)->tuple:
        """!
        @brief String search within a file

        @param inputFileName (string): Filepath and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for

        @return bool - True if found, False if there was an error
        @return string list - matching string(s) or None if there was an error
        """
        subprocCmdList = []
        subprocCmdList.append("powershell")
        subprocCmdList.append("-Command")
        subprocCmdList.append("sls "+searchregx+" "+inputFileName)

        try:
            check = subprocess.run(subprocCmdList, encoding='utf-8', stdout=subprocess.PIPE, check=True)
            grepRet = check.stdout
            return True, grepRet

        except Exception as error:
            #print("ERROR: File text search failed "+str(error))
            print("ERROR: File text search '"+inputFileName+"' for '"+searchregx+"' failed.")
            return False, None

def GetCommandShell()->LinuxShell|WindowsPowerShell|None:
    """!
    @brief Get the os specific shell object

    @return OS appropriate Command shell object or None if the OS is unknown
    """
    osType = platform.system()

    if osType == 'Linux':
        return LinuxShell()
    elif osType == 'Windows':
        return WindowsPowerShell()
    else:
        print("ERROR: Unsupported OS "+osType)
        return None
