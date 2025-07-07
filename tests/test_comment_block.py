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

import os

from dir_init import TEST_FILE_PATH

from copyright_maintenance_grocsoftware.comment_block import CommentBlock
from copyright_maintenance_grocsoftware.comment_block import TextFileCommentBlock
from copyright_maintenance_grocsoftware.comment_block import CommentParams

TEST_FILE_BASE_DIR = TEST_FILE_PATH


"""
Unit test for the TextFileCommentBlock class
"""
def test01_file_comment_block():
    """!
    @brief Test the default parser of is_copyright_line() with valid message
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.txt")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        block_parser = TextFileCommentBlock(testfile)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1
        assert block_parser.comment_blk_eol_off == 105

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 105
        assert block_parser.comment_blk_eol_off == 280

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 280
        assert block_parser.comment_blk_eol_off == 314

        assert not block_parser.find_next_comment_block()

def test02_empty_file_comment_block():
    """!
    @brief Test the default parser of is_copyright_line() with valid message
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile2.txt")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        block_parser = TextFileCommentBlock(testfile)
        assert not block_parser.find_next_comment_block()

# Unit test for the TextFileCommentBlock class

def test_comment_blockid():
    """!
    @brief Test that static get_comment_markers function returns
            the correct data for the file type
    """
    comment_markers = CommentParams.get_comment_markers("testfile.c")
    assert comment_markers == CommentParams.commentBlockDelim['.c']

    comment_markers = CommentParams.get_comment_markers("testfile.cpp")
    assert comment_markers == CommentParams.commentBlockDelim['.cpp']

    comment_markers = CommentParams.get_comment_markers("testfile.h")
    assert comment_markers == CommentParams.commentBlockDelim['.h']

    comment_markers = CommentParams.get_comment_markers("testfile.hpp")
    assert comment_markers == CommentParams.commentBlockDelim['.hpp']

    comment_markers = CommentParams.get_comment_markers("testfile.py")
    assert comment_markers == CommentParams.commentBlockDelim['.py']

    comment_markers = CommentParams.get_comment_markers("testfile.sh")
    assert comment_markers == CommentParams.commentBlockDelim['.sh']

    comment_markers = CommentParams.get_comment_markers("testfile.bat")
    assert comment_markers == CommentParams.commentBlockDelim['.bat']

    comment_markers = CommentParams.get_comment_markers("testfile.")
    assert comment_markers is None

# Unit test for the CommentBlock class c, cpp, h, hpp file case

def test_c_file_comment_block():
    """!
    @brief Test all comment blocks are found in the c test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.c")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.c")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 1082

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1083
        assert block_parser.comment_blk_eol_off == 1148

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1169
        assert block_parser.comment_blk_eol_off == 1274

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1432
        assert block_parser.comment_blk_eol_off == 1650

        assert not block_parser.find_next_comment_block()

def test_h_file_comment_block():
    """!
    @brief Test all comment blocks are found in the h test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.h")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.h")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 1082

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1083
        assert block_parser.comment_blk_eol_off == 1148

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1169
        assert block_parser.comment_blk_eol_off == 1274

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1310
        assert block_parser.comment_blk_eol_off == 1528

        assert not block_parser.find_next_comment_block()

def test_cpp_file_comment_block():
    """!
    @brief Test all comment blocks are found in the cpp test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.cpp")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.cpp")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 1082

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1083
        assert block_parser.comment_blk_eol_off == 1150

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1258
        assert block_parser.comment_blk_eol_off == 1363

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1533
        assert block_parser.comment_blk_eol_off == 1751

        assert not block_parser.find_next_comment_block()

def test_hpp_file_comment_block():
    """!
    @brief Test all comment blocks are found in the hpp test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.hpp")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.hpp")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 1082

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 1083
        assert block_parser.comment_blk_eol_off == 1150

        assert not block_parser.find_next_comment_block()

# Unit test for the CommentBlock class python file case

def test_file_comment_block():
    """!
    @brief Test all comment blocks are found in the python test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.py")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.py")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 56

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 57
        assert block_parser.comment_blk_eol_off == 1299

        assert not block_parser.find_next_comment_block()

# Unit test for the CommentBlock class bash shell file case

def test_sh_file_comment_block():
    """!
    @brief Test all comment blocks are found in the bash shell test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.sh")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.sh")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 13
        assert block_parser.comment_blk_eol_off == 39

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 40
        assert block_parser.comment_blk_eol_off == 60

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 102
        assert block_parser.comment_blk_eol_off == 154

        assert not block_parser.find_next_comment_block()

# Unit test for the CommentBlock class batch file case

def test_bat_file_comment_block():
    """!
    @brief Test all comment blocks are found in the bat test file
    """
    testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.bat")
    with open(testfile_path, "rt", encoding="utf-8") as testfile:
        comment_markers = CommentParams.get_comment_markers("testfile.bat")
        block_parser = CommentBlock(testfile, comment_markers)
        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 0
        assert block_parser.comment_blk_eol_off == 38

        assert block_parser.find_next_comment_block()
        assert block_parser.comment_blk_strt_off == 112
        assert block_parser.comment_blk_eol_off == 160

        assert not block_parser.find_next_comment_block()
