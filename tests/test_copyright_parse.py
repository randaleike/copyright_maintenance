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

from dir_init import TEST_FILE_PATH

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.copyright_generator import CopyrightGenerator
from copyright_maintenance_grocsoftware.copyright_finder import CopyrightFinder

TEST_FILE_BASE_DIR = TEST_FILE_PATH

# pylint: disable=protected-access

## @brief Unit test for the english copyright parser class
def test001_copyright_english_check_default():
    """!
    @brief Test create_copyright_msg.  Everything else was tested in the base and
            order unit tests
    """
    test_parser = CopyrightParseEnglish()

    test_string = test_parser.create_copyright_msg("James Kirk", 2024, 2024)
    assert test_string == "Copyright (c) 2024 James Kirk"

    test_string = test_parser.create_copyright_msg("James Kirk", 2022, 2024)
    assert test_string == "Copyright (c) 2022-2024 James Kirk"

    test_string = test_parser.create_copyright_msg("Mr. Spock", 2024, None)
    assert test_string == "Copyright (c) 2024 Mr. Spock"

    test_string = test_parser.create_copyright_msg("Mr. Spock", 2023)
    assert test_string == "Copyright (c) 2023 Mr. Spock"

class TestClass07CopyrightGenerator:
    """!
    @brief Unit test for the copyright generator class
    """
    def test000_copyright_generation_is_multi_year(self):
        """!
        @brief Test the parser of _is_multi_year()
        """
        assert not CopyrightGenerator._is_multi_year(2022, None)
        assert not CopyrightGenerator._is_multi_year(2022, 2022)
        assert CopyrightGenerator._is_multi_year(2022, 2023)

    def test001_copyright_default_generation(self):
        """!
        @brief Test the parser of get_new_copyright_msg()
        """
        test_generator = CopyrightGenerator()

        _, copyright_msg = test_generator.get_new_copyright_msg(2022, 2022)
        assert copyright_msg == 'Copyright (c) 2022 None'

        _, copyright_msg = test_generator.get_new_copyright_msg(2022,2024)
        assert copyright_msg == 'Copyright (c) 2022-2024 None'

    def test002_copyright_base_generation_single_year(self):
        """!
        @brief Test the parser of parse_copyright_msg() with valid single year
               message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        # Unchanged, create year == last modification year
        changed, new_msg = test_generator._get_new_copyright_msg(2022, 2022)
        assert not changed
        assert new_msg == copyright_msg

        # Unchanged, create year, last modification year = None
        changed, new_msg = test_generator._get_new_copyright_msg(2022)
        assert not changed
        assert new_msg == copyright_msg

        # Changed, create year > current year, last modification year = None
        changed, new_msg = test_generator._get_new_copyright_msg(2023)
        assert not changed
        assert new_msg == copyright_msg

        # Changed, create year < current year, last modification year = None
        changed, new_msg = test_generator._get_new_copyright_msg(2021)
        assert changed
        assert new_msg == "Copyright (C) 2021 Scott Summers"

    def test003_copyright_base_generation_single_year_multi_msg(self):
        """!
        @brief Test the parser of parse_copyright_msg() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022-2023 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        # Unchanged, create year = current year, last modification year = None
        changed, new_msg = test_generator._get_new_copyright_msg(2022)
        assert not changed
        assert new_msg == copyright_msg

        # Unchanged, create year <= current end year, last modification year = None
        changed, new_msg = test_generator._get_new_copyright_msg(2023)
        assert not changed
        assert new_msg == copyright_msg

        # Changed, create year < current year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2021)
        assert changed
        assert new_msg == "Copyright (C) 2021-2023 Scott Summers"

        # Changed, create year > current end year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2024)
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers"

    def test004_copyright_base_generation_multi_year(self):
        """!
        @brief Test the parser of parse_copyright_msg() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022-2023 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        # Unchanged, create year = current year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2022, 2023)
        assert not changed
        assert new_msg == copyright_msg

        # Changed, create year = current year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2022, 2024)
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers"

        # Changed, create year > current year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2023, 2024)
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers"

        # Changed, create year < current year, last modification year = new year
        changed, new_msg = test_generator._get_new_copyright_msg(2021, 2023)
        assert changed
        assert new_msg == "Copyright (C) 2021-2023 Scott Summers"

    def test005_copyright_normal_generation_no_change(self):
        """!
        @brief Test the parser of get_new_copyright_msg() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.get_new_copyright_msg(2022, 2022)
        assert not changed
        assert new_msg == copyright_msg

        copyright_msg = "Copyright (C) 2022-2024 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)
        changed, new_msg = test_generator.get_new_copyright_msg(2022, 2024)
        assert not changed
        assert new_msg == copyright_msg

        # Verify no move forward
        copyright_msg = "Copyright (C) 2022-2024 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)
        changed, new_msg = test_generator.get_new_copyright_msg(2023, 2024)
        assert not changed
        assert new_msg == copyright_msg

    def test006_copyright_normal_generation_change(self):
        """!
        @brief Test the parser of get_new_copyright_msg() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.get_new_copyright_msg(2022,2023)
        assert changed
        assert new_msg == "Copyright (C) 2022-2023 Scott Summers"

        copyright_msg = new_msg
        test_parser.parse_copyright_msg(copyright_msg)
        changed, new_msg = test_generator.get_new_copyright_msg(2022,2024)
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers"

        # Verify no move forward, multiyear
        test_parser.parse_copyright_msg(copyright_msg)
        changed, new_msg = test_generator.get_new_copyright_msg(2023, 2024)
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers"

    def test007_create_copyright_transition(self):
        """!
        @brief Test the parser of create_copyright_transition() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022-2035 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, old_msg, new_msg = test_generator.create_copyright_transition(2022,2032,2035,
                                                                               "Logan")
        assert changed
        assert old_msg == "Copyright (C) 2022-2032 Scott Summers"
        assert new_msg == "Copyright (C) 2032-2035 Logan"

        changed, old_msg, new_msg = test_generator.create_copyright_transition(2022,2035,2035,
                                                                               "Logan")
        assert not changed
        assert old_msg == "Copyright (C) 2022-2035 Scott Summers"
        assert new_msg == "Copyright (C) 2035 Logan"

    def test008_add_copyright_owner(self):
        """!
        @brief Test the parser of add_copyright_owner() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "Copyright (C) 2022 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2022,"Jean Gray")
        assert changed
        assert new_msg == "Copyright (C) 2022 Scott Summers, Jean Gray"

        copyright_msg = "Copyright (C) 2022 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2024,"Jean Gray")
        assert changed
        assert new_msg == "Copyright (C) 2022-2024 Scott Summers, Jean Gray"

        copyright_msg = "Copyright (C) 2022-2035 Scott Summers"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2035,"Jean Gray")
        assert changed
        assert new_msg == "Copyright (C) 2022-2035 Scott Summers, Jean Gray"

    def test009_add_copyright_owner_with_wrapper(self):
        """!
        @brief Test the parser of add_copyright_owner() with valid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)

        copyright_msg = "* Copyright (C) 2022 Scott Summers                   *"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2022,"Jean Gray")
        assert changed
        assert new_msg == "* Copyright (C) 2022 Scott Summers, Jean Gray        *"

        copyright_msg = "* Copyright (C) 2022 Scott Summers                   *"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2024,"Jean Gray")
        assert changed
        assert new_msg == "* Copyright (C) 2022-2024 Scott Summers, Jean Gray   *"

        copyright_msg = "* Copyright (C) 2022-2035 Scott Summers              *"
        test_parser.parse_copyright_msg(copyright_msg)

        changed, new_msg = test_generator.add_copyright_owner(2022,2035,"Jean Gray")
        assert changed
        assert new_msg == "* Copyright (C) 2022-2035 Scott Summers, Jean Gray   *"

    def test010_add_copyright_owner_failed(self):
        """!
        @brief Test the parser of add_copyright_owner() with invalid message and default regx
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)
        changed, new_msg = test_generator.add_copyright_owner(2022,2035,"Jean Gray")
        assert not changed
        assert new_msg is None

    def test011_create_new_msg(self):
        """!
        @brief Test the parser of create_new_copyright()
        """
        test_parser = CopyrightParseEnglish()
        test_generator = CopyrightGenerator(test_parser)
        new_msg = test_generator.create_new_copyright("Jean Gray", 2022, 2035)
        assert new_msg == "Copyright (c) 2022-2035 Jean Gray"

class TestClass08CopyrightFind:
    """!
    @brief Unit test for the copyright finder class
    """

    def test001_find_copyright_line_c(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in C file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.c")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 3
            assert location_dict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test001a_find_copyright_line_c(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in C file, pass parser into constructor
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.c")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder(CopyrightParseEnglish())
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 3
            assert location_dict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test002_find_copyright_line_cpp(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in cpp file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.cpp")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 3
            assert location_dict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test003_find_copyright_line_h(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in h file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.h")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 3
            assert location_dict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test004_find_copyright_line_hpp(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in hpp file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.hpp")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 3
            assert location_dict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test005_find_copyright_line_py(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in py file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert copyright_found
            assert location_dict['lineOffset'] == 133
            assert location_dict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test006_find_copyright_none_py(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in py file, no copyright message
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile_nomsg.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, None)
            assert not copyright_found
            assert location_dict is None

    def test007_find_copyright_abort_before_end_py(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in py file,
               abort search before end of file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, 200)
            assert copyright_found
            assert location_dict['lineOffset'] == 133
            assert location_dict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test008_find_copyright_none_and_abort_py(self):
        """!
        @brief Test the parser of find_next_copyright_msg() in py file, no copyright message,
               abort search before end of file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile_nomsg.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_next_copyright_msg(testfile, 0, 400)
            assert not copyright_found
            assert location_dict is None

    def test009_find_copyright_macro_py(self):
        """!
        @brief Test the parser of find_copyright_msg() in py file
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict = test_finder.find_copyright_msg(testfile)
            assert copyright_found
            assert location_dict['lineOffset'] == 133
            assert location_dict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test010_find_all_copyright_none_py(self):
        """!
        @brief Test the parser of find_all_copyright_msg() in py file, no copyright message,
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile_nomsg.py")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder()
            copyright_found, location_dict_list = test_finder.find_all_copyright_msg(testfile)
            assert not copyright_found
            assert location_dict_list is None

    def test011_find_all_copyright_c(self):
        """!
        @brief Test the parser of find_all_copyright_msg() in py file, no copyright message,
        """
        testfile_path = os.path.join(TEST_FILE_BASE_DIR, "testfile.c")
        with open(testfile_path, "rt", encoding="utf-8") as testfile:
            test_finder = CopyrightFinder(CopyrightParseEnglish())
            copyright_found, location_dict_list = test_finder.find_all_copyright_msg(testfile)
            assert copyright_found
            assert len(location_dict_list) == 1
            assert location_dict_list[0]['lineOffset'] == 3
            assert location_dict_list[0]['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'
