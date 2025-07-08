"""@package copyright_maintenance_unittest
Unittest for copyright maintenance utility
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

import time
import subprocess
from unittest.mock import patch, MagicMock

from tests.dir_init import TEST_FILE_PATH

from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_NONE
from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_MINIMAL
from copyright_maintenance_grocsoftware.file_dates import debug_print

from copyright_maintenance_grocsoftware.file_dates import GetFileSystemYears
from copyright_maintenance_grocsoftware.file_dates import GetGitArchiveFileYears
from copyright_maintenance_grocsoftware.file_dates import get_file_years

TEST_FILE_BASE_DIR = TEST_FILE_PATH

# pylint: disable=protected-access

def test001_debug_none(capsys):
    """!
    Test debug_print(), current level < message level
    """
    debug_print(DBG_MSG_MINIMAL, "test message")
    assert capsys.readouterr().out == ""

def test002_debug_message_equal(capsys):
    """!
    Test debug_print(), current level == message level
    """
    debug_print(DBG_MSG_NONE, "test message")
    assert capsys.readouterr().out == "Debug: test message\n"

def test003_get_filesystem_years_local_time_overflow(capsys):
    """!
    Test cvt_timestamp_to_year(), Overflow error
    """
    mock_local_time = time.time()
    with patch('time.localtime', MagicMock(return_value = mock_local_time)) as mock_time_patch:
        mock_time_patch.side_effect = OverflowError(mock_time_patch)
        test_obj = GetFileSystemYears("testfile")
        year = test_obj.cvt_timestamp_to_year(mock_local_time)
        assert year is None
        assert capsys.readouterr().out == "ERROR: Overflow error on conversion of time epoch.\n"

def test004_get_filesystem_years_local_time_os_error(capsys):
    """!
    Test cvt_timestamp_to_year(), OS error
    """
    mock_local_time = time.time()
    with patch('time.localtime', MagicMock(return_value = mock_local_time)) as mock_time_patch:
        mock_time_patch.side_effect = OSError(mock_time_patch)
        test_obj = GetFileSystemYears("testfile")
        year = test_obj.cvt_timestamp_to_year(mock_local_time)
        assert year is None
        assert capsys.readouterr().out == "ERROR: OS converstion error of time epoch.\n"

def test005_get_filesystem_years_file_error_current_time(capsys):
    """!
    Test get_file_years(), Current time error
    """
    mock_local_time = time.time()
    with patch('os.path.getctime', MagicMock(return_value = mock_local_time)) as ctime_mock:
        ctime_mock.side_effect = OSError(ctime_mock)
        test_obj = GetFileSystemYears("testfile")
        create_year, modify_year = test_obj.get_file_years()
        assert create_year is None
        assert modify_year is None
        assert capsys.readouterr().out == "ERROR: OS get file times error of time.\n"

def test006_get_filesystem_years_file_error_last_mod_time(capsys):
    """!
    Test get_file_years(), Last modification time error
    """
    mock_local_time = time.time()
    with patch('os.path.getmtime', MagicMock(return_value = mock_local_time)) as ctime_mock:
        ctime_mock.side_effect = OSError(ctime_mock)
        test_obj = GetFileSystemYears("testfile")
        create_year, modify_year = test_obj.get_file_years()
        assert create_year is None
        assert modify_year is None
        assert capsys.readouterr().out == "ERROR: OS get file times error of time.\n"

def test007_get_filesystem_years_file_pass(capsys):
    """!
    Test get_file_years(), Good path
    """
    mock_local_time = time.time()
    expected_str = time.strftime("%Y", time.localtime(mock_local_time))
    with patch('os.path.getctime', MagicMock(return_value = mock_local_time)):
        with patch('os.path.getmtime', MagicMock(return_value = mock_local_time)):
            test_obj = GetFileSystemYears("testfile")
            create_year, modify_year = test_obj.get_file_years()
            assert create_year == expected_str
            assert modify_year == expected_str
            assert capsys.readouterr().out == ""

def test008_get_creation_year_pass():
    """!
    Test get_creation_year(), Git cmd pass
    """
    ret_code_pass = subprocess.CompletedProcess("git",
                                                0,
                                                "2022-01-01T12:00:00-06:00".encode('utf-8'),
                                                "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_creation_year()
        assert year == '2022'

def test009_get_creation_year_git_fail(capsys):
    """!
    Test get_creation_year(), Git cmd failed
    """
    ret_code_fail = subprocess.CompletedProcess("git",
                                                2,
                                                "git error msg".encode('utf-8'),
                                                "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_fail)):
        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_creation_year()
        assert year is None
        assert capsys.readouterr().out == "ERROR: Git creation date failed: git error msg\n"

def test010_get_creation_year_system_failure(capsys):
    """!
    Test get_creation_year(), Git subprocess failure
    """
    ret_code_error = subprocess.CompletedProcess("", 2, "git error msg", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, "git_cmd", "", "git error msg")

        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_creation_year()
        assert year is None
        assert capsys.readouterr().out == "ERROR: Git creation date command failed for " \
                                          "file: testfile\n"

def test011_get_last_mod_year_pass():
    """!
    Test get_last_modification_year(), Git cmd pass
    """
    ret_code_pass = subprocess.CompletedProcess("git",
                                                0,
                                                "2023-01-01T12:00:00-06:00".encode('utf-8'),
                                                "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_pass)):
        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_last_modification_year()
        assert year == '2023'

def test012_get_last_mod_year_git_fail(capsys):
    """!
    Test get_last_modification_year(), Git cmd failed
    """
    ret_code_fail = subprocess.CompletedProcess("git",
                                                2,
                                                "git error msg".encode('utf-8'),
                                                "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_fail)):
        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_last_modification_year()
        assert year is None
        assert capsys.readouterr().out == "ERROR: Git last modification date failed: " \
                                    "git error msg\n"

def test013_get_last_mod_year_system_failure(capsys):
    """!
    Test get_last_modification_year(), Git subprocess failure
    """
    ret_code_error = subprocess.CompletedProcess("", 2, "git error msg", "")
    with patch('subprocess.run', MagicMock(return_value = ret_code_error)) as subproc:
        subproc.side_effect = subprocess.CalledProcessError(2, "git_cmd", "", "git error msg")
        test_obj = GetGitArchiveFileYears("testfile")
        year = test_obj.get_last_modification_year()
        assert year is None
        assert capsys.readouterr().out == "ERROR: Git last modification date command failed " \
                                          "for file: testfile\n"

def test014_get_years_pass():
    """!
    Test get_file_years(), Git pass
    """
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def mockrun(args, *, stdin=None,
                    inputstd=None, stdout=None,
                    stderr=None, capture_output=False,
                    shell=False, cwd=None,
                    timeout=None, check=False,
                    encoding=None, errors=None,
                    text=None, env=None, universal_newlines=None,
                    **other_popen_kwargs):

        git_cmd = ""
        prefix = ""
        for element in args:
            git_cmd += prefix
            git_cmd += element
            prefix = " "

        ret_code = None
        if args[2] == "-1":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2024-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        elif args[2] == "--diff-filter=A":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2023-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        else:
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               2,
                                               "Git error".encode('utf-8'),
                                               "")
        return ret_code
    # pylint: enable=unused-argument
    # pylint: enable=too-many-arguments

    with patch('subprocess.run', MagicMock(side_effect = mockrun)):
        test_obj = GetGitArchiveFileYears("testfile")
        startyear, modify_year = test_obj.get_file_years()
        assert startyear == '2023'
        assert modify_year == '2024'

    # pylint: enable=too-many-locals

def test015_get_years_start_fail(capsys):
    """!
    Test get_file_years(), Git pass
    """
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def mockrun(args, *, stdin=None,
                    inputstd=None, stdout=None,
                    stderr=None, capture_output=False,
                    shell=False, cwd=None,
                    timeout=None, check=False,
                    encoding=None, errors=None,
                    text=None, env=None, universal_newlines=None,
                    **other_popen_kwargs):

        git_cmd = ""
        prefix = ""
        for element in args:
            git_cmd += prefix
            git_cmd += element
            prefix = " "

        ret_code = None
        if args[2] == "-1":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2024-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        elif args[2] == "--diff-filter=A":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               2,
                                               "git error msg".encode('utf-8'),
                                               "")
        else:
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               4,
                                               "Git error".encode('utf-8'),
                                               "")
        return ret_code
    # pylint: enable=unused-argument
    # pylint: enable=too-many-arguments

    with patch('subprocess.run', MagicMock(side_effect = mockrun)):
        test_obj = GetGitArchiveFileYears("testfile")
        startyear, modify_year = test_obj.get_file_years()
        assert startyear is None
        assert modify_year is None
        assert capsys.readouterr().out == "ERROR: Git creation date failed: git error msg\n"
    # pylint: enable=too-many-locals

def test016_get_years_las_mod_fail(capsys):
    """!
    Test get_file_years(), Git pass
    """
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def mockrun(args, *, stdin=None,
                    inputstd=None, stdout=None,
                    stderr=None, capture_output=False,
                    shell=False, cwd=None,
                    timeout=None, check=False,
                    encoding=None, errors=None,
                    text=None, env=None, universal_newlines=None,
                    **other_popen_kwargs):

        git_cmd = ""
        prefix = ""
        for element in args:
            git_cmd += prefix
            git_cmd += element
            prefix = " "

        if args[2] == "-1":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               2,
                                               "git error msg".encode('utf-8'),
                                               "")
        elif args[2] == "--diff-filter=A":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2024-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        else:
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               4,
                                               "Git error".encode('utf-8'),
                                               "")
        return ret_code
    # pylint: enable=unused-argument
    # pylint: enable=too-many-arguments

    with patch('subprocess.run', MagicMock(side_effect = mockrun)):
        test_obj = GetGitArchiveFileYears("testfile")
        startyear, modify_year = test_obj.get_file_years()
        assert startyear is None
        assert modify_year is None
        expected = capsys.readouterr().out
        assert expected == "ERROR: Git last modification date failed: git error msg\n"
    # pylint: enable=too-many-locals

def test017_get_year_git():
    """!
    Test GIT get_file_years() method
    """
    # pylint: disable=too-many-locals
    def exist_return(filename):
        if filename == "testfile":
            ret_code = True
        elif filename == ".git":
            ret_code = True
        else:
            ret_code = False
        return ret_code

    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    def mockrun(args, *, stdin=None,
                    inputstd=None, stdout=None,
                    stderr=None, capture_output=False,
                    shell=False, cwd=None,
                    timeout=None, check=False,
                    encoding=None, errors=None,
                    text=None, env=None, universal_newlines=None,
                    **other_popen_kwargs):

        git_cmd = ""
        prefix = ""
        for element in args:
            git_cmd += prefix
            git_cmd += element
            prefix = " "
        if args[2] == "-1":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2025-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        elif args[2] == "--diff-filter=A":
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               0,
                                               "2022-01-01T12:00:00-06:00".encode('utf-8'),
                                               "")
        else:
            ret_code = subprocess.CompletedProcess(git_cmd,
                                               4,
                                               "Git error".encode('utf-8'),
                                               "")
        return ret_code
    # pylint: enable=unused-argument
    # pylint: enable=too-many-arguments

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = True)):
            with patch('os.path.isdir', MagicMock(return_value = True)):
                with patch('subprocess.run', MagicMock(side_effect = mockrun)):
                    startyear, modify_year = get_file_years("testfile")
                    assert startyear == '2022'
                    assert modify_year == '2025'
    # pylint: enable=too-many-locals

def test018_get_year_file_system():
    """!
    @brief Test file system get_file_years
    """
    def exist_return(filename):
        if filename == "testfile":
            ret_code = True
        elif filename == ".git":
            ret_code = False
        else:
            ret_code = False
        return ret_code

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = True)):
            mock_local_time = time.time()
            expected_str = time.strftime("%Y", time.localtime(mock_local_time))
            with patch('os.path.getctime', MagicMock(return_value = mock_local_time)):
                with patch('os.path.getmtime', MagicMock(return_value = mock_local_time)):
                    startyear, modify_year = get_file_years("testfile")
                    assert startyear == expected_str
                    assert modify_year == expected_str

def test019_get_year_file_system_git_not_dir():
    """!
    @brief Test get_file_years object return function, file system object
    """
    def exist_return(filename):
        if filename == "testfile":
            ret_code = True
        elif filename == ".git":
            ret_code = True
        else:
            ret_code = False
        return ret_code

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = True)):
            with patch('os.path.isdir', MagicMock(return_value = False)):
                mock_local_time = time.time()
                expected_str = time.strftime("%Y", time.localtime(mock_local_time))
                with patch('os.path.getctime', MagicMock(return_value = mock_local_time)):
                    with patch('os.path.getmtime', MagicMock(return_value = mock_local_time)):
                        startyear, modify_year = get_file_years("testfile")
                        assert startyear == expected_str
                        assert modify_year == expected_str

def test020_get_years_fail_no_file(capsys):
    """!
    @brief Test get_file_years object return function, file does not exist
    """
    def exist_return(filename):
        if filename == "testfile":
            ret_code = False
        elif filename == ".git":
            ret_code = True
        else:
            ret_code = False
        return ret_code

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = True)):
            with patch('os.path.isdir', MagicMock(return_value = True)):
                startyear, modify_year = get_file_years("testfile")
                assert startyear is None
                assert modify_year is None
                expected = "ERROR: File: \"testfile\" does not exist or is not a file.\n"
                assert capsys.readouterr().out == expected

def test021_get_years_fail_not_file(capsys):
    """!
    @brief Test get_file_years object return function, not a file failure
    """
    def exist_return(filename):
        if filename == "testfile":
            ret_code = True
        elif filename == ".git":
            ret_code = True
        else:
            ret_code = False
        return ret_code

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = False)):
            with patch('os.path.isdir', MagicMock(return_value = True)):
                startyear, modify_year = get_file_years("testfile")
                assert startyear is None
                assert modify_year is None
                expected = "ERROR: File: \"testfile\" does not exist or is not a file.\n"
                assert capsys.readouterr().out == expected

    with patch('os.path.exists', MagicMock(side_effect = exist_return)):
        with patch('os.path.isfile', MagicMock(return_value = False)):
            with patch('os.path.isdir', MagicMock(return_value = True)):
                startyear, modify_year = get_file_years("testfile")
                assert startyear is None
                assert modify_year is None
                expected = "ERROR: File: \"testfile\" does not exist or is not a file.\n"
                assert capsys.readouterr().out == expected
