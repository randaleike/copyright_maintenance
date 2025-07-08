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

import re
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightYearsList

class TestClass01CopyrightYearParser:
    """!
    @brief Unit test for the copyright year parser
    """
    def test001_parse_single_year(self):
        """!
        @brief Test single year only parse
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList(" 2024 ", year_regex)
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 1

        assert year_parser.get_first_entry() == 2024
        assert year_parser.get_last_entry() == 2024
        assert year_parser.get_starting_string_index() == 1
        assert year_parser.get_ending_string_index() == 5

    def test002_parse_multi_year_dash(self):
        """!
        @brief Test multiple dashed year only parse
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList(" 2024-2025 ", year_regex)
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 2

        assert year_parser.get_first_entry() == 2024
        assert year_parser.get_last_entry() == 2025
        assert year_parser.get_starting_string_index() == 1
        assert year_parser.get_ending_string_index() == 10

    def test003_parse_multi_year_list(self):
        """!
        @brief Test multiple comma seperated year only parse
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList(" 2022,2023,2024,2025 ", year_regex)
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 4

        assert year_parser.get_first_entry() == 2022
        assert year_parser.get_last_entry() == 2025
        assert year_parser.get_starting_string_index() == 1
        assert year_parser.get_ending_string_index() == 20

    def test004_parse_multi_year_fulldate(self):
        """!
        @brief Test multiple full date parse
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList(" 01-jan-2022:31-dec-2023 ", year_regex)
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 2

        assert year_parser.get_first_entry() == 2022
        assert year_parser.get_last_entry() == 2023
        assert year_parser.get_starting_string_index() == 8
        assert year_parser.get_ending_string_index() == 24

    def test005_parse_failure(self):
        """!
        @brief Test non-date text parse
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList(" Not date text ", year_regex)
        assert not year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 0

        assert year_parser.get_first_entry() is None
        assert year_parser.get_last_entry() is None

        assert year_parser.get_starting_string_index() == -1
        assert year_parser.get_ending_string_index() == -1

    def test006_parse_year_from_date(self):
        """!
        @brief Test multiple full date parse, different formats
        """
        year_regex = re.compile(r'(\d{4})')
        year_parser = CopyrightYearsList("", year_regex)
        # pylint: disable=protected-access

        assert year_parser._parse_year_from_date_str("jan-01-2022") == 2022
        assert year_parser._parse_year_from_date_str("14-mar-2023") == 2023
        assert year_parser._parse_year_from_date_str("03/14/2021") == 2021
        assert year_parser._parse_year_from_date_str("03/14") == 1970
