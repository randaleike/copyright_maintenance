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

from copyright_maintenance_grocsoftware.copyright_tools import SubTextMarker
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightYearsList
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParse

class TestClass01CopyrightParserBase:
    """!
    @brief Unit test for the copyright parser class
    """
    def setup_method(self):
        self.tstParser = CopyrightParse(copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                                        copyrightSearchTag = r'\([cC]\)',
                                        copyrightSearchDate = r'(\d{4})',
                                        copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                                        useUnicode = False)

    def test001CopyrightCheckDefault(self):
        """!
        @brief Test the default CopyrightParse constructor
        """
        # Test default values
        assert self.tstParser.copyrightTextStart == ""
        assert self.tstParser.copyrightTextMsg is None
        assert self.tstParser.copyrightTextTag is None
        assert self.tstParser.copyrightTextOwner is None
        assert self.tstParser.copyrightTextEol is None
        assert not self.tstParser.copyrightTextValid
        assert len(self.tstParser.copyrightYearList) == 0

    def test002CopyrightCheckAccessors(self):
        """!
        @brief Test the CopyrightParse accessor functions
        """
        # Test accessor functions
        assert self.tstParser.isCopyrightTextValid() == self.tstParser.copyrightTextValid
        assert self.tstParser.getCopyrightText() == self.tstParser.copyrightText
        yearList = self.tstParser.getCopyrightDates()
        assert len(yearList) == len(self.tstParser.copyrightYearList)

    def test003CopyrightAddOwnerNoParse(self):
        """!
        @brief Test the addOwner with noe parsed data
        """
        # False because no message parsed to add owner to
        assert not self.tstParser.addOwner("New Owner")

    def test004CopyrightReplaceOwnerNoParse(self):
        """!
        @brief Test the replace owner method
        """
        self.tstParser.replaceOwner("new owner")
        assert self.tstParser.copyrightTextOwner == "new owner"

        self.tstParser.replaceOwner("second city")
        assert self.tstParser.copyrightTextOwner == "second city"

        self.tstParser.replaceOwner("prince")
        assert self.tstParser.copyrightTextOwner == "prince"

    def test005CopyrightParseEOLNoTail(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        eolTextMarker = self.tstParser._parseEolString("", 20)
        assert eolTextMarker is None

        eolTextMarker = self.tstParser._parseEolString(" ", 20)
        assert eolTextMarker is None

    def test006CopyrightParseEOLWithTail(self):
        """!
        @brief Test the parse eol method, with EOL text
        """
        eolTextMarker = self.tstParser._parseEolString("*", 20)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 20
        assert eolTextMarker.end == 21

        eolTextMarker = self.tstParser._parseEolString(" *", 20)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 21
        assert eolTextMarker.end == 22

        eolTextMarker = self.tstParser._parseEolString(" * ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "*"
        assert eolTextMarker.start == 31
        assert eolTextMarker.end == 32

        eolTextMarker = self.tstParser._parseEolString(" ** ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "**"
        assert eolTextMarker.start == 31
        assert eolTextMarker.end == 33

        eolTextMarker = self.tstParser._parseEolString("   ** ", 30)
        assert eolTextMarker is not None
        assert eolTextMarker.text == "**"
        assert eolTextMarker.start == 33
        assert eolTextMarker.end == 35

    def test007CopyrightParseOwnerEmptyString(self):
        """!
        @brief Test the parse eol method, no EOL text
        """
        textMarker = self.tstParser._parseOwnerString("", 20)
        assert textMarker is None

        textMarker = self.tstParser._parseOwnerString(" ", 20)
        assert textMarker is None

        textMarker = self.tstParser._parseOwnerString("\t", 20)
        assert textMarker is None

        textMarker = self.tstParser._parseOwnerString("::", 20)
        assert textMarker is None

        textMarker = self.tstParser._parseOwnerString(";;", 20)
        assert textMarker is None

    def test008CopyrightParseOwnerString(self):
        """!
        @brief Test the parse owner method
        """
        ownerList = ["Wolverine", "Professor X", "professor.x@xavier.edu", "3M Corp."]
        for owner in ownerList:
            textMarker = self.tstParser._parseOwnerString(owner, 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 15
            assert textMarker.end == 15+len(owner)

            textMarker = self.tstParser._parseOwnerString(" "+owner, 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

            textMarker = self.tstParser._parseOwnerString(" "+owner+" ", 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

            textMarker = self.tstParser._parseOwnerString(" "+owner+"        *", 15)
            assert textMarker is not None
            assert textMarker.text == owner
            assert textMarker.start == 16
            assert textMarker.end == 16+len(owner)

    def test009CopyrightParseYears(self):
        """!
        @brief Test the parse years
        """
        yearParser = self.tstParser._parseYears(" 2024 ")
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 1

        assert yearParser.getFirstEntry() == 2024
        assert yearParser.getLastEntry() == 2024
        assert yearParser.getStartingStringIndex() == 1
        assert yearParser.getEndingStringIndex() == 5

        yearParser = self.tstParser._parseYears(" 2024-2025 ")
        assert yearParser.isValid()

        yearList = yearParser.getNumericYearList()
        assert len(yearList) == 2

        assert yearParser.getFirstEntry() == 2024
        assert yearParser.getLastEntry() == 2025
        assert yearParser.getStartingStringIndex() == 1
        assert yearParser.getEndingStringIndex() == 10

    def test010CopyrightParseComponents(self):
        """!
        @brief Test the parse copyright parse components, standard order, with fluff, no failure
        """
        copyrightMsgList = ["Copyright", "COPYRIGHT", "copyright"]
        copyrightTagList = ["(c)", "(C)"]
        startFluffList = ["", " ", "Owners name ", "Random text "]
        endFluffList = ["", " ", " Owners name", " Random text    *"]
        for crtag in copyrightTagList:
            for crmsg in copyrightMsgList:
                for startFluff in startFluffList:
                    for endFluff in  endFluffList:
                        testStr = startFluff+crmsg+" "+crtag+" 2024"+endFluff
                        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents(testStr)
                        assert msgMarker is not None
                        assert msgMarker.group() == crmsg
                        assert tagMarker is not None
                        assert tagMarker.group() == crtag
                        assert yearList is not None
                        assert yearList.isValid()

    def test011CopyrightParseComponentsFail(self):
        """!
        @brief Test the parse copyright parse components, standard order, failure
        """
        # Message fail
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("Random (c) 2024 owner")
        assert msgMarker is None
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert yearList.isValid()

        # Tag fail
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("copyright (r) 2024 owner")
        assert msgMarker is not None
        assert msgMarker.group() == "copyright"
        assert tagMarker is None
        assert yearList is not None
        assert yearList.isValid()

        # Year fail
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("copyright (c) notyear owner")
        assert msgMarker is not None
        assert msgMarker.group() == "copyright"
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert not yearList.isValid()

    def test012CopyrightParseComponentsDifferentOrders(self):
        """!
        @brief Test the parse copyright parse components, different orders
        """
        # Year first
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("2024 Copyright (c) owner")
        assert msgMarker is not None
        assert msgMarker.group() == "Copyright"
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert yearList.isValid()

        # owner, year first
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("2024 owner Copyright (c)")
        assert msgMarker is not None
        assert msgMarker.group() == "Copyright"
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert yearList.isValid()

        # msg tag weird
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("2024 owner (c) Copyright")
        assert msgMarker is not None
        assert msgMarker.group() == "Copyright"
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert yearList.isValid()

        # owner year
        msgMarker, tagMarker, yearList = self.tstParser._parseCopyrightComponents("owner 2024-2025 (c) Copyright")
        assert msgMarker is not None
        assert msgMarker.group() == "Copyright"
        assert tagMarker is not None
        assert tagMarker.group() == "(c)"
        assert yearList is not None
        assert yearList.isValid()

    def test013CopyrightCheckComponents(self):
        """!
        @brief Test the parse copyright check components
        """
        msgMarker = re.Match
        tagMarker = re.Match
        yearList = CopyrightYearsList('2022', r'(\d{4})', 25)
        ownerData = SubTextMarker("Owner", 34)

        # Test None inputs
        assert not self.tstParser._checkComponents(None, tagMarker, yearList, ownerData)
        assert not self.tstParser._checkComponents(msgMarker, None, yearList, ownerData)
        assert not self.tstParser._checkComponents(msgMarker, tagMarker, yearList, None)

        # Test Invalid date inputs
        yearListBad = CopyrightYearsList('', r'(\d{4})', 25)
        assert not yearListBad.isValid()
        assert not self.tstParser._checkComponents(msgMarker, tagMarker, yearListBad, ownerData)

        # Test passing case
        assert self.tstParser._checkComponents(msgMarker, tagMarker, yearList, ownerData)

    def test014CopyrightBuild(self):
        """!
        @brief Test the parse copyright build year string method
        """
        yearStr = self.tstParser._buildCopyrightYearString(2025,None)
        assert yearStr == "2025"
        yearStr = self.tstParser._buildCopyrightYearString(2022,2022)
        assert yearStr == "2022"
        yearStr = self.tstParser._buildCopyrightYearString(2022,2024)
        assert yearStr == "2022-2024"

class TestClass02CopyrightParserBase:
    def setup_method(self):
        self.tstParser = CopyrightParse(copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                                        copyrightSearchTag = r'\([cC]\)',
                                        copyrightSearchDate = r'(\d{4})',
                                        copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                                        useUnicode = False)

        self.tstMessage = " * Copyright (c) 2024-2025 Jean Grey             *"
        self.tstSolText = " * "
        self.tstEolMarker = SubTextMarker("*", len(self.tstMessage)-1)
        self.tstMsgMarker, self.tstTagMarker, self.tstYearList = self.tstParser._parseCopyrightComponents(self.tstMessage)
        self.tstOwnerData = SubTextMarker("Jean Grey", 27)

    def test001CopyrightSetParsedDataMsgNone(self):
        """!
        @brief Test the parse copyright set parsed data, msg=None
        """
        # Test msg none
        self.tstParser._setParsedCopyrightData("currentMsg", None, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == ""
        assert self.tstParser.copyrightTextStart == ""

        assert self.tstParser.copyrightTextMsg is None
        assert self.tstParser.copyrightTextTag == self.tstTagMarker.group()
        assert self.tstParser.copyrightTextOwner == self.tstOwnerData.text
        assert self.tstParser.copyrightTextEol == self.tstEolMarker.text
        assert len(self.tstParser.copyrightYearList) == 2

    def test002CopyrightSetParsedDataTagNone(self):
        """!
        @brief Test the parse copyright set parsed data, tag=None
        """
        # Test tag none
        self.tstParser._setParsedCopyrightData("currentMsg", self.tstMsgMarker, None, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == ""

        assert self.tstParser.copyrightTextStart == self.tstSolText
        assert self.tstParser.copyrightTextMsg == self.tstMsgMarker.group()
        assert self.tstParser.copyrightTextTag is None
        assert self.tstParser.copyrightTextOwner == self.tstOwnerData.text
        assert self.tstParser.copyrightTextEol == self.tstEolMarker.text
        assert len(self.tstParser.copyrightYearList) == 2

    def test003CopyrightSetParsedDataYearInvalid(self):
        """!
        @brief Test the parse copyright set parsed data, invalid year data
        """
        # Test year invalid
        invalidYearList = CopyrightYearsList("", r'(\d{4})', 10)
        self.tstParser._setParsedCopyrightData("currentMsg", self.tstMsgMarker, self.tstTagMarker, invalidYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)
        assert not self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == ""

        assert self.tstParser.copyrightTextStart == self.tstSolText
        assert self.tstParser.copyrightTextMsg == self.tstMsgMarker.group()
        assert self.tstParser.copyrightTextTag == self.tstTagMarker.group()
        assert self.tstParser.copyrightTextOwner == self.tstOwnerData.text
        assert self.tstParser.copyrightTextEol == self.tstEolMarker.text
        assert len(self.tstParser.copyrightYearList) == 0

    def test004CopyrightSetParsedDataEOLNone(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.tstParser._setParsedCopyrightData("currentMsg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, None)

        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == "currentMsg"

        assert self.tstParser.copyrightTextStart == self.tstSolText
        assert self.tstParser.copyrightTextMsg == self.tstMsgMarker.group()
        assert self.tstParser.copyrightTextTag == self.tstTagMarker.group()
        assert self.tstParser.copyrightTextOwner == self.tstOwnerData.text
        assert self.tstParser.copyrightTextEol is None
        assert len(self.tstParser.copyrightYearList) == 2

    def test005CopyrightSetParsedDataEOLNone(self):
        """!
        @brief Test the parse copyright set parsed data, eol text = None
        """
        # Test year invalid
        self.tstParser._setParsedCopyrightData("currentMsg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               self.tstOwnerData, self.tstSolText, self.tstEolMarker)

        assert self.tstParser.copyrightTextValid
        assert self.tstParser.copyrightText == "currentMsg"

        assert self.tstParser.copyrightTextStart == self.tstSolText
        assert self.tstParser.copyrightTextMsg == self.tstMsgMarker.group()
        assert self.tstParser.copyrightTextTag == self.tstTagMarker.group()
        assert self.tstParser.copyrightTextOwner == self.tstOwnerData.text
        assert self.tstParser.copyrightTextEol == self.tstEolMarker.text
        assert len(self.tstParser.copyrightYearList) == 2

    def test006CopyrightSetParsedDataOwnerNone(self):
        """!
        @brief Test the parse copyright set parsed data, owner = None
        """
        # Test year invalid
        self.tstParser._setParsedCopyrightData("currentMsg", self.tstMsgMarker, self.tstTagMarker, self.tstYearList,
                                               None, self.tstSolText, self.tstEolMarker)

        assert self.tstParser.copyrightTextValid == False
        assert self.tstParser.copyrightText == ""

        assert self.tstParser.copyrightTextStart == self.tstSolText
        assert self.tstParser.copyrightTextMsg == self.tstMsgMarker.group()
        assert self.tstParser.copyrightTextTag == self.tstTagMarker.group()
        assert self.tstParser.copyrightTextOwner is None
        assert self.tstParser.copyrightTextEol == self.tstEolMarker.text
        assert len(self.tstParser.copyrightYearList) == 2

    def test007CopyrightAddEOLNone(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = None
        """
        # Set the EOL marker
        self.tstParser.copyrightTextEol = None

        newCopyRightMsg = self.tstParser._addEolText("Current text")
        assert newCopyRightMsg == "Current text"

    def test008CopyrightAddEOL(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = *
        """
        # Set the EOL marker
        self.tstParser.copyrightText = "* Copyright (c) 2024 X-Men        *"
        self.tstParser.copyrightTextEol = '*'

        newCopyRightMsg = self.tstParser._addEolText("* Copyright (c) 2024-2025 X-Men")
        assert newCopyRightMsg == "* Copyright (c) 2024-2025 X-Men   *"

    def test009CopyrightAddEOLShort(self):
        """!
        @brief Test the parse copyright add eol marker with eol marker = *
        """
        # Set the EOL marker
        self.tstParser.copyrightText = "* Copyright (c) 2024 X-Men *"
        self.tstParser.copyrightTextEol = '*'

        newCopyRightMsg = self.tstParser._addEolText("* Copyright (c) 2024-2025 X-Men")
        assert newCopyRightMsg == "* Copyright (c) 2024-2025 X-Men*"

class TestClass03CopyrightParserBaseUniCode:
    """!
    @brief Unit test for the copyright parser class
    """
    def setup_method(self):
        self.tstParser = CopyrightParse(copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                                        copyrightSearchTag = r'\([cC]\)',
                                        copyrightSearchDate = r'(\d{4})',
                                        copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                                        useUnicode = True)

    def test001CopyrightCheckDefault(self):
        """!
        @brief Test the default CopyrightParse constructor
        """
        # Test default values
        assert self.tstParser.copyrightTextStart == ""
        assert self.tstParser.copyrightTextMsg is None
        assert self.tstParser.copyrightTextTag is None
        assert self.tstParser.copyrightTextOwner is None
        assert self.tstParser.copyrightTextEol is None
        assert not self.tstParser.copyrightTextValid
        assert len(self.tstParser.copyrightYearList) == 0
