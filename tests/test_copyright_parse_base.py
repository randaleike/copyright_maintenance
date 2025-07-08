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
        @brief Test method setup
        """
        # pylint: disable=attribute-defined-outside-init
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                          copyright_search_tag = r'\([cC]\)',
                                          copyright_search_date = r'(\d{4})',
                                          copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                          use_unicode = False)
        # pylint: enable=attribute-defined-outside-init

    def test001_copyright_check_default(self):
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

    def test002_copyright_check_accessors(self):
        """!
        @brief Test the CopyrightParse accessor functions
        """
        # Test accessor functions
        assert self.test_parser.is_copyright_text_valid() == self.test_parser.copyright_text_valid
        assert self.test_parser.get_copyright_text() == self.test_parser.copyright_text
        year_list = self.test_parser.get_copyright_dates()
        assert len(year_list) == len(self.test_parser.copyright_year_list)

    def test003_copyright_add_owner_no_parse(self):
        """!
        @brief Test the add_owner with noe parsed data
        """
        # False because no message parsed to add owner to
        assert not self.test_parser.add_owner("New Owner")

    def test004_copyright_replace_owner_no_parse(self):
        """!
        @brief Test the replace owner method
        """
        self.test_parser.replace_owner("new owner")
        assert self.test_parser.copyright_text_owner == "new owner"

        self.test_parser.replace_owner("second city")
        assert self.test_parser.copyright_text_owner == "second city"

        self.test_parser.replace_owner("prince")
        assert self.test_parser.copyright_text_owner == "prince"

    def test005_copyright_parse_e_o_l_no_tail(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        eol_text_marker = self.test_parser._parse_eol_string("", 20)
        assert eol_text_marker is None

        eol_text_marker = self.test_parser._parse_eol_string(" ", 20)
        assert eol_text_marker is None

    def test006_copyright_parse_e_o_l_with_tail(self):
        """!
        @brief Test the parse eol method, with EOL text
        """
        eol_text_marker = self.test_parser._parse_eol_string("*", 20)
        assert eol_text_marker is not None
        assert eol_text_marker.text == "*"
        assert eol_text_marker.start == 20
        assert eol_text_marker.end == 21

        eol_text_marker = self.test_parser._parse_eol_string(" *", 20)
        assert eol_text_marker is not None
        assert eol_text_marker.text == "*"
        assert eol_text_marker.start == 21
        assert eol_text_marker.end == 22

        eol_text_marker = self.test_parser._parse_eol_string(" * ", 30)
        assert eol_text_marker is not None
        assert eol_text_marker.text == "*"
        assert eol_text_marker.start == 31
        assert eol_text_marker.end == 32

        eol_text_marker = self.test_parser._parse_eol_string(" ** ", 30)
        assert eol_text_marker is not None
        assert eol_text_marker.text == "**"
        assert eol_text_marker.start == 31
        assert eol_text_marker.end == 33

        eol_text_marker = self.test_parser._parse_eol_string("   ** ", 30)
        assert eol_text_marker is not None
        assert eol_text_marker.text == "**"
        assert eol_text_marker.start == 33
        assert eol_text_marker.end == 35

    def test007_copyright_parse_owner_empty_string(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        text_marker = self.test_parser._parse_owner_string("", 20)
        assert text_marker is None

        text_marker = self.test_parser._parse_owner_string(" ", 20)
        assert text_marker is None

        text_marker = self.test_parser._parse_owner_string("\t", 20)
        assert text_marker is None

        text_marker = self.test_parser._parse_owner_string("::", 20)
        assert text_marker is None

        text_marker = self.test_parser._parse_owner_string(";;", 20)
        assert text_marker is None

    def test008_copyright_parse_owner_string(self):
        """!
        @brief Test the parse owner method
        """
        owner_list = ["Wolverine", "Professor X", "professor.x@xavier.edu", "3M Corp."]
        for owner in owner_list:
            text_marker = self.test_parser._parse_owner_string(owner, 15)
            assert text_marker is not None
            assert text_marker.text == owner
            assert text_marker.start == 15
            assert text_marker.end == 15+len(owner)

            text_marker = self.test_parser._parse_owner_string(" "+owner, 15)
            assert text_marker is not None
            assert text_marker.text == owner
            assert text_marker.start == 16
            assert text_marker.end == 16+len(owner)

            text_marker = self.test_parser._parse_owner_string(" "+owner+" ", 15)
            assert text_marker is not None
            assert text_marker.text == owner
            assert text_marker.start == 16
            assert text_marker.end == 16+len(owner)

            text_marker = self.test_parser._parse_owner_string(" "+owner+"        *", 15)
            assert text_marker is not None
            assert text_marker.text == owner
            assert text_marker.start == 16
            assert text_marker.end == 16+len(owner)

    def test009_copyright_parse_years(self):
        """!
        @brief Test the parse years
        """
        year_parser = self.test_parser._parse_years(" 2024 ")
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 1

        assert year_parser.get_first_entry() == 2024
        assert year_parser.get_last_entry() == 2024
        assert year_parser.get_starting_string_index() == 1
        assert year_parser.get_ending_string_index() == 5

        year_parser = self.test_parser._parse_years(" 2024-2025 ")
        assert year_parser.is_valid()

        year_list = year_parser.get_numeric_year_list()
        assert len(year_list) == 2

        assert year_parser.get_first_entry() == 2024
        assert year_parser.get_last_entry() == 2025
        assert year_parser.get_starting_string_index() == 1
        assert year_parser.get_ending_string_index() == 10

    def test010_copyright_parse_components(self):
        """!
        @brief Test the parse copyright parse components, standard order, with fluff, no failure
        """
        copyright_msg_list = ["Copyright", "COPYRIGHT", "copyright"]
        copyright_tag_list = ["(c)", "(C)"]
        start_fluff_list = ["", " ", "Owners name ", "Random text "]
        end_fluff_list = ["", " ", " Owners name", " Random text    *"]
        for crtag in copyright_tag_list:
            for crmsg in copyright_msg_list:
                for start_fluff in start_fluff_list:
                    for end_fluff in  end_fluff_list:
                        test_str = start_fluff+crmsg+" "+crtag+" 2024"+end_fluff
                        mm, tm, yrs = self.test_parser._parse_copyright_components(test_str)
                        assert mm is not None
                        assert mm.group() == crmsg
                        assert tm is not None
                        assert tm.group() == crtag
                        assert yrs is not None
                        assert yrs.is_valid()

    def test011_copyright_parse_components_fail(self):
        """!
        @brief Test the parse copyright parse components, standard order, failure
        """
        # Message fail
        mm, tm, yl = self.test_parser._parse_copyright_components("Random (c) 2024 owner")
        assert mm is None
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert yl.is_valid()

        # Tag fail
        mm, tm, yl = self.test_parser._parse_copyright_components("copyright (r) 2024 owner")
        assert mm is not None
        assert mm.group() == "copyright"
        assert tm is None
        assert yl is not None
        assert yl.is_valid()

        # Year fail
        mm, tm, yl = self.test_parser._parse_copyright_components("copyright (c) notyear owner")
        assert mm is not None
        assert mm.group() == "copyright"
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert not yl.is_valid()

    def test012_copyright_parse_components_different_orders(self):
        """!
        @brief Test the parse copyright parse components, different orders
        """
        # Year first
        mm, tm, yl = self.test_parser._parse_copyright_components("2024 Copyright (c) owner")
        assert mm is not None
        assert mm.group() == "Copyright"
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert yl.is_valid()

        # owner, year first
        mm, tm, yl = self.test_parser._parse_copyright_components("2024 owner Copyright (c)")
        assert mm is not None
        assert mm.group() == "Copyright"
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert yl.is_valid()

        # msg tag weird
        mm, tm, yl = self.test_parser._parse_copyright_components("2024 owner (c) Copyright")
        assert mm is not None
        assert mm.group() == "Copyright"
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert yl.is_valid()

        # owner year
        mm, tm, yl = self.test_parser._parse_copyright_components("owner 2024-2025 (c) Copyright")
        assert mm is not None
        assert mm.group() == "Copyright"
        assert tm is not None
        assert tm.group() == "(c)"
        assert yl is not None
        assert yl.is_valid()

    def test013_copyright_check_components(self):
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
        year_list_bad = CopyrightYearsList('', r'(\d{4})', 25)
        assert not year_list_bad.is_valid()
        assert not self.test_parser._check_components(msg_marker, tag_marker,
                                                      year_list_bad, owner_data)

        # Test passing case
        assert self.test_parser._check_components(msg_marker, tag_marker, year_list, owner_data)

    def test014_copyright_build(self):
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
    """!
    Test the base copyright parsing functionality
    """
    def setup_method(self):
        """!
        @brief Test method setup
        """
        # pylint: disable=attribute-defined-outside-init
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                        copyright_search_tag = r'\([cC]\)',
                                        copyright_search_date = r'(\d{4})',
                                        copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                        use_unicode = False)

        self.tst_message = " * Copyright (c) 2024-2025 Jean Grey             *"
        self.tst_sol_text = " * "
        self.tst_eol_marker = SubTextMarker("*", len(self.tst_message)-1)
        mm, tm, yl = self.test_parser._parse_copyright_components(self.tst_message)
        self.tst_msg_marker = mm
        self.tst_tag_marker = tm
        self.tst_year_list  = yl
        self.tst_owner_data = SubTextMarker("Jean Grey", 27)
        # pylint: enable=attribute-defined-outside-init

    def test001_copyright_set_parsed_data_msg_none(self):
        """!
        @brief Test the parse copyright set parsed data, msg=None
        """
        # Test msg none
        self.test_parser._set_parsed_copyright_data("current_msg", None,
                                                    self.tst_tag_marker, self.tst_year_list,
                                                    self.tst_owner_data, self.tst_sol_text,
                                                    self.tst_eol_marker)

        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""
        assert self.test_parser.copyright_text_start == ""

        assert self.test_parser.copyright_text_msg is None
        assert self.test_parser.copyright_text_tag == self.tst_tag_marker.group()
        assert self.test_parser.copyright_text_owner == self.tst_owner_data.text
        assert self.test_parser.copyright_text_eol == self.tst_eol_marker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test002_copyright_set_parsed_data_tag_none(self):
        """!
        @brief Test the parse copyright set parsed data, tag=None
        """
        # Test tag none
        self.test_parser._set_parsed_copyright_data("current_msg", self.tst_msg_marker,
                                                    None, self.tst_year_list,
                                                    self.tst_owner_data, self.tst_sol_text,
                                                    self.tst_eol_marker)

        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tst_sol_text
        assert self.test_parser.copyright_text_msg == self.tst_msg_marker.group()
        assert self.test_parser.copyright_text_tag is None
        assert self.test_parser.copyright_text_owner == self.tst_owner_data.text
        assert self.test_parser.copyright_text_eol == self.tst_eol_marker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test003_copyright_set_parsed_data_year_invalid(self):
        """!
        @brief Test the parse copyright set parsed data, invalid year data
        """
        # Test year invalid
        invalid_year_list = CopyrightYearsList("", r'(\d{4})', 10)
        self.test_parser._set_parsed_copyright_data("current_msg", self.tst_msg_marker,
                                                    self.tst_tag_marker, invalid_year_list,
                                                    self.tst_owner_data, self.tst_sol_text,
                                                    self.tst_eol_marker)

        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tst_sol_text
        assert self.test_parser.copyright_text_msg == self.tst_msg_marker.group()
        assert self.test_parser.copyright_text_tag == self.tst_tag_marker.group()
        assert self.test_parser.copyright_text_owner == self.tst_owner_data.text
        assert self.test_parser.copyright_text_eol == self.tst_eol_marker.text
        assert len(self.test_parser.copyright_year_list) == 0

    def test004_copyright_set_parsed_data_e_o_l_none(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tst_msg_marker,
                                                    self.tst_tag_marker, self.tst_year_list,
                                                    self.tst_owner_data, self.tst_sol_text,
                                                    None)

        assert self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == "current_msg"

        assert self.test_parser.copyright_text_start == self.tst_sol_text
        assert self.test_parser.copyright_text_msg == self.tst_msg_marker.group()
        assert self.test_parser.copyright_text_tag == self.tst_tag_marker.group()
        assert self.test_parser.copyright_text_owner == self.tst_owner_data.text
        assert self.test_parser.copyright_text_eol is None
        assert len(self.test_parser.copyright_year_list) == 2

    def test005_copyright_set_parsed_data_e_o_l_none(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tst_msg_marker,
                                                    self.tst_tag_marker, self.tst_year_list,
                                                    self.tst_owner_data, self.tst_sol_text,
                                                    self.tst_eol_marker)

        assert self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == "current_msg"

        assert self.test_parser.copyright_text_start == self.tst_sol_text
        assert self.test_parser.copyright_text_msg == self.tst_msg_marker.group()
        assert self.test_parser.copyright_text_tag == self.tst_tag_marker.group()
        assert self.test_parser.copyright_text_owner == self.tst_owner_data.text
        assert self.test_parser.copyright_text_eol == self.tst_eol_marker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test006_copyright_set_parsed_data_owner_none(self):
        """!
        @brief Test the parse copyright set parsed data, owner = None
        """
        # Test year invalid
        self.test_parser._set_parsed_copyright_data("current_msg", self.tst_msg_marker,
                                                    self.tst_tag_marker, self.tst_year_list,
                                                    None, self.tst_sol_text,
                                                    self.tst_eol_marker)

        assert not self.test_parser.copyright_text_valid
        assert self.test_parser.copyright_text == ""

        assert self.test_parser.copyright_text_start == self.tst_sol_text
        assert self.test_parser.copyright_text_msg == self.tst_msg_marker.group()
        assert self.test_parser.copyright_text_tag == self.tst_tag_marker.group()
        assert self.test_parser.copyright_text_owner is None
        assert self.test_parser.copyright_text_eol == self.tst_eol_marker.text
        assert len(self.test_parser.copyright_year_list) == 2

    def test007_copyright_add_e_o_l_none(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = None
        """
        # Set the EOL marker
        self.test_parser.copyright_text_eol = None

        new_copyright_msg = self.test_parser._add_eol_text("Current text")
        assert new_copyright_msg == "Current text"

    def test008_copyright_add_e_o_l(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = *
        """
        # Set the EOL marker
        self.test_parser.copyright_text = "* Copyright (c) 2024 X-Men        *"
        self.test_parser.copyright_text_eol = '*'

        new_copyright_msg = self.test_parser._add_eol_text("* Copyright (c) 2024-2025 X-Men")
        assert new_copyright_msg == "* Copyright (c) 2024-2025 X-Men   *"

    def test009_copyright_add_e_o_l_short(self):
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
        """!
        @brief Test method setup
        """
        # pylint: disable=attribute-defined-outside-init
        self.test_parser = CopyrightParse(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                        copyright_search_tag = r'\([cC]\)',
                                        copyright_search_date = r'(\d{4})',
                                        copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                        use_unicode = True)
        # pylint: enable=attribute-defined-outside-init

    def test001_copyright_check_default(self):
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
