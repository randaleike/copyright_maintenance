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

import re


from dir_init import pathincsetup
pathincsetup()

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightYearsList

class TestClass01CopyrightYearParser:
    """!
    @brief Unit test for the copyright year parser
    """
    def test001ParseSingleYear(self):
        """!
        @brief Test single year only parse
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList(" 2024 ", yearRegex)
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 1

        assert yearParser.getFirstEntry() == 2024
        assert yearParser.getLastEntry() == 2024
        assert yearParser.getStartingStringIndex() == 1
        assert yearParser.getEndingStringIndex() == 5

    def test002ParseMultiYearDash(self):
        """!
        @brief Test multiple dashed year only parse
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList(" 2024-2025 ", yearRegex)
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 2

        assert yearParser.getFirstEntry() == 2024
        assert yearParser.getLastEntry() == 2025
        assert yearParser.getStartingStringIndex() == 1
        assert yearParser.getEndingStringIndex() == 10

    def test003ParseMultiYearList(self):
        """!
        @brief Test multiple comma seperated year only parse
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList(" 2022,2023,2024,2025 ", yearRegex)
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 4

        assert yearParser.getFirstEntry() == 2022
        assert yearParser.getLastEntry() == 2025
        assert yearParser.getStartingStringIndex() == 1
        assert yearParser.getEndingStringIndex() == 20

    def test004ParseMultiYearFulldate(self):
        """!
        @brief Test multiple full date parse
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList(" 01-jan-2022:31-dec-2023 ", yearRegex)
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 2

        assert yearParser.getFirstEntry() == 2022
        assert yearParser.getLastEntry() == 2023
        assert yearParser.getStartingStringIndex() == 8
        assert yearParser.getEndingStringIndex() == 24

    def test005ParseFailure(self):
        """!
        @brief Test non-date text parse
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList(" Not date text ", yearRegex)
        assert not yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 0

        assert yearParser.getFirstEntry() is None
        assert yearParser.getLastEntry() is None

        assert yearParser.getStartingStringIndex() == -1
        assert yearParser.getEndingStringIndex() == -1

    def test006ParseYearFromDate(self):
        """!
        @brief Test multiple full date parse, different formats
        """
        yearRegex = re.compile(r'(\d{4})')
        yearParser = CopyrightYearsList("", yearRegex)

        assert yearParser._parseYearFromDate("jan-01-2022") == 2022
        assert yearParser._parseYearFromDate("14-mar-2023") == 2023
        assert yearParser._parseYearFromDate("03/14/2021") == 2021
        assert yearParser._parseYearFromDate("03/14") == 1970
