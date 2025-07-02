"""@package test_programmer_tools
Unittest for programmer base tools utility
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

import io, contextlib
from unittest.mock import patch, MagicMock

from dir_init import TESTFILEPATH
from dir_init import pathincsetup
pathincsetup()
testFileBaseDir = TESTFILEPATH

import time
import subprocess

from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_NONE
from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_MINIMAL
from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_VERBOSE
from copyright_maintenance_grocsoftware.file_dates import DBG_MSG_VERYVERBOSE
from copyright_maintenance_grocsoftware.file_dates import DebugPrint

from copyright_maintenance_grocsoftware.file_dates import GetFileSystemYears
from copyright_maintenance_grocsoftware.file_dates import GetGitArchiveFileYears
from copyright_maintenance_grocsoftware.file_dates import GetFileYears

class TestClass01Misc:
    """!
    @brief Test the DebugPrint function
    """
    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown close the file
        """

    def test001_debug_none(self):
        """!
        Test DebugPrint(), current level < message level
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            DebugPrint(DBG_MSG_MINIMAL, "test message")
            assert output.getvalue() == ""

    def test002_debug_message_equal(self):
        """!
        Test DebugPrint(), current level == message level
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            DebugPrint(DBG_MSG_NONE, "test message")
            assert output.getvalue() == "Debug: test message\n"

class TestClass02GetFilesystemDates:
    """!
    @brief Test the file system get dates GetFileSystemYears class
    """
    def test001_get_filesystem_years_local_time_overflow(self):
        """!
        Test _cvtTimestampToYear(), Overflow error
        """
        localTime = time.time()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('time.localtime', MagicMock(return_value = localTime)) as localTimeMock:
                localTimeMock.side_effect = OverflowError(localTimeMock)
                testObj = GetFileSystemYears("testfile")
                year = testObj._cvtTimestampToYear(localTime)
                assert year is None
                assert output.getvalue() == "ERROR: Overflow error on conversion of time epoch.\n"

    def test002_get_filesystem_years_local_time_os_error(self):
        """!
        Test _cvtTimestampToYear(), OS error
        """
        localTime = time.time()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('time.localtime', MagicMock(return_value = localTime)) as localTimeMock:
                localTimeMock.side_effect = OSError(localTimeMock)
                testObj = GetFileSystemYears("testfile")
                year = testObj._cvtTimestampToYear(localTime)
                assert year is None
                assert output.getvalue() == "ERROR: OS converstion error of time epoch.\n"

    def test003_get_filesystem_years_file_error_current_time(self):
        """!
        Test getFileYears(), Current time error
        """
        localTime = time.time()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('os.path.getctime', MagicMock(return_value = localTime)) as ctimeMock:
                ctimeMock.side_effect = OSError(ctimeMock)
                testObj = GetFileSystemYears("testfile")
                createYear, modYear = testObj.getFileYears()
                assert createYear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: OS get file times error of time.\n"

    def test004_get_filesystem_years_file_error_last_mod_time(self):
        """!
        Test getFileYears(), Last modification time error
        """
        localTime = time.time()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('os.path.getmtime', MagicMock(return_value = localTime)) as ctimeMock:
                ctimeMock.side_effect = OSError(ctimeMock)
                testObj = GetFileSystemYears("testfile")
                createYear, modYear = testObj.getFileYears()
                assert createYear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: OS get file times error of time.\n"

    def test005_get_filesystem_years_file_pass(self):
        """!
        Test getFileYears(), Good path
        """
        localTime = time.time()
        expectedStr = time.strftime("%Y", time.localtime(localTime))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('os.path.getctime', MagicMock(return_value = localTime)), patch('os.path.getmtime', MagicMock(return_value = localTime)):
                testObj = GetFileSystemYears("testfile")
                createYear, modYear = testObj.getFileYears()
                assert createYear == expectedStr
                assert modYear == expectedStr
                assert output.getvalue() == ""

from copyright_maintenance_grocsoftware.file_dates import GetGitArchiveFileYears

class TestClass03GetGitArchiveDates:
    """!
    @brief Test the file system get dates GetGitArchiveFileYears class
    """
    def test001_get_creation_year_pass(self):
        """!
        Test _getCreationYear(), Git cmd pass
        """
        retCodePass = subprocess.CompletedProcess("git", 0, "2022-01-01T12:00:00-06:00".encode('utf-8'), "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            testObj = GetGitArchiveFileYears("testfile")
            year = testObj._getCreationYear()
            assert year == '2022'

    def test002_get_creation_year_git_fail(self):
        """!
        Test _getCreationYear(), Git cmd failed
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeFail = subprocess.CompletedProcess("git", 2, "git error msg".encode('utf-8'), "")
            with patch('subprocess.run', MagicMock(return_value = retCodeFail)):
                testObj = GetGitArchiveFileYears("testfile")
                year = testObj._getCreationYear()
                assert year is None
                assert output.getvalue() == "ERROR: Git creation date failed: git error msg\n"

    def test003_get_creation_year_system_failure(self):
        """!
        Test _getCreationYear(), Git subprocess failure
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess("", 2, "git error msg", "")
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = OSError
                testObj = GetGitArchiveFileYears("testfile")
                year = testObj._getCreationYear()
                assert year is None
                assert output.getvalue() == "ERROR: Git creation date command failed for file: testfile\n"

    def test004_get_last_mod_year_pass(self):
        """!
        Test _getLastModificationYear(), Git cmd pass
        """
        retCodePass = subprocess.CompletedProcess("git", 0, "2023-01-01T12:00:00-06:00".encode('utf-8'), "")
        with patch('subprocess.run', MagicMock(return_value = retCodePass)):
            testObj = GetGitArchiveFileYears("testfile")
            year = testObj._getLastModificationYear()
            assert year == '2023'

    def test005_get_last_mod_year_git_fail(self):
        """!
        Test _getLastModificationYear(), Git cmd failed
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeFail = subprocess.CompletedProcess("git", 2, "git error msg".encode('utf-8'), "")
            with patch('subprocess.run', MagicMock(return_value = retCodeFail)):
                testObj = GetGitArchiveFileYears("testfile")
                year = testObj._getLastModificationYear()
                assert year is None
                assert output.getvalue() == "ERROR: Git last modification date failed: git error msg\n"

    def test006_get_last_mod_year_system_failure(self):
        """!
        Test _getLastModificationYear(), Git subprocess failure
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            retCodeError = subprocess.CompletedProcess("", 2, "git error msg", "")
            with patch('subprocess.run', MagicMock(return_value = retCodeError)) as subproc:
                subproc.side_effect = OSError
                testObj = GetGitArchiveFileYears("testfile")
                year = testObj._getLastModificationYear()
                assert year is None
                assert output.getvalue() == "ERROR: Git last modification date command failed for file: testfile\n"

    def test007_get_years_pass(self):
        """!
        Test getFileYears(), Git pass
        """
        def mockrun(args, *, stdin=None,
                     input=None, stdout=None,
                     stderr=None, capture_output=False,
                     shell=False, cwd=None,
                     timeout=None, check=False,
                     encoding=None, errors=None,
                     text=None, env=None, universal_newlines=None,
                     **other_popen_kwargs):

            gitCmd = ""
            prefix = ""
            for element in args:
                gitCmd += prefix
                gitCmd += element
                prefix = " "
            if args[2] == "-1":
                return subprocess.CompletedProcess(gitCmd, 0, "2024-01-01T12:00:00-06:00".encode('utf-8'), "")
            elif args[2] == "--diff-filter=A":
                return subprocess.CompletedProcess(gitCmd, 0, "2023-01-01T12:00:00-06:00".encode('utf-8'), "")
            else:
                return subprocess.CompletedProcess(gitCmd, 2, "Git error".encode('utf-8'), "")

        with patch('subprocess.run', MagicMock(side_effect = mockrun)):
            testObj = GetGitArchiveFileYears("testfile")
            startyear, modYear = testObj.getFileYears()
            assert startyear == '2023'
            assert modYear == '2024'

    def test008_get_years_start_fail(self):
        """!
        Test getFileYears(), Git pass
        """
        def mockrun(args, *, stdin=None,
                     input=None, stdout=None,
                     stderr=None, capture_output=False,
                     shell=False, cwd=None,
                     timeout=None, check=False,
                     encoding=None, errors=None,
                     text=None, env=None, universal_newlines=None,
                     **other_popen_kwargs):

            gitCmd = ""
            prefix = ""
            for element in args:
                gitCmd += prefix
                gitCmd += element
                prefix = " "
            if args[2] == "-1":
                return subprocess.CompletedProcess(gitCmd, 0, "2024-01-01T12:00:00-06:00".encode('utf-8'), "")
            elif args[2] == "--diff-filter=A":
                return subprocess.CompletedProcess(gitCmd, 2, "git error msg".encode('utf-8'), "")
            else:
                return subprocess.CompletedProcess(gitCmd, 4, "Git error".encode('utf-8'), "")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('subprocess.run', MagicMock(side_effect = mockrun)):
                testObj = GetGitArchiveFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: Git creation date failed: git error msg\n"

    def test009_get_years_las_mod_fail(self):
        """!
        Test getFileYears(), Git pass
        """
        def mockrun(args, *, stdin=None,
                     input=None, stdout=None,
                     stderr=None, capture_output=False,
                     shell=False, cwd=None,
                     timeout=None, check=False,
                     encoding=None, errors=None,
                     text=None, env=None, universal_newlines=None,
                     **other_popen_kwargs):

            gitCmd = ""
            prefix = ""
            for element in args:
                gitCmd += prefix
                gitCmd += element
                prefix = " "
            if args[2] == "-1":
                return subprocess.CompletedProcess(gitCmd, 2, "git error msg".encode('utf-8'), "")
            elif args[2] == "--diff-filter=A":
                return subprocess.CompletedProcess(gitCmd, 0, "2024-01-01T12:00:00-06:00".encode('utf-8'), "")
            else:
                return subprocess.CompletedProcess(gitCmd, 4, "Git error".encode('utf-8'), "")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch('subprocess.run', MagicMock(side_effect = mockrun)):
                testObj = GetGitArchiveFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: Git last modification date failed: git error msg\n"

class TestClass04GetYears:
    """!
    @brief Test marco class
    """
    def test001_get_year_git(self):
        def existReturn(filename):
            if filename == "testfile":
                return True
            elif filename == ".git":
                return True
            else:
                return False

        def mockrun(args, *, stdin=None,
                     input=None, stdout=None,
                     stderr=None, capture_output=False,
                     shell=False, cwd=None,
                     timeout=None, check=False,
                     encoding=None, errors=None,
                     text=None, env=None, universal_newlines=None,
                     **other_popen_kwargs):

            gitCmd = ""
            prefix = ""
            for element in args:
                gitCmd += prefix
                gitCmd += element
                prefix = " "
            if args[2] == "-1":
                return subprocess.CompletedProcess(gitCmd, 0, "2025-01-01T12:00:00-06:00".encode('utf-8'), "")
            elif args[2] == "--diff-filter=A":
                return subprocess.CompletedProcess(gitCmd, 0, "2022-01-01T12:00:00-06:00".encode('utf-8'), "")
            else:
                return subprocess.CompletedProcess(gitCmd, 4, "Git error".encode('utf-8'), "")

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = True)), patch('os.path.isdir', MagicMock(return_value = True)):
            with patch('subprocess.run', MagicMock(side_effect = mockrun)):
                testObj = GetFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear == '2022'
                assert modYear == '2025'

    def test002_get_year_file_system(self):
        def existReturn(filename):
            if filename == "testfile":
                return True
            elif filename == ".git":
                return False
            else:
                return False

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = True)):
            localTime = time.time()
            expectedStr = time.strftime("%Y", time.localtime(localTime))
            with patch('os.path.getctime', MagicMock(return_value = localTime)), patch('os.path.getmtime', MagicMock(return_value = localTime)):
                testObj = GetFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear == expectedStr
                assert modYear == expectedStr

    def test003_get_year_file_system_git_not_dir(self):
        def existReturn(filename):
            if filename == "testfile":
                return True
            elif filename == ".git":
                return True
            else:
                return False

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = True)), patch('os.path.isdir', MagicMock(return_value = False)):
            localTime = time.time()
            expectedStr = time.strftime("%Y", time.localtime(localTime))
            with patch('os.path.getctime', MagicMock(return_value = localTime)), patch('os.path.getmtime', MagicMock(return_value = localTime)):
                testObj = GetFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear == expectedStr
                assert modYear == expectedStr

    def test004_get_years_fail_no_file(self):
        def existReturn(filename):
            if filename == "testfile":
                return False
            elif filename == ".git":
                return True
            else:
                return False

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = True)), patch('os.path.isdir', MagicMock(return_value = True)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                testObj = GetFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: File: \"testfile\" does not exist or is not a file.\n"

    def test005_get_years_fail_not_file(self):
        def existReturn(filename):
            if filename == "testfile":
                return True
            elif filename == ".git":
                return True
            else:
                return False

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = False)), patch('os.path.isdir', MagicMock(return_value = True)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                testObj = GetFileYears("testfile")
                startyear, modYear = testObj.getFileYears()
                assert startyear is None
                assert modYear is None
                assert output.getvalue() == "ERROR: File: \"testfile\" does not exist or is not a file.\n"


if __name__ == '__main__':
    unittest.main()
