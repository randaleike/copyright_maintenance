"""@package copyright_maintenance
OS shell utility functions
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
    def stream_edit(self, input_file_name:str, searchregx:str,
                    replaceregx:str, output_file_name:str = None)->bool:
        """!
        @brief Inline stream editor function

        @param input_file_name (string): file_path and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for
        @param replaceregx (regex string): Regx string describing the replacement string
        @param output_file_name (string): file_path and name of the output file or None to
                                        force inline change

        @return bool - True if replacement was successful, False if there was an error
        """
        subproc_cmd_list = []

        subproc_cmd_list.append("sed")
        if output_file_name is None:
            subproc_cmd_list.append("-i")
            output_file = None
        else:
            try:
                output_file = open(output_file_name, 'wt', encoding='utf-8') # pylint: disable=consider-using-with
            except OSError:
                print("ERROR: Output file creation "+output_file_name+" failed")
                return False

        subproc_cmd_list.append(r"s/"+searchregx+"/"+replaceregx+"/g")
        subproc_cmd_list.append(input_file_name)

        try:
            subprocess.run(subproc_cmd_list, stdout=output_file, encoding='utf-8', check=True)
            if output_file is not None:
                output_file.close()
            return True

        except subprocess.CalledProcessError:
            error_str = "ERROR: Stream edit '"
            error_str += input_file_name
            error_str += "' replace '"
            error_str += searchregx
            error_str += "' with '"
            error_str += replaceregx
            error_str += "' failed."
            print(error_str)
            if output_file is not None:
                output_file.close()
            return False

        except TimeoutError:
            print("ERROR: Stream edit '"+input_file_name+"' timeout failure.")
            if output_file is not None:
                output_file.close()
            return False

    def seach_file(self, input_file_name:str, searchregx:str)->tuple:
        """!
        @brief String search within a file

        @param input_file_name (string): file_path and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for

        @return bool - True if found, False if there was an error
        @return string list - matching string(s) or None if there was an error
        """
        subproc_cmd_list = []
        subproc_cmd_list.append("grep")
        subproc_cmd_list.append(searchregx)
        subproc_cmd_list.append(input_file_name)

        try:
            check = subprocess.run(subproc_cmd_list, encoding='utf-8',
                                   stdout=subprocess.PIPE, check=True)
            grep_return = check.stdout
            return True, grep_return

        except subprocess.CalledProcessError:
            print("ERROR: File text search '"+input_file_name+"' for '"+searchregx+"' failed.")
            return False, None

        except TimeoutError:
            print("ERROR: File text search '"+input_file_name+"' timeout failure.")
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
        self._windows_version = platform.release()

    def stream_edit(self, input_file_name:str, searchregx:str, replaceregx:str,
                    output_file_name:str = None)->bool:
        """!
        @brief Inline stream editor function

        @param input_file_name (string): file_path and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for
        @param replaceregx (regex string): Regx string describing the replacement string
        @param output_file_name (string): file_path and name of the output file or None to
                                        force inline change

        @return bool - True if replacement was successful, False if there was an error
        """
        subproc_cmd_list = []

        replace_cmd = "-replace \'"
        replace_cmd+= searchregx
        replace_cmd+= "\', \'"
        replace_cmd+= replaceregx
        replace_cmd+= "\'"

        if output_file_name is None:
            output_file_cmd = " | Out-File -encoding ASCII "+input_file_name
        else:
            output_file_cmd = " | Out-File -encoding ASCII "+output_file_name

        if self._windows_version < 10:
            cmdtext = "\"(gc "
            cmdtext+= input_file_name
            cmdtext+= ") "+replace_cmd+output_file_cmd
            cmdtext+= "\""

            subproc_cmd_list.append("powershell")
            subproc_cmd_list.append("-Command")
            subproc_cmd_list.append(cmdtext)
        else:
            cmdtext = "(Get-Content "
            cmdtext+= input_file_name
            cmdtext+= ") "+replace_cmd+output_file_cmd
            subproc_cmd_list.append(cmdtext)

        try:
            subprocess.run(subproc_cmd_list, encoding='utf-8', check=True)
            return True

        except subprocess.CalledProcessError:
            error_str = "ERROR: Stream edit '"
            error_str += input_file_name
            error_str += "' replace '"
            error_str += searchregx
            error_str += "' with '"
            error_str += replaceregx
            error_str += "' failed."
            print(error_str)
            return False

        except TimeoutError:
            print("ERROR: Stream edit '"+input_file_name+"' timeout failure.")
            return False

    def seach_file(self, input_file_name:str, searchregx:str)->tuple:
        """!
        @brief String search within a file

        @param input_file_name (string): file_path and name of the input file
        @param searchregx (regx string): Regx string describing the string to search for

        @return bool - True if found, False if there was an error
        @return string list - matching string(s) or None if there was an error
        """
        subproc_cmd_list = []
        subproc_cmd_list.append("powershell")
        subproc_cmd_list.append("-Command")
        subproc_cmd_list.append("sls "+searchregx+" "+input_file_name)

        try:
            check = subprocess.run(subproc_cmd_list, encoding='utf-8',
                                   stdout=subprocess.PIPE, check=True)
            grep_return = check.stdout
            return True, grep_return

        except subprocess.CalledProcessError:
            print("ERROR: File text search '"+input_file_name+"' for '"+searchregx+"' failed.")
            return False, None

        except TimeoutError:
            print("ERROR: File text search '"+input_file_name+"' timeout failure.")
            return False, None

def get_command_shell():
    """!
    @brief Get the os specific shell object

    @return OS appropriate Command shell object or None if the OS is unknown
    """
    os_type = platform.system()
    return_shell = None

    if os_type == 'Linux':
        return_shell = LinuxShell()
    elif os_type == 'Windows':
        return_shell = WindowsPowerShell()
    else:
        print("ERROR: Unsupported OS "+os_type)

    return return_shell
