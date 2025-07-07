"""@package test_programmer_tools
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

from copyright_maintenance_grocsoftware.copyright_tools import SubTextMarker
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightYearsList
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParse

# pylint: disable=protected-access

class TestClass01CopyrightParserBase:
    """!
    @brief Unit test for the copyright parser class
    """
    def setup_method(self, _):
        """!
        @brief Method setup function
        """
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                          copyright_search_tag = r'\([cC]\)',
                                          copyright_search_date = r'(\d{4})',
                                          copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                          use_unicode = False)

    def test001CopyrightCheckDefault(self):
        """!
        @brief Test the default CopyrightParse constructor
        """
        # Test default values
        assert self.test_parser.copyright_text_start == ""
        assert self.test_parser.copyright_text_msg is None
        assert self.test_parser.copyright_text_tag is None
        assert self.test_parser.copyright_text_owner is None
        assert self.test_parser.copyright_text_eol is None
        assert not self.test_parser.copyright_text_valid
        assert len(self.test_parser.copyright_year_list) == 0

    def test002CopyrightCheckAccessors(self):
        """!
        @brief Test the CopyrightParse accessor functions
        """
        # Test accessor functions
        assert self.test_parser.is_copyright_text_valid() == self.test_parser.copyright_text_valid
        assert self.test_parser.get_copyright_text() == self.test_parser.copyright_text
        year_list = self.test_parser.get_copyright_dates()
        assert len(year_list) == len(self.test_parser.copyright_year_list)

    def test003CopyrightAddOwnerNoParse(self):
        """!
        @brief Test the add_owner with noe parsed data
        """
        # False because no message parsed to add owner to
        assert not self.test_parser.add_owner("New Owner")

    def test004CopyrightReplaceOwnerNoParse(self):
        """!
        @brief Test the replace owner method
        """
        self.test_parser.replace_owner("new owner")
        assert self.test_parser.copyright_text_owner == "new owner"

        self.test_parser.replace_owner("second city")
        assert self.test_parser.copyright_text_owner == "second city"

        self.test_parser.replace_owner("prince")
        assert self.test_parser.copyright_text_owner == "prince"

    def test005CopyrightParseEOLNoTail(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        eolTextMarker = self.test_parser._parse_eol_string("", 20)
        assert eolTextMarker is None

        eolTextMarker = self.test_parser._parse_eol_string(" ", 20)
        assert eolTextMarker is None

    def test006CopyrightParseEOLWithTail(self):
        """!
        @brief Test the parse eol method, with EOL text
        """
        eolTextMarker = self.test_parser._parse_eol_string("*", 20)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 20
        assert eolTextMarker.end == 21

        eolTextMarker = self.test_parser._parse_eol_string(" *", 20)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 21
        assert eolTextMarker.end == 22

        eolTextMarker = self.test_parser._parse_eol_string(" * ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 31
        assert eolTextMarker.end == 32

        eolTextMarker = self.test_parser._parse_eol_string(" ** ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "**"
        assert eolTextMarker.start == 31
        assert eolTextMarker.end == 33

        eolTextMarker = self.test_parser._parse_eol_string("   ** ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "**"
        assert eolTextMarker.start == 33
        assert eolTextMarker.end == 35

    def test007CopyrightParseOwnerEmptyString(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        textMarker = self.test_parser._parse_owner_string("", 20)
        assert textMarker is None

        textMarker = self.test_parser._parse_owner_string(" ", 20)
        assert textMarker is None

        textMarker = self.test_parser._parse_owner_string("\t", 20)
        assert textMarker is None

        textMarker = self.test_parser._parse_owner_string("::", 20)
        assert textMarker is None

        textMarker = self.test_parser._parse_owner_string(";;", 20)
        assert textMarker is None

    def test008CopyrightParseOwnerString(self):
        """!
        @brief Test the parse owner method
        """
        ownerList = ["Wolverine", "Professor X", "professor.x@xavier.edu", "3M Corp."]
        for owner in ownerList:
            textMarker = self.test_parser._parse_owner_string(owner, 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 15
            assert textMarker.end == 15+len(owner)

            textMarker = self.test_parser._parse_owner_string(" "+owner, 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

            textMarker = self.test_parser._parse_owner_string(" "+owner+" ", 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

            textMarker = self.test_parser._parse_owner_string(" "+owner+"        *", 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

    def test009CopyrightParseYears(self):
        """!
        @brief Test the parse years
        """
        yearParser = self.test_parser._parse_years(" 2024 ")
        assert yearParser.is_valid()

        year_list = yearParser.get_numeric_year_list()
        assert len(year_list) == 1

        assert yearParser.get_first_entry() == 2024
        assert yearParser.get_last_entry() == 2024
        assert yearParser.get_starting_string_index() == 1
        assert yearParser.get_ending_string_index() == 5

        yearParser = self.test_parser._parse_years(" 2024-2025 ")
        assert yearParser.is_valid()

        year_list = yearParser.get_numeric_year_list()
        assert len(year_list) == 2

        assert yearParser.get_first_entry() == 2024
        assert yearParser.get_last_entry() == 2025
        assert yearParser.get_starting_string_index() == 1
        assert yearParser.get_ending_string_index() == 10

    def test010CopyrightParseComponents(self):
        """!
        @brief Test the parse copyright parse components, standard order, with fluff, no failure
        """
        copyright_msg_list = ["Copyright", "COPYRIGHT", "copyright"]
        copyrightTagList = ["(c)", "(C)"]
        startFluffList = ["", " ", "Owners name ", "Random text "]
        endFluffList = ["", " ", " Owners name", " Random text    *"]
        for crtag in copyrightTagList:
            for crmsg in copyright_msg_list:
                for startFluff in startFluffList:
                    for endFluff in  endFluffList:
                        test_str = startFluff+crmsg+" "+crtag+" 2024"+endFluff
                        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components(test_str)
                        assert msg_marker is not None
                        assert msg_marker.group() == crmsg
                        assert tag_marker is not None
                        assert tag_marker.group() == crtag
                        assert year_list is not None
                        assert year_list.is_valid()

    def test011CopyrightParseComponentsFail(self):
        """!
        @brief Test the parse copyright parse components, standard order, failure
        """
        # Message fail
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("Random (c) 2024 owner")
        assert msg_marker is None
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert year_list.is_valid()

        # Tag fail
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("copyright (r) 2024 owner")
        assert msg_marker is not None
        assert msg_marker.group() == "copyright"
        assert tag_marker is None
        assert year_list is not None
        assert year_list.is_valid()

        # Year fail
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("copyright (c) notyear owner")
        assert msg_marker is not None
        assert msg_marker.group() == "copyright"
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert not year_list.is_valid()

    def test012CopyrightParseComponentsDifferentOrders(self):
        """!
        @brief Test the parse copyright parse components, different orders
        """
        # Year first
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("2024 Copyright (c) owner")
        assert msg_marker is not None
        assert msg_marker.group() == "Copyright"
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert year_list.is_valid()

        # owner, year first
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("2024 owner Copyright (c)")
        assert msg_marker is not None
        assert msg_marker.group() == "Copyright"
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert year_list.is_valid()

        # msg tag weird
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("2024 owner (c) Copyright")
        assert msg_marker is not None
        assert msg_marker.group() == "Copyright"
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert year_list.is_valid()

        # owner year
        msg_marker, tag_marker, year_list = self.test_parser._parse_copyright_components("owner 2024-2025 (c) Copyright")
        assert msg_marker is not None
        assert msg_marker.group() == "Copyright"
        assert tag_marker is not None
        assert tag_marker.group() == "(c)"
        assert year_list is not None
        assert year_list.is_valid()

    def test013CopyrightCheckComponents(self):
        """!
        @brief Test the parse copyright check components
        """
        msg_marker = re.Match
        tag_marker = re.Match
        year_list = CopyrightYearsList('2022', r'(\d{4})', 25)
        owner_data = SubTextMarker("Owner", 34)

        # Test None inputs
        assert not self.test_parser._check_components(None, tag_marker, year_list, owner_data)
        assert not self.test_parser._check_components(msg_marker, None, year_list, owner_data)
        assert not self.test_parser._check_components(msg_marker, tag_marker, year_list, None)

        # Test Invalid date inputs
        yearListBad = CopyrightYearsList('', r'(\d{4})', 25)
        assert not yearListBad.is_valid()
        assert not self.test_parser._check_components(msg_marker, tag_marker, yearListBad, owner_data)

        # Test passing case
        assert self.test_parser._check_components(msg_marker, tag_marker, year_list, owner_data)

    def test014CopyrightBuild(self):
        """!
        @brief Test the parse copyright build year string method
        """
        year_str = self.test_parser._build_copyright_year_string(2025,None)
        assert year_str == "2025"
        year_str = self.test_parser._build_copyright_year_string(2022,2022)
        assert year_str == "2022"
        year_str = self.test_parser._build_copyright_year_string(2022,2024)
        assert year_str == "2022-2024"

class TestClass02CopyrightParserBase:
    def setup_method(self):
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                        copyright_search_tag = r'\([cC]\)',
                                        copyright_search_date = r'(\d{4})',
                                        copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                        use_unicode = False)

        self.tstMessage = " * Copyright (c) 2024-2025 Jean Grey             *"
        self.tstSolText = " * "
        self.tstEolMarker = SubTextMarker("*", len(self.tstMessage)-1)
        self.tstMsgMarker, self.tstTagMarker, self.tstYearList = self.test_parser._parse_copyright_components(self.tstMessage)
        self.tstOwnerData = SubTextMarker("Jean Grey", 27)

    def test001CopyrightSetParsedDataMsgNone(self):
        """!
        @brief Test the parse copyright set parsed data, msg=None
        """
        # Test msg none
        self.test_parser._set_parsed_copyright_data("current_msg", None, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""
        assert self.test_parser.copyright_text_start == ""

        assert self.test_parser.copyright_text_msg is None
        assert self.test_parser.copyright_text_tag == self.tstTagMarker.group()
        assert self.test_parser.copyright_text_owner == self.tstOwnerData.text
        assert self.test_parser.copyright_text_eol == self.tstEolMarker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test002CopyrightSetParsedDataTagNone(self):
        """!
        @brief Test the parse copyright set parsed data, tag=None
        """
        # Test tag none
        self.test_parser._set_parsed_copyright_data("current_msg", self.tstMsgMarker, None, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tstSolText
        assert self.test_parser.copyright_text_msg == self.tstMsgMarker.group()
        assert self.test_parser.copyright_text_tag is None
        assert self.test_parser.copyright_text_owner == self.tstOwnerData.text
        assert self.test_parser.copyright_text_eol == self.tstEolMarker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test003CopyrightSetParsedDataYearInvalid(self):
        """!
        @brief Test the parse copyright set parsed data, invalid year data
        """
        # Test year invalid
        invalidYearList = CopyrightYearsList("", r'(\d{4})', 10)
        self.test_parser._set_parsed_copyright_data("current_msg", self.tstMsgMarker, self.tstTagMarker, invalidYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tstSolText
        assert self.test_parser.copyright_text_msg == self.tstMsgMarker.group()
        assert self.test_parser.copyright_text_tag == self.tstTagMarker.group()
        assert self.test_parser.copyright_text_owner == self.tstOwnerData.text
        assert self.test_parser.copyright_text_eol == self.tstEolMarker.text
        assert len(self.test_parser.copyright_year_list) == 0

    def test004CopyrightSetParsedDataEOLNone(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, None)

        assert self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == "current_msg"

        assert self.test_parser.copyright_text_start == self.tstSolText
        assert self.test_parser.copyright_text_msg == self.tstMsgMarker.group()
        assert self.test_parser.copyright_text_tag == self.tstTagMarker.group()
        assert self.test_parser.copyright_text_owner == self.tstOwnerData.text
        assert self.test_parser.copyright_text_eol is None
        assert len(self.test_parser.copyright_year_list) == 2

    def test005CopyrightSetParsedDataEOLNone(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)

        assert self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == "current_msg"

        assert self.test_parser.copyright_text_start == self.tstSolText
        assert self.test_parser.copyright_text_msg == self.tstMsgMarker.group()
        assert self.test_parser.copyright_text_tag == self.tstTagMarker.group()
        assert self.test_parser.copyright_text_owner == self.tstOwnerData.text
        assert self.test_parser.copyright_text_eol == self.tstEolMarker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test006CopyrightSetParsedDataOwnerNone(self):
        """!
        @brief Test the parse copyright set parsed data, owner = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               None, self.tstSolText, self.tstEolMarker)

        assert self.test_parser.copyright_text_valid == False
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tstSolText
        assert self.test_parser.copyright_text_msg == self.tstMsgMarker.group()
        assert self.test_parser.copyright_text_tag == self.tstTagMarker.group()
        assert self.test_parser.copyright_text_owner is None
        assert self.test_parser.copyright_text_eol == self.tstEolMarker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test007CopyrightAddEOLNone(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = None
        """
        # Set the EOL marker
        self.test_parser.copyright_text_eol = None

        new_copyright_msg = self.test_parser._add_eol_text("Current text")
        assert new_copyright_msg == "Current text"

    def test008CopyrightAddEOL(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = *
        """
        # Set the EOL marker
        self.test_parser.copyright_text = "* Copyright (c) 2024 X-Men        *"
        self.test_parser.copyright_text_eol = '*'

        new_copyright_msg = self.test_parser._add_eol_text("* Copyright (c) 2024-2025 X-Men")
        assert new_copyright_msg == "* Copyright (c) 2024-2025 X-Men   *"

    def test009CopyrightAddEOLShort(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = *
        """
        # Set the EOL marker
        self.test_parser.copyright_text = "* Copyright (c) 2024 X-Men *"
        self.test_parser.copyright_text_eol = '*'

        new_copyright_msg = self.test_parser._add_eol_text("* Copyright (c) 2024-2025 X-Men")
        assert new_copyright_msg == "* Copyright (c) 2024-2025 X-Men*"

class TestClass03CopyrightParserBaseUniCode:
    """!
    @brief Unit test for the copyright parser class
    """
    def setup_method(self):
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                        copyright_search_tag = r'\([cC]\)',
                                        copyright_search_date = r'(\d{4})',
                                        copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                        use_unicode = True)

    def test001CopyrightCheckDefault(self):
        """!
        @brief Test the default CopyrightParse constructor
        """
        # Test default values
        assert self.test_parser.copyright_text_start == ""
        assert self.test_parser.copyright_text_msg is None
        assert self.test_parser.copyright_text_tag is None
        assert self.test_parser.copyright_text_owner is None
        assert self.test_parser.copyright_text_eol is None
        assert not self.test_parser.copyright_text_valid
        assert len(self.test_parser.copyright_year_list) == 0
