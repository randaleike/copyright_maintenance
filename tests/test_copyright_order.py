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

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder1
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder2

# pylint: disable=protected-access

# Unit test for the copyright parser order1 class
def setup_order1():
    """!
    @brief TestClass04CopyrightParserOrder1 test setup
    """
    test_parser = CopyrightParseOrder1(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                       copyright_search_tag = r'\([cC]\)',
                                       copyright_search_date = r'(\d{4})',
                                       copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                       use_unicode = False)
    return test_parser

def test1001_is_copyright_line():
    """!
    @brief Test the is_copyright_line method
    """
    test_parser = setup_order1()
    assert test_parser.is_copyright_line(" Copyright (c) 2024 Me")
    assert test_parser.is_copyright_line(" copyright (c)  2024 Me")
    assert test_parser.is_copyright_line(" COPYRIGHT (c)  2024  Me")
    assert test_parser.is_copyright_line(" Copyright  (c)   2024-2025   foo")
    assert test_parser.is_copyright_line(" copyright (c) 2024-2025 you")
    assert test_parser.is_copyright_line(" COPYRIGHT (c) 2024,2025 You")

    assert test_parser.is_copyright_line(" Copyright (C) 2024 her")
    assert test_parser.is_copyright_line(" copyright (C) 2024 them")
    assert test_parser.is_copyright_line(" COPYRIGHT (C) 2024 other")
    assert test_parser.is_copyright_line(" COPYRIGHT (C) 2024,2025 some body")

    assert test_parser.is_copyright_line("* COPYRIGHT (C) 2024,2025 some body     *")

def test1002_is_copyright_line_missing_component_fail():
    """!
    @brief Test the is_copyright_line() method, failed for missing components
    """
    test_parser = setup_order1()
    assert not test_parser.is_copyright_line(" Copy right (c) 2024 Me")
    assert not test_parser.is_copyright_line(" Copyright (a) 2024 Me")
    assert not test_parser.is_copyright_line(" Copyright (c) Me")
    assert not test_parser.is_copyright_line(" Copyright c 2024 Me")
    assert not test_parser.is_copyright_line(" Random text 2024 Me")
    assert not test_parser.is_copyright_line(" COPYRIGHT (C) 2024,2025")

def test1003_is_copyright_line_order_fail():
    """!
    @brief Test the is_copyright_line() method, failed for invalid order
    """
    test_parser = setup_order1()
    assert not test_parser.is_copyright_line(" (c) Copyright 2024 Me")
    assert not test_parser.is_copyright_line(" 2024 Copyright (c) Me")
    assert not test_parser.is_copyright_line(" me Copyright (c) 2024")
    assert not test_parser.is_copyright_line(" Copyright (c) me 2024")
    assert not test_parser.is_copyright_line(" Copyright 2022-2024 (c) me")

def test1004_parse_copyright_msg():
    """!
    @brief Test the parse_copyright_msg() method.

    Basic test as TestClass02CopyrightParserBase does a more complete job
    of testing the component functiions that this function calls
    """
    test_parser = setup_order1()
    test_parser.parse_copyright_msg(" Copyright (c) 2024 Me")
    assert test_parser.copyright_text_valid
    assert test_parser.copyright_text == " Copyright (c) 2024 Me"
    assert test_parser.copyright_text_start == " "
    assert test_parser.copyright_text_msg == "Copyright"
    assert test_parser.copyright_text_tag == "(c)"
    assert test_parser.copyright_text_owner == "Me"
    assert test_parser.copyright_text_eol is None
    assert len(test_parser.copyright_year_list) == 1

def test1005_parse_copyright_msg_with_eol():
    """!
    @brief Test the parse_copyright_msg() method.

    Basic test as TestClass02CopyrightParserBase does a more complete job
    of testing the component functiions that this function calls
    """
    test_parser = setup_order1()
    test_parser.parse_copyright_msg(" * Copyright (c) 2024 Me                 *")
    assert test_parser.copyright_text_valid
    assert test_parser.copyright_text == " * Copyright (c) 2024 Me                 *"
    assert test_parser.copyright_text_start == " * "
    assert test_parser.copyright_text_msg == "Copyright"
    assert test_parser.copyright_text_tag == "(c)"
    assert test_parser.copyright_text_owner == "Me"
    assert test_parser.copyright_text_eol == "*"
    assert len(test_parser.copyright_year_list) == 1

def test1006_create_copyright_msg():
    """!
    @brief Test the _create_copyright_msg() method.
    """
    test_parser = setup_order1()
    return_str = test_parser._create_copyright_msg("James Kirk", "Copyright", "(c)", 2024, 2024)
    assert return_str == "Copyright (c) 2024 James Kirk"

    return_str = test_parser._create_copyright_msg("James Kirk", "Copyright", "(c)", 2022, 2024)
    assert return_str == "Copyright (c) 2022-2024 James Kirk"

    return_str = test_parser._create_copyright_msg("Mr. Spock", "Copyright", "(c)", 2024, None)
    assert return_str == "Copyright (c) 2024 Mr. Spock"

    return_str = test_parser._create_copyright_msg("Mr. Spock", "Copyright", "(c)", 2023)
    assert return_str == "Copyright (c) 2023 Mr. Spock"

def test1007_build_new_msg():
    """!
    @brief Test the build_new_copyright_msg() method.
    """
    test_parser = setup_order1()
    test_parser.parse_copyright_msg(" * Copyright (c) 2022 James Kirk               *")
    return_str = test_parser.build_new_copyright_msg(2024)
    assert return_str == "Copyright (c) 2024 James Kirk"

    return_str = test_parser.build_new_copyright_msg(2023, None)
    assert return_str == "Copyright (c) 2023 James Kirk"

    return_str = test_parser.build_new_copyright_msg(2023, 2024)
    assert return_str == "Copyright (c) 2023-2024 James Kirk"

    return_str = test_parser.build_new_copyright_msg(2024, add_start_end=True)
    assert return_str == " * Copyright (c) 2024 James Kirk               *"

    return_str = test_parser.build_new_copyright_msg(2023, None, True)
    assert return_str == " * Copyright (c) 2023 James Kirk               *"

    return_str = test_parser.build_new_copyright_msg(2023, 2024, True)
    assert return_str == " * Copyright (c) 2023-2024 James Kirk          *"

def test1008_build_new_msg_no_parse():
    """!
    @brief Test the build_new_copyright_msg() method with no parsed data
    """
    test_parser = setup_order1()
    return_str = test_parser.build_new_copyright_msg(2024)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, None)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, 2024)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2024, add_start_end=True)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, None, True)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, 2024, True)
    assert return_str is None

# Unit test for the copyright parser order1 class

def setup_order2():
    """!
    @brief TestClass05CopyrightParserOrder2 test setup
    """
    test_parser = CopyrightParseOrder2(copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                                       copyright_search_tag = r'\([cC]\)',
                                       copyright_search_date = r'(\d{4})',
                                       copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                                       use_unicode = False)
    return test_parser

def test2001_is_copyright_line():
    """!
    @brief Test the is_copyright_line method
    """
    test_parser = setup_order2()
    assert test_parser.is_copyright_line(" Me Copyright (c) 2024")
    assert test_parser.is_copyright_line(" Me copyright (c)  2024")
    assert test_parser.is_copyright_line(" ME COPYRIGHT (c)  2024")
    assert test_parser.is_copyright_line(" foo  Copyright  (c)   2024-2025")
    assert test_parser.is_copyright_line(" you copyright (c) 2024-2025")
    assert test_parser.is_copyright_line(" You COPYRIGHT (c) 2024,2025")

    assert test_parser.is_copyright_line(" her Copyright (C) 2024")
    assert test_parser.is_copyright_line(" them copyright (C) 2024")
    assert test_parser.is_copyright_line(" other COPYRIGHT (C) 2024")
    assert test_parser.is_copyright_line(" some body COPYRIGHT (C) 2024,2025")

    assert test_parser.is_copyright_line("* some body COPYRIGHT (C) 2024,2025      *")

def test2002_is_copyright_line_missing_component_fail():
    """!
    @brief Test the is_copyright_line() method, failed for missing components
    """
    test_parser = setup_order2()
    assert not test_parser.is_copyright_line(" Me Copy right (c) 2024")
    assert not test_parser.is_copyright_line(" Me Copyright (a) 2024")
    assert not test_parser.is_copyright_line(" Me Copyright (c)")
    assert not test_parser.is_copyright_line(" Me Copyright c 2024")
    assert not test_parser.is_copyright_line(" Me Random text 2024")
    assert not test_parser.is_copyright_line(" COPYRIGHT (C) 2024,2025")

def test2003_is_copyright_line_order_fail():
    """!
    @brief Test the is_copyright_line() method, failed for invalid order
    """
    test_parser = setup_order2()
    assert not test_parser.is_copyright_line(" (c) Copyright 2024 Me")
    assert not test_parser.is_copyright_line(" 2024 Copyright (c) Me")
    assert not test_parser.is_copyright_line(" Copyright (c) 2024 Me")
    assert not test_parser.is_copyright_line(" Copyright (c) me 2024")
    assert not test_parser.is_copyright_line(" Me Copyright 2022-2024 (c)")

def test2004_parse_copyright_msg():
    """!
    @brief Test the parse_copyright_msg() method.

    Basic test as TestClass02CopyrightParserBase does a more complete job
    of testing the component functiions that this function calls
    """
    test_parser = setup_order2()
    test_parser.parse_copyright_msg(" Me Copyright (c) 2024")
    assert test_parser.copyright_text_valid
    assert test_parser.copyright_text == " Me Copyright (c) 2024"
    assert test_parser.copyright_text_start == " "
    assert test_parser.copyright_text_msg == "Copyright"
    assert test_parser.copyright_text_tag == "(c)"
    assert test_parser.copyright_text_owner == "Me"
    assert test_parser.copyright_text_eol is None
    assert len(test_parser.copyright_year_list) == 1

def test2005_parse_copyright_msg_with_eol():
    """!
    @brief Test the parse_copyright_msg() method.

    Basic test as TestClass02CopyrightParserBase does a more complete job
    of testing the component functiions that this function calls
    """
    test_parser = setup_order2()
    test_parser.parse_copyright_msg(" * Me Copyright (c) 2024                 *")
    assert test_parser.copyright_text_valid
    assert test_parser.copyright_text == " * Me Copyright (c) 2024                 *"
    assert test_parser.copyright_text_start == " * "
    assert test_parser.copyright_text_msg == "Copyright"
    assert test_parser.copyright_text_tag == "(c)"
    assert test_parser.copyright_text_owner == "Me"
    assert test_parser.copyright_text_eol == "*"
    assert len(test_parser.copyright_year_list) == 1

def test2006_parse_copyright_msg_with_error():
    """!
    @brief Test the parse_copyright_msg() method.

    Basic test as TestClass02CopyrightParserBase does a more complete job
    of testing the component functiions that this function calls
    """
    test_parser = setup_order2()
    test_parser.parse_copyright_msg(" * Me (c) 2024                 *")
    assert not test_parser.copyright_text_valid
    assert test_parser.copyright_text == ""
    assert test_parser.copyright_text_start == ""

    assert test_parser.copyright_text_msg is None
    assert test_parser.copyright_text_tag == "(c)"
    assert test_parser.copyright_text_owner is None
    assert test_parser.copyright_text_eol == "*"
    assert len(test_parser.copyright_year_list) == 1

def test2007_create_copyright_msg():
    """!
    @brief Test the _create_copyright_msg() method.
    """
    test_parser = setup_order2()
    return_str = test_parser._create_copyright_msg("James Kirk", "Copyright",
                                                        "(c)", 2024, 2024)
    assert return_str == "James Kirk Copyright (c) 2024"

    return_str = test_parser._create_copyright_msg("James Kirk", "Copyright",
                                                        "(c)", 2022, 2024)
    assert return_str == "James Kirk Copyright (c) 2022-2024"

    return_str = test_parser._create_copyright_msg("Mr. Spock", "Copyright",
                                                        "(c)", 2024, None)
    assert return_str == "Mr. Spock Copyright (c) 2024"

    return_str = test_parser._create_copyright_msg("Mr. Spock", "Copyright",
                                                        "(c)", 2023)
    assert return_str == "Mr. Spock Copyright (c) 2023"

def test2008_build_new_msg():
    """!
    @brief Test the build_new_copyright_msg() method.
    """
    test_parser = setup_order2()
    test_parser.parse_copyright_msg(" * James Kirk Copyright (c) 2022               *")
    return_str = test_parser.build_new_copyright_msg(2024)
    assert return_str == "James Kirk Copyright (c) 2024"

    return_str = test_parser.build_new_copyright_msg(2023, None)
    assert return_str == "James Kirk Copyright (c) 2023"

    return_str = test_parser.build_new_copyright_msg(2023, 2024)
    assert return_str == "James Kirk Copyright (c) 2023-2024"

    return_str = test_parser.build_new_copyright_msg(2024, add_start_end=True)
    assert return_str == " * James Kirk Copyright (c) 2024               *"

    return_str = test_parser.build_new_copyright_msg(2023, None, True)
    assert return_str == " * James Kirk Copyright (c) 2023               *"

    return_str = test_parser.build_new_copyright_msg(2023, 2024, True)
    assert return_str == " * James Kirk Copyright (c) 2023-2024          *"

def test2009_build_new_msg_no_parse():
    """!
    @brief Test the build_new_copyright_msg() method with no parsed data
    """
    test_parser = setup_order2()
    return_str = test_parser.build_new_copyright_msg(2024)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, None)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, 2024)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2024, add_start_end=True)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, None, True)
    assert return_str is None

    return_str = test_parser.build_new_copyright_msg(2023, 2024, True)
    assert return_str is None
