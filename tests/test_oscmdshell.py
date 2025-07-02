"""@package test_programmer_tools
Unittest for programmer base tools utility

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

from unittest.mock import patch, MagicMock, mock_open

import platform
import io
import contextlib
import subprocess

from dir_init import TESTFILEPATH
from dir_init import pathincsetup
pathincsetup()
testFileBaseDir = TESTFILEPATH

from copyright_maintenance_grocsoftware.oscmdshell import GetCommandShell
from copyright_maintenance_grocsoftware.oscmdshell import LinuxShell
from copyright_maintenance_grocsoftware.oscmdshell import WindowsPowerShell


class TestUnittest01GetShell:
    """!
    @brief Unit test for the GetCommandShell class
    """
    def test01_get_linux_shell(self):
        """!
        @brief Test GetCommandShell()
        """
        with patch('platform.system', MagicMock(return_value='Linux')):
            shell = GetCommandShell()
            assert isinstance(shell, LinuxShell)

    def test02_get_windows_shell(self):
        """!
        @brief Test GetCommandShell()
        """
        with patch('platform.system', MagicMock(return_value='Windows')):
            shell = GetCommandShell()
            assert isinstance(shell, WindowsPowerShell)

    def test03_get_shell_failed(self):
        """!
        @brief Test GetCommandShell()
        """
        output = io.StringIO()
        with patch('platform.system', MagicMock(return_value='SomethingElse')):
            with contextlib.redirect_stdout(output):
                shell = GetCommandShell()
                assert shell is None
                assert output.getvalue() == "ERROR: Unsupported OS SomethingElse\n"

    def test04_get_shell_real_call(self):
        """!
        @brief Test GetCommandShell()
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            shell = GetCommandShell()
            osType = platform.system()

            if osType == 'Linux':
                assert isinstance(shell, LinuxShell)
            elif osType == 'Windows':
                assert isinstance(shell, WindowsPowerShell)
            else:
                assert shell is None
                assert output.getvalue() == "ERROR: Unsupported OS "+osType

    def test05_linux_shell_stream_edit_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        with patch("builtins.open", mock_open()):
            retCodePass = subprocess.CompletedProcess("", 0, "", "")
            with patch('subprocess.run', MagicMock(return_value = retCodePass)):
                shell = LinuxShell()
                assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025", "streamedit.out")

    def test06_linux_shell_stream_edit_inline_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        retCodePass = subprocess.CompletedProcess("", 0, "", "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            shell = LinuxShell()
            assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025")

    def test07_linux_shell_stream_edit_inline_output_open_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()) as mockOpen:
                mockOpen.return_value = None
                mockOpen.side_effect = Exception(FileNotFoundError)
                shell = LinuxShell()
                assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025", "testFile.out")
                assert output.getvalue() == "ERROR: Output file creation testFile.out failed\n"

    def test08_linux_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(OSError)
                shell = LinuxShell()
                assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test09_linux_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(TimeoutError)
                shell = LinuxShell()
                assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test10_linux_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(ValueError)
                shell = LinuxShell()
                assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test11_linux_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(subprocess.CalledProcessError(2, cmdMsg, outMsg, errMsg))
                shell = LinuxShell()
                assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test12_linux_shell_stream_edit_inline_error_with_output_file(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()):
                retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
                with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                    subproc.side_effect = Exception(OSError)
                    shell = LinuxShell()
                    assert not shell.streamEdit("testFilePath", "2022-2024", "2022-2025", "streamedit.out")
                    assert output.getvalue() == "ERROR: Stream edit 'testFilePath' replace '2022-2024' with '2022-2025' failed.\n"

    def test13_linux_shell_search_file(self):
        """!
        @brief Test shell.seachFile(), pass
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodePass = subprocess.CompletedProcess("", 0, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            shell = LinuxShell()
            status, retStr = shell.seachFile("shelltest.x", "Copyright")
            assert status
            assert retStr == testString

    def test14_linux_shell_search_file_fail(self):
        """!
        @brief Test shell.seachFile(), failure
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodeError = subprocess.CompletedProcess("", 2, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
            subproc.side_effect = Exception(OSError)
            shell = LinuxShell()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status, retStr = shell.seachFile("shelltest.x", "Kilroy was here")
                assert not status
                assert retStr is None
                assert output.getvalue() == "ERROR: File text search 'shelltest.x' for 'Kilroy was here' failed.\n"

    def test15_windows9_shell_stream_edit_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        with patch("builtins.open", mock_open()):
            retCodePass = subprocess.CompletedProcess("", 0, "", "")
            with patch('subprocess.run', MagicMock(return_value = retCodePass)):
                with patch('platform.release', MagicMock(return_value = 9)):
                    shell = WindowsPowerShell()
                    assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025", "streamedit.out")

    def test16_windows9_shell_stream_edit_inline_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        retCodePass = subprocess.CompletedProcess("", 0, "", "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            with patch('platform.release', MagicMock(return_value = 9)):
                shell = WindowsPowerShell()
                assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025")

    def test17_windows9_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(OSError)
                with patch('platform.release', MagicMock(return_value = 9)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test18_windows9_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(TimeoutError)
                with patch('platform.release', MagicMock(return_value = 9)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test19_windows9_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(ValueError)
                with patch('platform.release', MagicMock(return_value = 9)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test20_windows9_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(subprocess.CalledProcessError(2, cmdMsg, outMsg, errMsg))
                with patch('platform.release', MagicMock(return_value = 9)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test21_windows9_shell_stream_edit_inline_error_with_output_file(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch("builtins.open", mock_open()):
                with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                    subproc.side_effect = Exception(OSError)
                    with patch('platform.release', MagicMock(return_value = 9)):
                        shell = WindowsPowerShell()
                        assert not shell.streamEdit("testFilePath", "2022-2024", "2022-2025", "streamedit.out")
                        assert output.getvalue() == "ERROR: Stream edit 'testFilePath' replace '2022-2024' with '2022-2025' failed.\n"

    def test22_windows9_shell_search_file(self):
        """!
        @brief Test shell.seachFile(), pass
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodePass = subprocess.CompletedProcess("", 0, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            with patch('platform.release', MagicMock(return_value = 9)):
                shell = WindowsPowerShell()
                status, retStr = shell.seachFile("shelltest.x", "Copyright")
                assert status
                assert retStr == testString

    def test23_windows9_shell_search_file_fail(self):
        """!
        @brief Test shell.seachFile(), failure
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodeError = subprocess.CompletedProcess("", 2, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
            subproc.side_effect = Exception(OSError)
            with patch('platform.release', MagicMock(return_value = 9)):
                shell = WindowsPowerShell()
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status, retStr = shell.seachFile("shelltest.x", "Kilroy was here")
                    assert not status
                    assert retStr is None
                    assert output.getvalue() == "ERROR: File text search 'shelltest.x' for 'Kilroy was here' failed.\n"

    def test24_windows11_shell_stream_edit_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        with patch("builtins.open", mock_open()):
            retCodePass = subprocess.CompletedProcess("", 0, "", "")
            with patch('subprocess.run', MagicMock(return_value = retCodePass)):
                with patch('platform.release', MagicMock(return_value = 11)):
                    shell = WindowsPowerShell()
                    assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025", "streamedit.out")

    def test25_windows11_shell_stream_edit_inline_pass(self):
        """!
        @brief Test shell.streamEdit(), good case
        """
        retCodePass = subprocess.CompletedProcess("", 0, "", "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            with patch('platform.release', MagicMock(return_value = 11)):
                shell = WindowsPowerShell()
                assert shell.streamEdit("testFile.in", "2022-2024", "2022-2025")

    def test26_windows11_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(OSError)
                with patch('platform.release', MagicMock(return_value = 11)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test27_windows11_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(TimeoutError)
                with patch('platform.release', MagicMock(return_value = 11)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test28_windows11_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(ValueError)
                with patch('platform.release', MagicMock(return_value = 11)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test29_windows11_shell_stream_edit_inline_error(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = Exception(subprocess.CalledProcessError(2, cmdMsg, outMsg, errMsg))
                with patch('platform.release', MagicMock(return_value = 11)):
                    shell = WindowsPowerShell()
                    assert not shell.streamEdit("testFile.in", "2022-2024", "2022-2025")
                    assert output.getvalue() == "ERROR: Stream edit 'testFile.in' replace '2022-2024' with '2022-2025' failed.\n"

    def test30_windows11_shell_stream_edit_inline_error_with_output_file(self):
        """!
        @brief Test shell.streamEdit(), output file open failure
        """
        errMsg = "sed: can't read testFile.in: No such file or directory"
        outMsg = ""
        cmdMsg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testFile.in']"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess(cmdMsg, 2, outMsg, errMsg)
            with patch("builtins.open", mock_open()):
                with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                    subproc.side_effect = Exception(OSError)
                    with patch('platform.release', MagicMock(return_value = 11)):
                        shell = WindowsPowerShell()
                        assert not shell.streamEdit("testFilePath", "2022-2024", "2022-2025", "streamedit.out")
                        assert output.getvalue() == "ERROR: Stream edit 'testFilePath' replace '2022-2024' with '2022-2025' failed.\n"

    def test31_windows11_shell_search_file(self):
        """!
        @brief Test shell.seachFile(), pass
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodePass = subprocess.CompletedProcess("", 0, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            with patch('platform.release', MagicMock(return_value = 11)):
                shell = WindowsPowerShell()
                status, retStr = shell.seachFile("shelltest.x", "Copyright")
                assert status
                assert retStr == testString

    def test32_windows11_shell_search_file_fail(self):
        """!
        @brief Test shell.seachFile(), failure
        """
        testString = "/* Copyright (c) 2022-2024 Randal Eike */\n"
        retCodeError = subprocess.CompletedProcess("", 2, testString, "")
        with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
            subproc.side_effect = Exception(OSError)
            with patch('platform.release', MagicMock(return_value = 11)):
                shell = WindowsPowerShell()
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status, retStr = shell.seachFile("shelltest.x", "Kilroy was here")
                    assert not status
                    assert retStr is None
                    assert output.getvalue() == "ERROR: File text search 'shelltest.x' for 'Kilroy was here' failed.\n"

if __name__ == '__main__':
    unittest.main()
