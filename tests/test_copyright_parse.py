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

import os


from dir_init import TESTFILEPATH
from dir_init import pathincsetup
pathincsetup()
testFileBaseDir = TESTFILEPATH

from copyright_maintenance_grocsoftware.copyright_tools import CopyrightParseEnglish
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightGenerator
from copyright_maintenance_grocsoftware.copyright_tools import CopyrightFinder

class TestClass06CopyrightParserEnglish:
    """!
    @brief Unit test for the english copyright parser class
    """
    def test001CopyrightCheckDefault(self):
        """!
        @brief Test createCopyrightMsg.  Everything else was tested in the base and order unit tests
        """
        self.tstParser = CopyrightParseEnglish()

        testStr = self.tstParser.createCopyrightMsg("James Kirk", 2024, 2024)
        assert testStr == "Copyright (c) 2024 James Kirk"

        testStr = self.tstParser.createCopyrightMsg("James Kirk", 2022, 2024)
        assert testStr == "Copyright (c) 2022-2024 James Kirk"

        testStr = self.tstParser.createCopyrightMsg("Mr. Spock", 2024, None)
        assert testStr == "Copyright (c) 2024 Mr. Spock"

        testStr = self.tstParser.createCopyrightMsg("Mr. Spock", 2023)
        assert testStr == "Copyright (c) 2023 Mr. Spock"

class TestClass07CopyrightGenerator:
    """!
    @brief Unit test for the copyright generator class
    """
    def test000CopyrightGenerationisMultiYear(self):
        """!
        @brief Test the parser of parseCopyrightMsg() with valid message and default regx
        """
        assert not CopyrightGenerator._isMultiYear(2022, None)
        assert not CopyrightGenerator._isMultiYear(2022, 2022)
        assert CopyrightGenerator._isMultiYear(2022, 2023)

    def test001CopyrightDefaultGeneration(self):
        """!
        @brief Test the parser of parseCopyrightMsg() with valid message and default regx
        """
        tstGenerator = CopyrightGenerator()

        _, defaultMsg = tstGenerator.getNewCopyrightMsg(2022, 2022)
        assert defaultMsg == 'Copyright (c) 2022 None'

        _, defaultMsg = tstGenerator.getNewCopyrightMsg(2022,2024)
        assert defaultMsg == 'Copyright (c) 2022-2024 None'

    def test002CopyrightBaseGenerationSingleYear(self):
        """!
        @brief Test the parser of parseCopyrightMsg() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        # Unchanged, create year == last modification year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2022, 2022)
        assert not changed
        assert newMsg == copyrightMsg

        # Unchanged, create year, last modification year = None
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2022)
        assert not changed
        assert newMsg == copyrightMsg

        # Changed, create year > current year, last modification year = None
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2023)
        assert not changed
        assert newMsg == copyrightMsg

        # Changed, create year < current year, last modification year = None
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2021)
        assert changed
        assert newMsg == "Copyright (C) 2021 Scott Summers"

    def test003CopyrightBaseGenerationSingleYearMultiMsg(self):
        """!
        @brief Test the parser of parseCopyrightMsg() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022-2023 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        # Unchanged, create year = current year, last modification year = None
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2022)
        assert not changed
        assert newMsg == copyrightMsg

        # Unchanged, create year <= current end year, last modification year = None
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2023)
        assert not changed
        assert newMsg == copyrightMsg

        # Changed, create year < current year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2021)
        assert changed
        assert newMsg == "Copyright (C) 2021-2023 Scott Summers"

        # Changed, create year > current end year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2024)
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers"

    def test004CopyrightBaseGenerationMultiYear(self):
        """!
        @brief Test the parser of parseCopyrightMsg() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022-2023 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        # Unchanged, create year = current year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2022, 2023)
        assert not changed
        assert newMsg == copyrightMsg

        # Changed, create year = current year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2022, 2024)
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers"

        # Changed, create year > current year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2023, 2024)
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers"

        # Changed, create year < current year, last modification year = new year
        changed, newMsg = tstGenerator._getNewCopyrightMsg(2021, 2023)
        assert changed
        assert newMsg == "Copyright (C) 2021-2023 Scott Summers"

    def test005CopyrightNormalGenerationNoChange(self):
        """!
        @brief Test the parser of getNewCopyrightMsg() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.getNewCopyrightMsg(2022, 2022)
        assert not changed
        assert newMsg == copyrightMsg

        copyrightMsg = "Copyright (C) 2022-2024 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)
        changed, newMsg = tstGenerator.getNewCopyrightMsg(2022, 2024)
        assert not changed
        assert newMsg == copyrightMsg

        # Verify no move forward
        copyrightMsg = "Copyright (C) 2022-2024 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)
        changed, newMsg = tstGenerator.getNewCopyrightMsg(2023, 2024)
        assert not changed
        assert newMsg == copyrightMsg

    def test006CopyrightNormalGenerationChange(self):
        """!
        @brief Test the parser of getNewCopyrightMsg() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.getNewCopyrightMsg(2022,2023)
        assert changed
        assert newMsg == "Copyright (C) 2022-2023 Scott Summers"

        copyrightMsg = newMsg
        self.tstParser.parseCopyrightMsg(copyrightMsg)
        changed, newMsg = tstGenerator.getNewCopyrightMsg(2022,2024)
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers"

        # Verify no move forward, multiyear
        self.tstParser.parseCopyrightMsg(copyrightMsg)
        changed, newMsg = tstGenerator.getNewCopyrightMsg(2023, 2024)
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers"

    def test007CreateCopyrightTransition(self):
        """!
        @brief Test the parser of createCopyrightTransition() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022-2035 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, oldMsg, newMsg = tstGenerator.createCopyrightTransition(2022,2032,2035,"Logan")
        assert changed
        assert oldMsg == "Copyright (C) 2022-2032 Scott Summers"
        assert newMsg == "Copyright (C) 2032-2035 Logan"

        changed, oldMsg, newMsg = tstGenerator.createCopyrightTransition(2022,2035,2035,"Logan")
        assert not changed
        assert oldMsg == "Copyright (C) 2022-2035 Scott Summers"
        assert newMsg == "Copyright (C) 2035 Logan"

    def test008AddCopyrightOwner(self):
        """!
        @brief Test the parser of addCopyrightOwner() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "Copyright (C) 2022 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2022,"Jean Gray")
        assert changed
        assert newMsg == "Copyright (C) 2022 Scott Summers, Jean Gray"

        copyrightMsg = "Copyright (C) 2022 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2024,"Jean Gray")
        assert changed
        assert newMsg == "Copyright (C) 2022-2024 Scott Summers, Jean Gray"

        copyrightMsg = "Copyright (C) 2022-2035 Scott Summers"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2035,"Jean Gray")
        assert changed
        assert newMsg == "Copyright (C) 2022-2035 Scott Summers, Jean Gray"

    def test009AddCopyrightOwnerWithWrapper(self):
        """!
        @brief Test the parser of addCopyrightOwner() with valid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)

        copyrightMsg = "* Copyright (C) 2022 Scott Summers                   *"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2022,"Jean Gray")
        assert changed
        assert newMsg == "* Copyright (C) 2022 Scott Summers, Jean Gray        *"

        copyrightMsg = "* Copyright (C) 2022 Scott Summers                   *"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2024,"Jean Gray")
        assert changed
        assert newMsg == "* Copyright (C) 2022-2024 Scott Summers, Jean Gray   *"

        copyrightMsg = "* Copyright (C) 2022-2035 Scott Summers              *"
        self.tstParser.parseCopyrightMsg(copyrightMsg)

        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2035,"Jean Gray")
        assert changed
        assert newMsg == "* Copyright (C) 2022-2035 Scott Summers, Jean Gray   *"

    def test010AddCopyrightOwnerFailed(self):
        """!
        @brief Test the parser of addCopyrightOwner() with invalid message and default regx
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)
        changed, newMsg = tstGenerator.addCopyrightOwner(2022,2035,"Jean Gray")
        assert not changed
        assert newMsg is None

    def test011CreateNewMsg(self):
        """!
        @brief Test the parser of createNewCopyright()
        """
        self.tstParser = CopyrightParseEnglish()
        tstGenerator = CopyrightGenerator(self.tstParser)
        newMsg = tstGenerator.createNewCopyright("Jean Gray", 2022, 2035)
        assert newMsg == "Copyright (c) 2022-2035 Jean Gray"

class TestClass08CopyrightFind:
    """!
    @brief Unit test for the copyright finder class
    """

    def test001FindCopyrightLineC(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in C file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.c")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 3
            assert locationDict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test001aFindCopyrightLineC(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in C file, pass parser into constructor
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.c")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder(CopyrightParseEnglish())
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 3
            assert locationDict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test002FindCopyrightLineCpp(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in cpp file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.cpp")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 3
            assert locationDict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test003FindCopyrightLineH(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in h file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.h")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 3
            assert locationDict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test004FindCopyrightLineHpp(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in hpp file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.hpp")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 3
            assert locationDict['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'

    def test005FindCopyrightLinePy(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in py file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert copyrightFound
            assert locationDict['lineOffset'] == 133
            assert locationDict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test006FindCopyrightNonePy(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in py file, no copyright message
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile_nomsg.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, None)
            assert not copyrightFound
            assert locationDict is None

    def test007FindCopyrightAbortBeforeEndPy(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in py file, abort search before end of file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, 200)
            assert copyrightFound
            assert locationDict['lineOffset'] == 133
            assert locationDict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test008FindCopyrightNoneAndAbortPy(self):
        """!
        @brief Test the parser of findNextCopyrightMsg() in py file, no copyright message, abort search before end of file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile_nomsg.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findNextCopyrightMsg(testFile, 0, 400)
            assert not copyrightFound
            assert locationDict is None

    def test009FindCopyrightMacroPy(self):
        """!
        @brief Test the parser of findCopyrightMsg() in py file
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDict = tstFinder.findCopyrightMsg(testFile)
            assert copyrightFound
            assert locationDict['lineOffset'] == 133
            assert locationDict['text'] == '# Copyright (c) 2024 Randal Eike\n'

    def test010FindAllCopyrightNonePy(self):
        """!
        @brief Test the parser of findAllCopyrightMsg() in py file, no copyright message,
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile_nomsg.py")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder()
            copyrightFound, locationDictList = tstFinder.findAllCopyrightMsg(testFile)
            assert not copyrightFound
            assert locationDictList is None

    def test011FindAllCopyrightC(self):
        """!
        @brief Test the parser of findAllCopyrightMsg() in py file, no copyright message,
        """
        testFilePath = os.path.join(testFileBaseDir, "testfile.c")
        with open(testFilePath, "rt", encoding="utf-8") as testFile:
            tstFinder = CopyrightFinder(CopyrightParseEnglish())
            copyrightFound, locationDictList = tstFinder.findAllCopyrightMsg(testFile)
            assert copyrightFound
            assert len(locationDictList) == 1
            assert locationDictList[0]['lineOffset'] == 3
            assert locationDictList[0]['text'] == ' Copyright (c) 2022-2024 Randal Eike\n'
