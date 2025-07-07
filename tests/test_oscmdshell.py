"""@package test_programmer_tools
Unittest for copyright maintenance utility
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

import platform
import subprocess

from unittest.mock import patch, MagicMock, mock_open
import pytest

from dir_init import TEST_FILE_PATH
from copyright_maintenance_grocsoftware.oscmdshell import get_command_shell
from copyright_maintenance_grocsoftware.oscmdshell import LinuxShell
from copyright_maintenance_grocsoftware.oscmdshell import WindowsPowerShell

TEST_FILE_BASE_DIR = TEST_FILE_PATH
OUTFILENAME = "streamedit.out"

@pytest.fixture
def output_file_sim():
    """!
    @brief Output file simulator for test that require an output file
    """
    fake_output_file = MagicMock()
    with patch("builtins.open", return_value = fake_output_file, create=True) as mock_file:
        yield fake_output_file, mock_file

        mock_file.assert_called_once_with(OUTFILENAME, 'wt', encoding='utf-8')
        fake_output_file.close.assert_called_once()

def test01_get_linux_shell():
    """!
    @brief Test get_command_shell()
    """
    with patch('platform.system', MagicMock(return_value='Linux')):
        shell = get_command_shell()
        assert isinstance(shell, LinuxShell)

def test02_get_windows_shell():
    """!
    @brief Test get_command_shell()
    """
    with patch('platform.system', MagicMock(return_value='Windows')):
        shell = get_command_shell()
        assert isinstance(shell, WindowsPowerShell)

def test03_get_shell_failed(capsys):
    """!
    @brief Test get_command_shell()
    """
    with patch('platform.system', MagicMock(return_value='SomethingElse')):
        shell = get_command_shell()
        assert shell is None
        expected = capsys.readouterr().out
        assert expected == "ERROR: Unsupported OS SomethingElse\n"

def test04_get_shell_real_call(capsys):
    """!
    @brief Test get_command_shell()
    """
    shell = get_command_shell()
    os_type = platform.system()

    if os_type == 'Linux':
        assert isinstance(shell, LinuxShell)
    elif os_type == 'Windows':
        assert isinstance(shell, WindowsPowerShell)
    else:
        assert shell is None
        expected = capsys.readouterr().out
        assert expected == "ERROR: Unsupported OS "+os_type

def test05_linux_shell_stream_edit_pass(output_file_sim):
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        shell = LinuxShell()
        assert shell.stream_edit("testfile.in", "2022-2024", "2022-2025", OUTFILENAME)

def test06_linux_shell_stream_edit_inline_pass():
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        shell = LinuxShell()
        assert shell.stream_edit("testfile.in", "2022-2024", "2022-2025")

def test07_linux_shell_stream_edit_inline_output_open_error(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    with patch("builtins.open", mock_open()) as mock_obj:
        mock_obj.return_value = None
        mock_obj.side_effect = OSError
        shell = LinuxShell()
        assert not shell.stream_edit("testfile.in", "2022-2024",
                                     "2022-2025", "testfile.out")
        expected = capsys.readouterr().out
        assert expected == "ERROR: Output file creation testfile.out failed\n"

def test08_linux_shell_stream_edit_inline_error(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "sed: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        shell = LinuxShell()
        assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
        expected = capsys.readouterr().out
        assert expected == "ERROR: Stream edit 'testfile.in' replace '2022-2024' " \
                           "with '2022-2025' failed.\n"

def test09_linux_shell_stream_edit_timeout_error(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "sed: timeout"
    output_msg = ""
    command_msg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        shell = LinuxShell()
        assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
        expected = capsys.readouterr().out
        assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test10_linux_shell_stream_edit_inline_error_with_output_file(output_file_sim, capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "sed: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        shell = LinuxShell()

        assert not shell.stream_edit("testfile_path", "2022-2024", "2022-2025", OUTFILENAME)

        msgout = capsys.readouterr()
        assert msgout.out == "ERROR: Stream edit 'testfile_path' replace '2022-2024' " \
                             "with '2022-2025' failed.\n"

def test11_linux_shell_stream_edit_timeout_error_with_output_file(output_file_sim, capsys):
    """!
    @brief Test shell.stream_edit(), process timeout
    """
    error_msg = "sed: timeout"
    output_msg = ""
    command_msg = "['sed', '-i', 's/2022-2024/2022-2025/g', 'testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        shell = LinuxShell()
        assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025", OUTFILENAME)
        expected = capsys.readouterr().out
        assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test12_linux_shell_search_file():
    """!
    @brief Test shell.seach_file(), pass
    """
    test_str = "/* Copyright (c) 2022-2024 Randal Eike */\n"
    ret_code_pass = subprocess.CompletedProcess("", 0, test_str, "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        shell = LinuxShell()
        status, return_str = shell.seach_file("shelltest.x", "Copyright")
        assert status
        assert return_str == test_str

def test13_linux_shell_search_file_fail(capsys):
    """!
    @brief Test shell.seach_file(), failure
    """
    test_str = "/* Copyright (c) 2022-2024 Randal Eike */\n"

    ret_code_error = subprocess.CompletedProcess("grep "+test_str, 2, "not found", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, "grep "+test_str, "not found", "")
        shell = LinuxShell()
        status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
        assert not status
        assert return_str is None
        expected = capsys.readouterr().out
        assert expected == "ERROR: File text search 'shelltest.x' for 'Kilroy was here' failed.\n"

def test14_linux_shell_search_file_fail_timeout(capsys):
    """!
    @brief Test shell.seach_file(), failure
    """
    test_str = "/* Copyright (c) 2022-2024 Randal Eike */\n"

    ret_code_error = subprocess.CompletedProcess("grep "+test_str, 2, "grep timeout", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        shell = LinuxShell()
        status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
        assert not status
        assert return_str is None
        expected = capsys.readouterr().out
        assert expected == "ERROR: File text search 'shelltest.x' timeout failure.\n"

def test15_windows9_shell_stream_edit_pass():
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert shell.stream_edit("testfile.in", "2022-2024",
                                     "2022-2025", OUTFILENAME)

def test16_windows9_shell_stream_edit_inline_pass():
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert shell.stream_edit("testfile.in", "2022-2024", "2022-2025")

def test17_windows9_shell_stream_edit_inline_error(capsys):
    """!
    @brief Test shell.stream_edit(), process fail
    """
    error_msg = "gc: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['powershell', '-Command', " \
                  "'(gc testfile.in -replace \'2022-2024\', \'2022-2025\')']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile.in' replace '2022-2024'" \
                               " with '2022-2025' failed.\n"

def test18_windows9_shell_stream_edit_inline_timeout_error(capsys):
    """!
    @brief Test shell.stream_edit(), process timeout fail
    """
    error_msg = "gc: timeout"
    output_msg = ""
    command_msg = "['powershell', '-Command', " \
                  "'(gc testfile.in -replace \'2022-2024\', \'2022-2025\')']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test19_windows9_shell_stream_edit_inline_error_with_output_file(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "gc: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['powershell', '-Command', '(gc testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile_path", "2022-2024",
                                        "2022-2025", OUTFILENAME)
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile_path' replace '2022-2024' " \
                               "with '2022-2025' failed.\n"

def test20_windows9_shell_stream_edit_inline_timeout_error_with_output_file(capsys):
    """!
    @brief Test shell.stream_edit(), process timeout fail
    """
    error_msg = "gc: timeout"
    output_msg = ""
    command_msg = "['powershell', '-Command', '(gc testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test21_windows9_shell_search_file():
    """!
    @brief Test shell.seach_file(), pass
    """
    test_str = "/* Copyright (c) 2022-2024 Randal Eike */\n"
    ret_code_pass = subprocess.CompletedProcess("", 0, test_str, "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Copyright")
            assert status
            assert return_str == test_str

def test22_windows9_shell_search_file_fail(capsys):
    """!
    @brief Test shell.seach_file(), failure
    """
    error_msg = "sls: failed"
    output_msg = ""
    command_msg = "['powershell', '-Command', 'sls \'Kilroy was here\' testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
            assert not status
            assert return_str is None
            expected = capsys.readouterr().out
            assert expected == "ERROR: File text search 'shelltest.x' for " \
                               "'Kilroy was here' failed.\n"

def test23_windows9_shell_search_file_fail_timout(capsys):
    """!
    @brief Test shell.seach_file(), timeout failure
    """
    error_msg = "sls: failed"
    output_msg = ""
    command_msg = "['powershell', '-Command', 'sls \'Kilroy was here\' testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 9)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
            assert not status
            assert return_str is None
            expected = capsys.readouterr().out
            assert expected == "ERROR: File text search 'shelltest.x' timeout failure.\n"

def test24_windows11_shell_stream_edit_pass():
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert shell.stream_edit("testfile.in", "2022-2024",
                                      "2022-2025", OUTFILENAME)

def test25_windows11_shell_stream_edit_inline_pass():
    """!
    @brief Test shell.stream_edit(), good case
    """
    ret_code_pass = subprocess.CompletedProcess("", 0, "", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert shell.stream_edit("testfile.in", "2022-2024", "2022-2025")

def test26_windows11_shell_stream_edit_inline_error(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "Get-Content: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['powershell', '(Get-Content testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile_path", "2022-2024", "2022-2025")
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile_path' replace '2022-2024' " \
                               "with '2022-2025' failed.\n"

def test27_windows11_shell_stream_edit_inline_timeout_error(capsys):
    """!
    @brief Test shell.stream_edit(), timeout failure
    """
    error_msg = "Get-Content: timeout"
    output_msg = ""
    command_msg = "['powershell', '(Get-Content testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025")
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test28_windows11_shell_stream_edit_inline_error_with_output_file(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "Get-Content: can't read testfile.in: No such file or directory"
    output_msg = ""
    command_msg = "['powershell', '(Get-Content testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile_path", "2022-2024", "2022-2025", OUTFILENAME)
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile_path' replace '2022-2024' " \
                               "with '2022-2025' failed.\n"

def test29_windows11_shell_stream_edit_inline_timeout_error_with_output_file(capsys):
    """!
    @brief Test shell.stream_edit(), output file open failure
    """
    error_msg = "Get-Content: timeout"
    output_msg = ""
    command_msg = "['powershell', '(Get-Content testfile.in -replace \'2022-2024\'," \
                  " \'2022-2025\') | Out-File -encoding ASCII outfile']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            assert not shell.stream_edit("testfile.in", "2022-2024", "2022-2025", OUTFILENAME)
            expected = capsys.readouterr().out
            assert expected == "ERROR: Stream edit 'testfile.in' timeout failure.\n"

def test30_windows11_shell_search_file():
    """!
    @brief Test shell.seach_file(), pass
    """
    test_str = "/* Copyright (c) 2022-2024 Randal Eike */\n"
    ret_code_pass = subprocess.CompletedProcess("", 0, test_str, "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Copyright")
            assert status
            assert return_str == test_str

def test31_windows11_shell_search_file_fail(capsys):
    """!
    @brief Test shell.seach_file(), failure
    """
    error_msg = "sls: failed"
    output_msg = ""
    command_msg = "['powershell', '-Command', 'sls \'Kilroy was here\' testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, command_msg, output_msg, error_msg)
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
            assert not status
            assert return_str is None
            expected = capsys.readouterr().out
            assert expected == "ERROR: File text search 'shelltest.x' for " \
                               "'Kilroy was here' failed.\n"

def test32_windows11_shell_search_file_fail_timeout(capsys):
    """!
    @brief Test shell.seach_file(), failure
    """
    error_msg = "sls: timeout"
    output_msg = ""
    command_msg = "['powershell', '-Command', 'sls \'Kilroy was here\' testfile.in']"

    ret_code_error = subprocess.CompletedProcess(command_msg, 2, output_msg, error_msg)
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = TimeoutError
        with patch('platform.release', MagicMock(return_value = 11)):
            shell = WindowsPowerShell()
            status, return_str = shell.seach_file("shelltest.x", "Kilroy was here")
            assert not status
            assert return_str is None
            expected = capsys.readouterr().out
            assert expected == "ERROR: File text search 'shelltest.x' timeout failure.\n"
