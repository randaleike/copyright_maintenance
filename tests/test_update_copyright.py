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

import pytest
import os
import time
import _io, io, contextlib
from unittest.mock import patch, MagicMock, mock_open

from dir_init import TESTFILEPATH
from dir_init import pathincsetup
pathincsetup()
testFileBaseDir = TESTFILEPATH

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder1
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.comment_block import CommentParams

from copyright_maintenance_grocsoftware.file_dates import GetFileYears
from copyright_maintenance_grocsoftware.oscmdshell import GetCommandShell
from copyright_maintenance_grocsoftware.update_copyright import CopyrightCommentBlock
from copyright_maintenance_grocsoftware.update_copyright import UpdateCopyRightYears
from copyright_maintenance_grocsoftware.update_copyright import InsertNewCopyrightBlock

class dummyParser(CopyrightParseOrder1):
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
    @classmethod
    def setup_class(cls):
        """!
        @brief On test start set the filename
        """
        cls._testFileName = os.path.join(testFileBaseDir, "copyrighttest.h")
        cls._testFile = open(cls._testFileName, "rt", encoding="utf-8")

    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown restore the original copyright dates
        """
        cls._testFile.close()

    """!
    @brief Test the CopyrightCommentBlock class
    """
    def test001_constructor_with_default(self):
        """!
        @brief Test the default constructor
        """
        testObj = CopyrightCommentBlock(self._testFile)
        #self.assertIsInstance(testObj._copyrightParser, CopyrightParseEnglish)
        assert testObj.commentData is None
        assert isinstance(testObj.inputFile, _io.TextIOWrapper)
        assert len(testObj.copyrightBlockData) == 0

    def test002_constructor_with_partial_input(self):
        """!
        @brief Test the constructor with default copyright parser
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.pyCommentParms)
        #self.assertIsInstance(testObj._copyrightParser, CopyrightParseEnglish)
        assert testObj.commentData == CommentParams.pyCommentParms
        assert isinstance(testObj.inputFile, _io.TextIOWrapper)
        assert len(testObj.copyrightBlockData) == 0

    def test003_constructor_with_input(self):
        """!
        @brief Test the constructor with full input
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms, dummyParser)
        #self.assertIsInstance(testObj._copyrightParser, dummyParser)
        assert testObj.commentData == CommentParams.cCommentParms
        assert isinstance(testObj.inputFile, _io.TextIOWrapper)
        assert len(testObj.copyrightBlockData) == 0

    def test004_is_copyright_comment_block_no_input(self):
        """!
        @brief Test the _isCopyrightCommentBlock method, default input
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        status, text = testObj._isCopyrightCommentBlock(None, None)
        assert not status
        assert text is None

    def test005_is_copyright_comment_block_partial_input(self):
        """!
        @brief Test the _isCopyrightCommentBlock method, incomplete input
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        status, locationDict = testObj._isCopyrightCommentBlock(0, None)
        assert not status
        assert locationDict is None

        status1, locationDict1 = testObj._isCopyrightCommentBlock(None, 100)
        assert not status1
        assert locationDict1 is None

    def test004_is_copyright_comment_block_good_input(self):
        """!
        @brief Test the _isCopyrightCommentBlock method, good input
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        status, locationDict = testObj._isCopyrightCommentBlock(0, 1082)
        assert status
        assert locationDict['lineOffset'] == 3
        assert locationDict['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

    def test005_is_copyright_comment_block_post_blk_input(self):
        """!
        @brief Test the _isCopyrightCommentBlock method, post block input
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        status, locationDict = testObj._isCopyrightCommentBlock(1084, 1084+81)
        assert not status
        assert locationDict is None

    def test006_is_find_next_block_found(self):
        """!
        @brief Test the _isfindNextCopyrightBlock method, good find
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        self._testFile.seek(0)
        status, locationDict = testObj._isfindNextCopyrightBlock()
        assert status
        assert locationDict['blkStart'] == 0
        assert locationDict['blkEndEOL'] == 1082
        assert locationDict['blkEndSOL'] == 1079
        assert len(locationDict['copyrightMsgs']) == 1
        assert locationDict['copyrightMsgs'][0]['lineOffset'] == 3
        assert locationDict['copyrightMsgs'][0]['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

    def test007_is_find_next_block_not_found(self):
        """!
        @brief Test the _isfindNextCopyrightBlock method, not found
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        self._testFile.seek(1084)
        status, locationDict = testObj._isfindNextCopyrightBlock()
        assert not status
        assert locationDict['blkStart'] == 1186
        assert locationDict['blkEndEOL'] == 1291
        assert locationDict['blkEndSOL'] == 1287
        assert len(locationDict['copyrightMsgs']) == 0

    def test008_find_copyright_blocks(self):
        """!
        @brief Test the findCopyrightBlocks method, found
        """
        testObj = CopyrightCommentBlock(self._testFile, CommentParams.cCommentParms)
        locationList = testObj.findCopyrightBlocks()
        assert len(locationList) == 1
        assert locationList[0]['blkStart'] == 0
        assert locationList[0]['blkEndEOL'] == 1082
        assert locationList[0]['blkEndSOL'] == 1079
        assert len(locationList[0]['copyrightMsgs']) == 1
        assert locationList[0]['copyrightMsgs'][0]['lineOffset'] == 3
        assert locationList[0]['copyrightMsgs'][0]['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

    def test009_find_copyright_blocks_not_found(self):
        """!
        @brief Test the findCopyrightBlocks method, not found
        """
        testFileName = os.path.join(testFileBaseDir, "copyrighttest_none.h")
        testFile = open(testFileName, "rt", encoding="utf-8")

        testObj = CopyrightCommentBlock(testFile, CommentParams.cCommentParms)
        locationList = testObj.findCopyrightBlocks()
        assert len(locationList) == 0

        testFile.close()

    def test010_find_copyright_blocks_double_find(self):
        """!
        @brief Test the findCopyrightBlocks method, double found
        """
        testFileName = os.path.join(testFileBaseDir, "copyrighttest_dbl.h")
        testFile = open(testFileName, "rt", encoding="utf-8")

        testObj = CopyrightCommentBlock(testFile, CommentParams.cCommentParms)
        locationList = testObj.findCopyrightBlocks()
        assert len(locationList) == 1
        assert locationList[0]['blkStart'] == 0
        assert locationList[0]['blkEndEOL'] == 1112
        assert locationList[0]['blkEndSOL'] == 1109
        assert len(locationList[0]['copyrightMsgs']) == 2
        assert locationList[0]['copyrightMsgs'][0]['lineOffset'] == 3
        assert locationList[0]['copyrightMsgs'][0]['text'] == " Copyright (c) 2022-2023 Randal Eike\n"
        assert locationList[0]['copyrightMsgs'][1]['lineOffset'] == 40
        assert locationList[0]['copyrightMsgs'][1]['text'] == " Copyright (c) 2024-2025 Zeus\n"

        testFile.close()

    def test011_find_copyright_blocks_double_blk_find(self):
        """!
        @brief Test the findCopyrightBlocks method, double block found
        """
        testFileName = os.path.join(testFileBaseDir, "copyrighttest_dblblk.h")
        testFile = open(testFileName, "rt", encoding="utf-8")

        testObj = CopyrightCommentBlock(testFile, CommentParams.cCommentParms)
        locationList = testObj.findCopyrightBlocks()
        assert len(locationList) == 2
        assert locationList[0]['blkStart'] == 0
        assert locationList[0]['blkEndEOL'] == 1082
        assert locationList[0]['blkEndSOL'] == 1079
        assert len(locationList[0]['copyrightMsgs']) == 1
        assert locationList[0]['copyrightMsgs'][0]['lineOffset'] == 3
        assert locationList[0]['copyrightMsgs'][0]['text'] == " Copyright (c) 2022-2023 Randal Eike\n"

        assert locationList[1]['blkStart'] == 1083
        assert locationList[1]['blkEndEOL'] == 2158
        assert locationList[1]['blkEndSOL'] == 2155
        assert len(locationList[1]['copyrightMsgs']) == 1
        assert locationList[1]['copyrightMsgs'][0]['lineOffset'] == 1086
        assert locationList[1]['copyrightMsgs'][0]['text'] == " Copyright (c) 2024-2025 Odin\n"

        testFile.close()


class TestClass02CopyrightUpdate:
    """!
    @brief Test the UpdateCopyRightYears function
    """
    @classmethod
    def setup_class(cls):
        """!
        @brief On test start set the filename
        """
        cls._testFileName = os.path.join(testFileBaseDir, "copyrighttest.h")
        fileDates = GetFileYears(cls._testFileName)
        _, expectedMod = fileDates.getFileYears()
        cpGen = CopyrightParseEnglish()
        cls._yearStr = cpGen._buildCopyrightYearString(2022, expectedMod)

    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown restore the original copyright dates
        """
        newMsg = "Copyright (c) "+cls._yearStr+" Randal Eike"
        GetCommandShell().streamEdit(cls._testFileName,
                                     newMsg,
                                     "Copyright (c) 2022-2023 Randal Eike")

    def grepCheck(self, filename, searchStr):
        """!
        @brief On test teardown restore the original copyright dates
        """
        status, searchResults = GetCommandShell().seachFile(filename, searchStr)
        return status, searchResults

    def resetCopyrightMsg(self, searchStr):
        """!
        @brief On test teardown restore the original copyright dates
        """
        GetCommandShell().streamEdit(self._testFileName,
                                     searchStr,
                                     "Copyright (c) 2022-2023 Randal Eike")

    def test001_update_years(self):
        """!
        Test UpdateCopyRightYears()
        """
        def existReturn(filename):
            if filename == self._testFileName:
                return True
            elif filename == ".git":
                return False
            else:
                return False

        with patch('os.path.exists', MagicMock(side_effect = existReturn)), patch('os.path.isfile', MagicMock(return_value = True)):
            localTime = time.time()
            mockCreateStr = "01 Jan 2022 12:00:00"
            mockCreateObj = time.strptime(mockCreateStr, "%d %b %Y %H:%M:%S")
            createTime = time.mktime(mockCreateObj)
            with patch('os.path.getctime', MagicMock(return_value = createTime)), patch('os.path.getmtime', MagicMock(return_value = localTime)):
                UpdateCopyRightYears(self._testFileName)
                grepStatus, testStr = self.grepCheck(self._testFileName, r" Copyright (c)")
                self.resetCopyrightMsg("Copyright (c) 2022-2025 Randal Eike")
                assert grepStatus
                expectedMsg = " Copyright (c) 2022-2025 Randal Eike\n"
                assert expectedMsg == testStr

    def test002_update_years_get_file_years_fail(self):
        """!
        Test UpdateCopyRightYears(), GetFileYears failure
        """
        with pytest.raises(FileNotFoundError) as context:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                UpdateCopyRightYears("foo")
                expectedErrStr = "ERROR: File: \"foo\" does not exist or is not a file.\n"
                expectedErrStr += "None returned from GetFileYears() for creation year\n"
                expectedErrStr += "None returned from GetFileYears() for year year\n"
                assert output.getvalue() == expectedErrStr

class TestClass03InsertNewCopyrightBlock:
    @classmethod
    def setup_class(cls):
        """!
        @brief On test start open the input file
        """
        cls._inputFileName = os.path.join(testFileBaseDir, "copyrighttest.h")
        cls._inputFile = open(cls._inputFileName, mode='rt', encoding='utf-8')

    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown close the file
        """
        cls._inputFile.close()

    """!
    @brief Test the InsertNewCopyrightBlock function
    """
    def test001_insert_new_copyright_block_write_fail(self):
        """!
        Test InsertNewCopyrightBlock(), write file open failure
        """
        commentBlkLocation = {'blkStart': 0, 'blkEndEOL': 1082, 'blkEndSOL': 1079,
                              'copyrightMsgs': [{'lineOffset': 3, 'text':" Copyright (c) 2022-2023 Randal Eike\n"}] }
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()) as mockWrite:
                mockWrite.return_value = None
                mockWrite.side_effect = Exception(OSError)
                status = InsertNewCopyrightBlock(self._inputFile, "test.c.out", commentBlkLocation,
                                                 CommentParams.cCommentParms,
                                                 "* Copyright (c) 2022-2023 Randal Eike\n",
                                                 ["test eula"])
                assert not status
                expectedErrStr = "ERROR: Unable to open file \"test.c.out\" for writing as text file.\n"
                assert output.getvalue() == expectedErrStr

    def test002_insert_new_copyright_block_replace_all(self):
        """!
        Test InsertNewCopyrightBlock(), replace entire eula block
        """
        commentBlkLocation = {'blkStart': 0, 'blkEndEOL': 1082, 'blkEndSOL': 1079,
                              'copyrightMsgs': [{'lineOffset': 3, 'text':" Copyright (c) 2022-2023 Randal Eike\n"}] }
        testCommentMarkers = CommentParams.cCommentParms
        testCommentMarkers['blockLineStart'] = '*'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()) as mockWrite:
                status = InsertNewCopyrightBlock(self._inputFile, "test.c.out", commentBlkLocation, testCommentMarkers,
                                                "Copyright (c) 2022-2025 Randal Eike",
                                                ["test eula"])
                assert status
                mockWrite.assert_called_once_with('test.c.out', mode='wt', encoding='utf-8')
                handle = mockWrite()
                handle.write.assert_any_call('/*\n')
                handle.write.assert_any_call('* Copyright (c) 2022-2025 Randal Eike\n')
                handle.write.assert_any_call('*\n')
                handle.write.assert_any_call('* test eula\n')
                handle.write.assert_any_call('*/\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @file copyrighttest.h\n')
                handle.write.assert_any_call(' * @ingroup test_copyright_msg_replacement\n')
                handle.write.assert_any_call(' * @{\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('// Single for test\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call(' *\n')
                handle.write.assert_any_call(' * @param nothing - nothing at all\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('void uselessFunction(int nothing);\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('//=========================================================\n')
                handle.write.assert_any_call('// @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call('//\n')
                handle.write.assert_any_call('// @param nothing - nothing at all\n')
                handle.write.assert_any_call('//==========================================================\n')
                handle.write.assert_any_call('void uselessFunction2(int nothing);\n')
                handle.write.assert_any_call('/** @} */')

    def test003_insert_new_copyright_block_replace_copyright_reformat(self):
        """!
        Test InsertNewCopyrightBlock(), replace copyright, keep EULA, reformat comment block
        """
        commentBlkLocation = {'blkStart': 0, 'blkEndEOL': 1082, 'blkEndSOL': 1079,
                              'copyrightMsgs': [{'lineOffset': 3, 'text':" Copyright (c) 2022-2023 Randal Eike\n"}] }
        testCommentMarkers = CommentParams.cCommentParms
        testCommentMarkers['blockLineStart'] = '*'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()) as mockWrite:
                status = InsertNewCopyrightBlock(self._inputFile, "test.c.out", commentBlkLocation, testCommentMarkers,
                                                "Copyright (c) 2022-2024 Randal Eike",
                                                None)
                assert status
                mockWrite.assert_called_once_with('test.c.out', mode='wt', encoding='utf-8')
                handle = mockWrite()
                handle.write.assert_any_call('/*\n')
                handle.write.assert_any_call('* Copyright (c) 2022-2024 Randal Eike\n')
                handle.write.assert_any_call('* \n')
                handle.write.assert_any_call('*  Permission is hereby granted, free of charge, to any person obtaining a\n')
                handle.write.assert_any_call('*  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n')
                handle.write.assert_any_call('*/\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @file copyrighttest.h\n')
                handle.write.assert_any_call(' * @ingroup test_copyright_msg_replacement\n')
                handle.write.assert_any_call(' * @{\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('// Single for test\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call(' *\n')
                handle.write.assert_any_call(' * @param nothing - nothing at all\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('void uselessFunction(int nothing);\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('//=========================================================\n')
                handle.write.assert_any_call('// @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call('//\n')
                handle.write.assert_any_call('// @param nothing - nothing at all\n')
                handle.write.assert_any_call('//==========================================================\n')
                handle.write.assert_any_call('void uselessFunction2(int nothing);\n')
                handle.write.assert_any_call('/** @} */')

    def test004_insert_new_copyright_block_replace_all_not_start(self):
        """!
        Test InsertNewCopyrightBlock(), replace entire eula block
        """
        commentBlkLocation = {'blkStart': 3, 'blkEndEOL': 1085, 'blkEndSOL': 1082,
                              'copyrightMsgs': [{'lineOffset': 6, 'text':" Copyright (c) 2022-2023 Randal Eike\n"}] }
        testCommentMarkers = CommentParams.cCommentParms
        testCommentMarkers['blockLineStart'] = '*'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.open", mock_open()) as mockWrite:
                status = InsertNewCopyrightBlock(self._inputFile, "test.c.out", commentBlkLocation, testCommentMarkers,
                                                "Copyright (c) 2022-2026 Randal Eike",
                                                ["test eula"])
                assert status
                mockWrite.assert_called_once_with('test.c.out', mode='wt', encoding='utf-8')
                handle = mockWrite()
                handle.write.assert_any_call('//\n')
                handle.write.assert_any_call('/*\n')
                handle.write.assert_any_call('* Copyright (c) 2022-2026 Randal Eike\n')
                handle.write.assert_any_call('*\n')
                handle.write.assert_any_call('* test eula\n')
                handle.write.assert_any_call('*/\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @file copyrighttest.h\n')
                handle.write.assert_any_call(' * @ingroup test_copyright_msg_replacement\n')
                handle.write.assert_any_call(' * @{\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('// Single for test\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('/**\n')
                handle.write.assert_any_call(' * @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call(' *\n')
                handle.write.assert_any_call(' * @param nothing - nothing at all\n')
                handle.write.assert_any_call(' */\n')
                handle.write.assert_any_call('void uselessFunction(int nothing);\n')
                handle.write.assert_any_call('\n')
                handle.write.assert_any_call('//=========================================================\n')
                handle.write.assert_any_call('// @brief Useless dummy function to fill space in the file\n')
                handle.write.assert_any_call('//\n')
                handle.write.assert_any_call('// @param nothing - nothing at all\n')
                handle.write.assert_any_call('//==========================================================\n')
                handle.write.assert_any_call('void uselessFunction2(int nothing);\n')
                handle.write.assert_any_call('/** @} */')

import copyright_maintenance_grocsoftware.update_copyright as update_copyright

class TestClass04Misc:
    """!
    @brief Test the DebugPrint function
    """
    @classmethod
    def teardown_class(cls):
        """!
        @brief On test teardown close the file
        """
        update_copyright.DEBUG_LEVEL = update_copyright.DBG_MSG_NONE

    def test001_debug_none(self):
        """!
        Test DebugPrint(), current level < message level
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            update_copyright.DEBUG_LEVEL = update_copyright.DBG_MSG_NONE
            update_copyright.DebugPrint(update_copyright.DBG_MSG_MINIMAL, "test message")
            assert output.getvalue() == ""

    def test002_debug_message_equal(self):
        """!
        Test DebugPrint(), current level == message level
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            update_copyright.DEBUG_LEVEL = update_copyright.DBG_MSG_MINIMAL
            update_copyright.DebugPrint(update_copyright.DBG_MSG_MINIMAL, "test message")
            assert output.getvalue() == "Debug: test message\n"

    def test003_debug_message_lt(self):
        """!
        Test DebugPrint(), current level < message level
        """
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            update_copyright.DEBUG_LEVEL = update_copyright.DBG_MSG_VERYVERBOSE
            update_copyright.DebugPrint(update_copyright.DBG_MSG_MINIMAL, "test message")
            assert output.getvalue() == "Debug: test message\n"
