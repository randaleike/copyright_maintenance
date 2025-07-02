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

import os

from dir_init import TESTFILEPATH
from dir_init import pathincsetup
pathincsetup()
testFileBaseDir = TESTFILEPATH

from copyright_maintenance_grocsoftware.comment_block import CommentBlock
from copyright_maintenance_grocsoftware.comment_block import TextFileCommentBlock
from copyright_maintenance_grocsoftware.comment_block import CommentParams

class Test01TextCommentBlock:
    """!
    @brief Unit test for the TextFileCommentBlock class
    """
    def test01FileCommentBlock(self):
        """!
        @brief Test the default parser of isCopyrightLine() with valid message
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.txt")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            blockParser = TextFileCommentBlock(testFile)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1
            assert blockParser.commentBlkEOLOff == 105

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 105
            assert blockParser.commentBlkEOLOff == 280

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 280
            assert blockParser.commentBlkEOLOff == 314

            assert not blockParser.findNextCommentBlock()

    def test02EmptyFileCommentBlock(self):
        """!
        @brief Test the default parser of isCopyrightLine() with valid message
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile2.txt")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            blockParser = TextFileCommentBlock(testFile)
            assert not blockParser.findNextCommentBlock()

class Test02CommentBlock:
    """!
    @brief Unit test for the TextFileCommentBlock class
    """
    def testCommentBlockId(self):
        """!
        @brief Test that static getCommentMarkers function returns
               the correct data for the file type
        """
        commentMarkers = CommentParams.getCommentMarkers("testfile.c")
        assert commentMarkers == CommentParams.commentBlockDelim['.c']

        commentMarkers = CommentParams.getCommentMarkers("testfile.cpp")
        assert commentMarkers == CommentParams.commentBlockDelim['.cpp']

        commentMarkers = CommentParams.getCommentMarkers("testfile.h")
        assert commentMarkers == CommentParams.commentBlockDelim['.h']

        commentMarkers = CommentParams.getCommentMarkers("testfile.hpp")
        assert commentMarkers == CommentParams.commentBlockDelim['.hpp']

        commentMarkers = CommentParams.getCommentMarkers("testfile.py")
        assert commentMarkers == CommentParams.commentBlockDelim['.py']

        commentMarkers = CommentParams.getCommentMarkers("testfile.sh")
        assert commentMarkers == CommentParams.commentBlockDelim['.sh']

        commentMarkers = CommentParams.getCommentMarkers("testfile.bat")
        assert commentMarkers == CommentParams.commentBlockDelim['.bat']

        commentMarkers = CommentParams.getCommentMarkers("testfile.")
        assert commentMarkers is None


class Test03CCommentBlock:
    """!
    @brief Unit test for the CommentBlock class c, cpp, h, hpp file case
    """
    def testCFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the c test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.c")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.c")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 1082

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1083
            assert blockParser.commentBlkEOLOff == 1148

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1169
            assert blockParser.commentBlkEOLOff == 1274

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1432
            assert blockParser.commentBlkEOLOff == 1650

            assert not blockParser.findNextCommentBlock()

    def testHFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the h test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.h")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.h")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 1082

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1083
            assert blockParser.commentBlkEOLOff == 1148

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1169
            assert blockParser.commentBlkEOLOff == 1274

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1310
            assert blockParser.commentBlkEOLOff == 1528

            assert not blockParser.findNextCommentBlock()

    def testCppFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the cpp test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.cpp")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.cpp")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 1082

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1083
            assert blockParser.commentBlkEOLOff == 1150

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1258
            assert blockParser.commentBlkEOLOff == 1363

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1533
            assert blockParser.commentBlkEOLOff == 1751

            assert not blockParser.findNextCommentBlock()

    def testHppFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the hpp test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.hpp")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.hpp")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 1082

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 1083
            assert blockParser.commentBlkEOLOff == 1150

            assert not blockParser.findNextCommentBlock()

class Test04PythonCommentBlock:
    """!
    @brief Unit test for the CommentBlock class python file case
    """
    def testFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the python test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.py")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 56

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 57
            assert blockParser.commentBlkEOLOff == 1299

            assert not blockParser.findNextCommentBlock()

class Test05ShellCommentBlock:
    """!
    @brief Unit test for the CommentBlock class bash shell file case
    """
    def testFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the bash shell test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.sh")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.sh")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 13
            assert blockParser.commentBlkEOLOff == 39

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 40
            assert blockParser.commentBlkEOLOff == 60

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 102
            assert blockParser.commentBlkEOLOff == 154

            assert not blockParser.findNextCommentBlock()

class Test06BatCommentBlock:
    """!
    @brief Unit test for the CommentBlock class batch file case
    """
    def testFileCommentBlock(self):
        """!
        @brief Test all comment blocks are found in the bat test file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.bat")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            commentMarkers = CommentParams.getCommentMarkers("testfile.bat")
            blockParser = CommentBlock(testFile, commentMarkers)
            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 0
            assert blockParser.commentBlkEOLOff == 38

            assert blockParser.findNextCommentBlock()
            assert blockParser.commentBlkStrtOff == 112
            assert blockParser.commentBlkEOLOff == 160

            assert not blockParser.findNextCommentBlock()
