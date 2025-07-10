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

import os
import time
import io
import contextlib
from unittest.mock import patch, MagicMock
import _io
import pytest


from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder1
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.comment_block import CommentParams

from copyright_maintenance_grocsoftware.file_dates import get_file_years
from copyright_maintenance_grocsoftware.oscmdshell import get_command_shell
from copyright_maintenance_grocsoftware.update_copyright import CopyrightCommentBlock
from copyright_maintenance_grocsoftware.update_copyright import update_copyright_years

from tests.dir_init import TEST_FILE_PATH
TEST_FILE_BASE_DIR = TEST_FILE_PATH

# pylint: disable=protected-access

class DummyParser(CopyrightParseOrder1):
    """!
    Dummy copyright parser class for testing
    """
    def __init__(self):
        super().__init__(r'Copyright|COPYRIGHT|copyright',
                         r'\([cC]\)',
                         r'(\d{4})',
                         r'[a-zA-Z0-9,\./\- @]',
                         False)

class TestClass01CopyrightBlock:
    """!
    @brief Test the CopyrightCommentBlock class
    """
    @classmethod
    def setup_class(cls):
        """!
        @brief On test start set the filename
        """
        cls._test_file_name = os.path.join(TEST_FILE_BASE_DIR, "copyrighttest.h")
        cls._test_file = None
        # pylint: disable=consider-using-with
        cls._test_file = open(cls._test_file_name, "rt", encoding="utf-8")
        # pylint: enable=consider-using-with

    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown restore the original copyright dates
        """
        if cls._test_file is not None:
            cls._test_file.close()

    def test001_constructor_with_default(self):
        """!
        @brief Test the default constructor
        """
        test_obj = CopyrightCommentBlock(self._test_file)
        #self.assertIsInstance(test_obj._copyright_parser, CopyrightParseEnglish)
        assert test_obj.comment_data is None
        assert isinstance(test_obj.input_file, _io.TextIOWrapper)
        assert len(test_obj._copyright_block_data) == 0

    def test002_constructor_with_partial_input(self):
        """!
        @brief Test the constructor with default copyright parser
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.pyCommentParms)
        #self.assertIsInstance(test_obj._copyright_parser, CopyrightParseEnglish)
        assert test_obj.comment_data == CommentParams.pyCommentParms
        assert isinstance(test_obj.input_file, _io.TextIOWrapper)
        assert len(test_obj._copyright_block_data) == 0

    def test003_constructor_with_input(self):
        """!
        @brief Test the constructor with full input
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms, DummyParser)
        #self.assertIsInstance(test_obj._copyright_parser, DummyParser)
        assert test_obj.comment_data == CommentParams.cCommentParms
        assert isinstance(test_obj.input_file, _io.TextIOWrapper)
        assert len(test_obj._copyright_block_data) == 0

    def test004_is_copyright_comment_block_no_input(self):
        """!
        @brief Test the _is_copyright_comment_block method, default input
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        status, text = test_obj._is_copyright_comment_block(None, None)
        assert not status
        assert text is None

    def test005_is_copyright_comment_block_partial_input(self):
        """!
        @brief Test the _is_copyright_comment_block method, incomplete input
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        status, location_dict = test_obj._is_copyright_comment_block(0, None)
        assert not status
        assert location_dict is None

        status1, location_dict1 = test_obj._is_copyright_comment_block(None, 100)
        assert not status1
        assert location_dict1 is None

    def test004_is_copyright_comment_block_good_input(self):
        """!
        @brief Test the _is_copyright_comment_block method, good input
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        status, location_dict = test_obj._is_copyright_comment_block(0, 1082)
        assert status
        assert location_dict['lineOffset'] == 3
        assert location_dict['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

    def test005_is_copyright_comment_block_post_blk_input(self):
        """!
        @brief Test the _is_copyright_comment_block method, post block input
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        status, location_dict = test_obj._is_copyright_comment_block(1084, 1084+81)
        assert not status
        assert location_dict is None

    def test006_is_find_next_block_found(self):
        """!
        @brief Test the _is_find_next_copyright_block method, good find
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        self._test_file.seek(0)
        status, location_dict = test_obj._is_find_next_copyright_block()
        assert status
        assert location_dict['blkStart'] == 0
        assert location_dict['blkEndEOL'] == 1082
        assert location_dict['blkEndSOL'] == 1079
        assert len(location_dict['copyrightMsgs']) == 1
        assert location_dict['copyrightMsgs'][0]['lineOffset'] == 3
        assert location_dict['copyrightMsgs'][0]['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

    def test007_is_find_next_block_not_found(self):
        """!
        @brief Test the _is_find_next_copyright_block method, not found
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        self._test_file.seek(1084)
        status, location_dict = test_obj._is_find_next_copyright_block()
        assert not status
        assert location_dict['blkStart'] == 1186
        assert location_dict['blkEndEOL'] == 1291
        assert location_dict['blkEndSOL'] == 1287
        assert len(location_dict['copyrightMsgs']) == 0

    def test008_find_copyright_blocks(self):
        """!
        @brief Test the find_copyright_blocks method, found
        """
        test_obj = CopyrightCommentBlock(self._test_file, CommentParams.cCommentParms)
        location_list = test_obj.find_copyright_blocks()
        assert len(location_list) == 1
        assert location_list[0]['blkStart'] == 0
        assert location_list[0]['blkEndEOL'] == 1082
        assert location_list[0]['blkEndSOL'] == 1079
        assert len(location_list[0]['copyrightMsgs']) == 1
        assert location_list[0]['copyrightMsgs'][0]['lineOffset'] == 3
        expected = " Copyright (c) 2022-2023 Randal Eike\n"
        assert location_list[0]['copyrightMsgs'][0]['text'] == expected

    def test009_find_copyright_blocks_not_found(self):
        """!
        @brief Test the find_copyright_blocks method, not found
        """
        test_filename = os.path.join(TEST_FILE_BASE_DIR, "copyrighttest_none.h")
        with open(test_filename, "rt", encoding="utf-8") as testfile:
            test_obj = CopyrightCommentBlock(testfile, CommentParams.cCommentParms)
            location_list = test_obj.find_copyright_blocks()
            assert len(location_list) == 0

            testfile.close()

    def test010_find_copyright_blocks_double_find(self):
        """!
        @brief Test the find_copyright_blocks method, double found
        """
        test_filename = os.path.join(TEST_FILE_BASE_DIR, "copyrighttest_dbl.h")
        with open(test_filename, "rt", encoding="utf-8") as testfile:
            test_obj = CopyrightCommentBlock(testfile, CommentParams.cCommentParms)
            location_list = test_obj.find_copyright_blocks()
            assert len(location_list) == 1
            assert location_list[0]['blkStart'] == 0
            assert location_list[0]['blkEndEOL'] == 1112
            assert location_list[0]['blkEndSOL'] == 1109
            assert len(location_list[0]['copyrightMsgs']) == 2
            assert location_list[0]['copyrightMsgs'][0]['lineOffset'] == 3
            expected = " Copyright (c) 2022-2023 Randal Eike\n"
            assert location_list[0]['copyrightMsgs'][0]['text'] == expected
            assert location_list[0]['copyrightMsgs'][1]['lineOffset'] == 40
            assert location_list[0]['copyrightMsgs'][1]['text'] == " Copyright (c) 2024-2025 Zeus\n"

            testfile.close()

    def test011_find_copyright_blocks_double_blk_find(self):
        """!
        @brief Test the find_copyright_blocks method, double block found
        """
        test_filename = os.path.join(TEST_FILE_BASE_DIR, "copyrighttest_dblblk.h")
        with open(test_filename, "rt", encoding="utf-8") as testfile:
            test_obj = CopyrightCommentBlock(testfile, CommentParams.cCommentParms)
            location_list = test_obj.find_copyright_blocks()
            assert len(location_list) == 2
            assert location_list[0]['blkStart'] == 0
            assert location_list[0]['blkEndEOL'] == 1082
            assert location_list[0]['blkEndSOL'] == 1079
            assert len(location_list[0]['copyrightMsgs']) == 1
            assert location_list[0]['copyrightMsgs'][0]['lineOffset'] == 3
            expected = " Copyright (c) 2022-2023 Randal Eike\n"
            assert location_list[0]['copyrightMsgs'][0]['text'] == expected

            assert location_list[1]['blkStart'] == 1083
            assert location_list[1]['blkEndEOL'] == 2158
            assert location_list[1]['blkEndSOL'] == 2155
            assert len(location_list[1]['copyrightMsgs']) == 1
            assert location_list[1]['copyrightMsgs'][0]['lineOffset'] == 1086
            assert location_list[1]['copyrightMsgs'][0]['text'] == " Copyright (c) 2024-2025 Odin\n"

            testfile.close()


class TestClass02CopyrightUpdate:
    """!
    @brief Test the update_copyright_years function
    """
    @classmethod
    def setup_class(cls):
        """!
        @brief On test start set the filename
        """
        cls._test_file_name = os.path.join(TEST_FILE_BASE_DIR, "copyrighttest.h")
        _, expected = get_file_years(cls._test_file_name)
        copyright_gen = CopyrightParseEnglish()
        cls._yearStr = copyright_gen._build_copyright_year_string(2022, expected)

    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown restore the original copyright dates
        """
        new_msg = "Copyright (c) "+cls._yearStr+" Randal Eike"
        get_command_shell().stream_edit(cls._test_file_name,
                                     new_msg,
                                     "Copyright (c) 2022-2023 Randal Eike")

    def grep_check(self, filename, search_str):
        """!
        @brief On test teardown restore the original copyright dates
        """
        status, search_results = get_command_shell().seach_file(filename, search_str)
        return status, search_results

    def reset_copyright_msg(self, search_str):
        """!
        @brief On test teardown restore the original copyright dates
        """
        get_command_shell().stream_edit(self._test_file_name,
                                        search_str,
                                        "Copyright (c) 2022-2023 Randal Eike")

    def test001_update_years(self):
        """!
        Test update_copyright_years()
        """
        def exist_return(filename):
            if filename == self._test_file_name:
                ret_code = True
            elif filename == ".git":
                ret_code = False
            else:
                ret_code = False
            return ret_code

        with patch('os.path.exists', MagicMock(side_effect = exist_return)):
            with patch('os.path.isfile', MagicMock(return_value = True)):
                local_mock_tm = time.time()
                mock_create_str = "01 Jan 2022 12:00:00"
                mock_create_obj = time.strptime(mock_create_str, "%d %b %Y %H:%M:%S")
                mock_create_tm = time.mktime(mock_create_obj)
                with patch('os.path.getctime', MagicMock(return_value = mock_create_tm)):
                    with patch('os.path.getmtime', MagicMock(return_value = local_mock_tm)):
                        update_copyright_years(self._test_file_name)
                        grep_status, test_str = self.grep_check(self._test_file_name,
                                                                r" Copyright (c)")
                        self.reset_copyright_msg("Copyright (c) 2022-2025 Randal Eike")
                        assert grep_status
                        expected_msg = " Copyright (c) 2022-2025 Randal Eike\n"
                        assert expected_msg == test_str

    def test002_update_years_get_file_years_fail(self):
        """!
        Test update_copyright_years(), get_file_years failure
        """
        with pytest.raises(FileNotFoundError):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                update_copyright_years("foo")
                expected_err_str = "ERROR: File: \"foo\" does not exist or is not a file.\n"
                expected_err_str += "None returned from get_file_years() for creation year\n"
                expected_err_str += "None returned from get_file_years() for year year\n"
                assert output.getvalue() == expected_err_str
