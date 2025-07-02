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



from dir_init import pathincsetup
pathincsetup()

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder1
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseOrder2

class TestClass04CopyrightParserOrder1:
    """!
    @brief Unit test for the copyright parser order1 class
    """
    def setup_method(self):
        self.tstParser = CopyrightParseOrder1(copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                                              copyrightSearchTag = r'\([cC]\)',
                                              copyrightSearchDate = r'(\d{4})',
                                              copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                                              useUnicode = False)

    def test001IsCopyright(self):
        """!
        @brief Test the isCopyrightLine method
        """
        assert self.tstParser.isCopyrightLine(" Copyright (c) 2024 Me")
        assert self.tstParser.isCopyrightLine(" copyright (c)  2024 Me")
        assert self.tstParser.isCopyrightLine(" COPYRIGHT (c)  2024  Me")
        assert self.tstParser.isCopyrightLine(" Copyright  (c)   2024-2025   foo")
        assert self.tstParser.isCopyrightLine(" copyright (c) 2024-2025 you")
        assert self.tstParser.isCopyrightLine(" COPYRIGHT (c) 2024,2025 You")

        assert self.tstParser.isCopyrightLine(" Copyright (C) 2024 her")
        assert self.tstParser.isCopyrightLine(" copyright (C) 2024 them")
        assert self.tstParser.isCopyrightLine(" COPYRIGHT (C) 2024 other")
        assert self.tstParser.isCopyrightLine(" COPYRIGHT (C) 2024,2025 some body")

        assert self.tstParser.isCopyrightLine("* COPYRIGHT (C) 2024,2025 some body     *")

    def test002IsCopyrightMissingFail(self):
        """!
        @brief Test the isCopyrightLine() method, failed for missing components
        """
        assert not self.tstParser.isCopyrightLine(" Copy right (c) 2024 Me")
        assert not self.tstParser.isCopyrightLine(" Copyright (a) 2024 Me")
        assert not self.tstParser.isCopyrightLine(" Copyright (c) Me")
        assert not self.tstParser.isCopyrightLine(" Copyright c 2024 Me")
        assert not self.tstParser.isCopyrightLine(" Random text 2024 Me")
        assert not self.tstParser.isCopyrightLine(" COPYRIGHT (C) 2024,2025")

    def test003IsCopyrightOrderFail(self):
        """!
        @brief Test the isCopyrightLine() method, failed for invalid order
        """
        assert not self.tstParser.isCopyrightLine(" (c) Copyright 2024 Me")
        assert not self.tstParser.isCopyrightLine(" 2024 Copyright (c) Me")
        assert not self.tstParser.isCopyrightLine(" me Copyright (c) 2024")
        assert not self.tstParser.isCopyrightLine(" Copyright (c) me 2024")
        assert not self.tstParser.isCopyrightLine(" Copyright 2022-2024 (c) me")

    def test004ParseMsg(self):
        """!
        @brief Test the parseCopyrightMsg() method.

        Basic test as TestClass02CopyrightParserBase does a more complete job
        of testing the component functiions that this function calls
        """
        self.tstParser.parseCopyrightMsg(" Copyright (c) 2024 Me")
        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == " Copyright (c) 2024 Me"
        assert self.tstParser.copyrightTextStart == " "
        assert self.tstParser.copyrightTextMsg == "Copyright"
        assert self.tstParser.copyrightTextTag == "(c)"
        assert self.tstParser.copyrightTextOwner == "Me"
        assert self.tstParser.copyrightTextEol is None
        assert len(self.tstParser.copyrightYearList) == 1

    def test005ParseMsgWithEol(self):
        """!
        @brief Test the parseCopyrightMsg() method.

        Basic test as TestClass02CopyrightParserBase does a more complete job
        of testing the component functiions that this function calls
        """
        self.tstParser.parseCopyrightMsg(" * Copyright (c) 2024 Me                 *")
        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == " * Copyright (c) 2024 Me                 *"
        assert self.tstParser.copyrightTextStart == " * "
        assert self.tstParser.copyrightTextMsg == "Copyright"
        assert self.tstParser.copyrightTextTag == "(c)"
        assert self.tstParser.copyrightTextOwner == "Me"
        assert self.tstParser.copyrightTextEol == "*"
        assert len(self.tstParser.copyrightYearList) == 1

    def test006CreateMsg(self):
        """!
        @brief Test the _createCopyrightMsg() method.
        """
        testStr = self.tstParser._createCopyrightMsg("James Kirk", "Copyright", "(c)", 2024, 2024)
        assert testStr == "Copyright (c) 2024 James Kirk"

        testStr = self.tstParser._createCopyrightMsg("James Kirk", "Copyright", "(c)", 2022, 2024)
        assert testStr == "Copyright (c) 2022-2024 James Kirk"

        testStr = self.tstParser._createCopyrightMsg("Mr. Spock", "Copyright", "(c)", 2024, None)
        assert testStr == "Copyright (c) 2024 Mr. Spock"

        testStr = self.tstParser._createCopyrightMsg("Mr. Spock", "Copyright", "(c)", 2023)
        assert testStr == "Copyright (c) 2023 Mr. Spock"

    def test007BuildNewMsg(self):
        """!
        @brief Test the buildNewCopyrightMsg() method.
        """
        self.tstParser.parseCopyrightMsg(" * Copyright (c) 2022 James Kirk               *")
        testStr = self.tstParser.buildNewCopyrightMsg(2024)
        assert testStr == "Copyright (c) 2024 James Kirk"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None)
        assert testStr == "Copyright (c) 2023 James Kirk"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024)
        assert testStr == "Copyright (c) 2023-2024 James Kirk"

        testStr = self.tstParser.buildNewCopyrightMsg(2024, addStartEnd=True)
        assert testStr == " * Copyright (c) 2024 James Kirk               *"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None, True)
        assert testStr == " * Copyright (c) 2023 James Kirk               *"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024, True)
        assert testStr == " * Copyright (c) 2023-2024 James Kirk          *"

    def test008BuildNewMsgNoParse(self):
        """!
        @brief Test the buildNewCopyrightMsg() method with no parsed data
        """
        testStr = self.tstParser.buildNewCopyrightMsg(2024)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2024, addStartEnd=True)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None, True)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024, True)
        assert testStr is None

class TestClass05CopyrightParserOrder2:
    """!
    @brief Unit test for the copyright parser order1 class
    """
    def setup_method(self):
        self.tstParser = CopyrightParseOrder2(copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                                              copyrightSearchTag = r'\([cC]\)',
                                              copyrightSearchDate = r'(\d{4})',
                                              copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                                              useUnicode = False)

    def test001IsCopyright(self):
        """!
        @brief Test the isCopyrightLine method
        """
        assert self.tstParser.isCopyrightLine(" Me Copyright (c) 2024")
        assert self.tstParser.isCopyrightLine(" Me copyright (c)  2024")
        assert self.tstParser.isCopyrightLine(" ME COPYRIGHT (c)  2024")
        assert self.tstParser.isCopyrightLine(" foo  Copyright  (c)   2024-2025")
        assert self.tstParser.isCopyrightLine(" you copyright (c) 2024-2025")
        assert self.tstParser.isCopyrightLine(" You COPYRIGHT (c) 2024,2025")

        assert self.tstParser.isCopyrightLine(" her Copyright (C) 2024")
        assert self.tstParser.isCopyrightLine(" them copyright (C) 2024")
        assert self.tstParser.isCopyrightLine(" other COPYRIGHT (C) 2024")
        assert self.tstParser.isCopyrightLine(" some body COPYRIGHT (C) 2024,2025")

        assert self.tstParser.isCopyrightLine("* some body COPYRIGHT (C) 2024,2025      *")

    def test002IsCopyrightMissingFail(self):
        """!
        @brief Test the isCopyrightLine() method, failed for missing components
        """
        assert not self.tstParser.isCopyrightLine(" Me Copy right (c) 2024")
        assert not self.tstParser.isCopyrightLine(" Me Copyright (a) 2024")
        assert not self.tstParser.isCopyrightLine(" Me Copyright (c)")
        assert not self.tstParser.isCopyrightLine(" Me Copyright c 2024")
        assert not self.tstParser.isCopyrightLine(" Me Random text 2024")
        assert not self.tstParser.isCopyrightLine(" COPYRIGHT (C) 2024,2025")

    def test003IsCopyrightOrderFail(self):
        """!
        @brief Test the isCopyrightLine() method, failed for invalid order
        """
        assert not self.tstParser.isCopyrightLine(" (c) Copyright 2024 Me")
        assert not self.tstParser.isCopyrightLine(" 2024 Copyright (c) Me")
        assert not self.tstParser.isCopyrightLine(" Copyright (c) 2024 Me")
        assert not self.tstParser.isCopyrightLine(" Copyright (c) me 2024")
        assert not self.tstParser.isCopyrightLine(" Me Copyright 2022-2024 (c)")

    def test004ParseMsg(self):
        """!
        @brief Test the parseCopyrightMsg() method.

        Basic test as TestClass02CopyrightParserBase does a more complete job
        of testing the component functiions that this function calls
        """
        self.tstParser.parseCopyrightMsg(" Me Copyright (c) 2024")
        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == " Me Copyright (c) 2024"
        assert self.tstParser.copyrightTextStart == " "
        assert self.tstParser.copyrightTextMsg == "Copyright"
        assert self.tstParser.copyrightTextTag == "(c)"
        assert self.tstParser.copyrightTextOwner == "Me"
        assert self.tstParser.copyrightTextEol is None
        assert len(self.tstParser.copyrightYearList) == 1

    def test005ParseMsgWithEol(self):
        """!
        @brief Test the parseCopyrightMsg() method.

        Basic test as TestClass02CopyrightParserBase does a more complete job
        of testing the component functiions that this function calls
        """
        self.tstParser.parseCopyrightMsg(" * Me Copyright (c) 2024                 *")
        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == " * Me Copyright (c) 2024                 *"
        assert self.tstParser.copyrightTextStart == " * "
        assert self.tstParser.copyrightTextMsg == "Copyright"
        assert self.tstParser.copyrightTextTag == "(c)"
        assert self.tstParser.copyrightTextOwner == "Me"
        assert self.tstParser.copyrightTextEol == "*"
        assert len(self.tstParser.copyrightYearList) == 1

    def test006ParseMsgWithError(self):
        """!
        @brief Test the parseCopyrightMsg() method.

        Basic test as TestClass02CopyrightParserBase does a more complete job
        of testing the component functiions that this function calls
        """
        self.tstParser.parseCopyrightMsg(" * Me (c) 2024                 *")
        assert not self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == ""
        assert self.tstParser.copyrightTextStart == ""

        assert self.tstParser.copyrightTextMsg is None
        assert self.tstParser.copyrightTextTag == "(c)"
        assert self.tstParser.copyrightTextOwner is None
        assert self.tstParser.copyrightTextEol == "*"
        assert len(self.tstParser.copyrightYearList) == 1

    def test007CreateMsg(self):
        """!
        @brief Test the _createCopyrightMsg() method.
        """
        testStr = self.tstParser._createCopyrightMsg("James Kirk", "Copyright", "(c)", 2024, 2024)
        assert testStr == "James Kirk Copyright (c) 2024"

        testStr = self.tstParser._createCopyrightMsg("James Kirk", "Copyright", "(c)", 2022, 2024)
        assert testStr == "James Kirk Copyright (c) 2022-2024"

        testStr = self.tstParser._createCopyrightMsg("Mr. Spock", "Copyright", "(c)", 2024, None)
        assert testStr == "Mr. Spock Copyright (c) 2024"

        testStr = self.tstParser._createCopyrightMsg("Mr. Spock", "Copyright", "(c)", 2023)
        assert testStr == "Mr. Spock Copyright (c) 2023"

    def test008BuildNewMsg(self):
        """!
        @brief Test the buildNewCopyrightMsg() method.
        """
        self.tstParser.parseCopyrightMsg(" * James Kirk Copyright (c) 2022               *")
        testStr = self.tstParser.buildNewCopyrightMsg(2024)
        assert testStr == "James Kirk Copyright (c) 2024"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None)
        assert testStr == "James Kirk Copyright (c) 2023"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024)
        assert testStr == "James Kirk Copyright (c) 2023-2024"

        testStr = self.tstParser.buildNewCopyrightMsg(2024, addStartEnd=True)
        assert testStr == " * James Kirk Copyright (c) 2024               *"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None, True)
        assert testStr == " * James Kirk Copyright (c) 2023               *"

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024, True)
        assert testStr == " * James Kirk Copyright (c) 2023-2024          *"

    def test009BuildNewMsgNoParse(self):
        """!
        @brief Test the buildNewCopyrightMsg() method with no parsed data
        """
        testStr = self.tstParser.buildNewCopyrightMsg(2024)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2024, addStartEnd=True)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, None, True)
        assert testStr is None

        testStr = self.tstParser.buildNewCopyrightMsg(2023, 2024, True)
        assert testStr is None
