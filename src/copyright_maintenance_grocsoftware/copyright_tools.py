"""@package copyright_tools
Scan source files and find the copyright message, parse the copyright into it's component parts and
generate updates copyright text
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

class SubTextMarker(object):
    """!
    @brief Regex trimmed substrng text and location information
    """
    def __init__(self, newText:str, originalStart:int):
        """!
        * @brief Process the input string to remove leading and trailing white space and store the results
        *
        * @param newText {string} - String data.
        * @param originalStart {int} - starting index newText within the base string
        """
        trimedText = newText.lstrip()
        ## Trimmed text value
        self.text = trimedText.rstrip()
        ## Starting position from the start of the input string plus originalStart value
        self.start = originalStart + (len(newText) - len(trimedText))
        ## Ending position from the start of the input string plus originalStart value
        self.end = self.start + len(self.text)

class CopyrightYearsList(object):
    """!
    Parse dates return data structure
    """
    def __init__(self, yearString:str, yearRegx:str, baseIndex:int = 0):
        """!
        Default constructor

        @param yearString {string} - String to parse years from
        @param yearRegx {RegExp} - Regex year matching criteria
        @param baseIndex {int} - Index of the year data substring within the original string
        """
        ## List of found years as strings
        self._years = []
        ## List of found years as integers
        self._intyears = []
        ## Start index of the first date text within the parsed input string
        self._start = -1
        ## End index of the last date text within the parsed input string
        self._end = -1

        for yearMatch in re.finditer(yearRegx, yearString):
            # Get the found year
            self._years.append(yearMatch.group())
            self._intyears.append(self._parseYearFromDate(yearMatch.group()))

            if self._start == -1:
                self._start = yearMatch.start() + baseIndex
            if (yearMatch.end() + baseIndex) > self._end:
                self._end = yearMatch.end() + baseIndex

    def _parseYearFromDate(self, yearStr:str)->int:
        """!
        @brief Convert year text to year int
        @param yearStr {string} - Date string to convert
        @returns int - Year as a numeric value
        """
        yearMatch = re.search(r'(\d{4})', yearStr)
        if yearMatch is not None:
            return int(yearMatch.group())
        else:
            return 1970

    def isValid(self)->bool:
        """!
        @brief - Determine if anything was added to the list

        @returns - True if list is not empty, else false
        """
        if self._intyears:
            return True
        else:
            return False

    def getNumericYearList(self)->list:
        """!
        @brief Pull the numeric year data from the years list

        @returns int[] - Numeric List of years
        """
        return self._intyears

    def getFirstEntry(self):
        """!
        @brief Get the first year entry

        @returns Entry 0 or None if the list is empty
        """
        if len(self._intyears) > 0:
            return self._intyears[0]
        else:
            return None

    def getLastEntry(self)->int|None:
        """!
        @brief Get the last year entry

        @returns Last year entry or None if the list is empty
        """
        if len(self._intyears) > 0:
            return self._intyears[-1]
        else:
            return None

    def getStartingStringIndex(self)->int:
        """!
        @brief Return the starting index of first year in the year list.
               Returns -1 if the list is empty.

        @returns int - Starting index of the first entry or -1 if list is empty
        """
        return self._start

    def getEndingStringIndex(self)->int:
        """!
        @brief Return the ending index of last year in the year list.
               Returns -1 if the list is empty.

        @returns int - Starting index of the first entry or -1 if list is empty
        """
        return self._end


class CopyrightParse(object):
    """!
    @brief Copyright parsing and new message class

    Utility class used to parse the existing copyright message into it's
    component parts and generate a new copyright message if the copyright
    years change.
    """

    def __init__(self, copyrightSearchMsg:str, copyrightSearchTag:str, copyrightSearchDate:str,
                 copyrightOwnerSpec:str, useUnicode:bool = False):
        """!
        @brief Constructor

        @param copyrightSearchMsg (string): Regular expresssion string used to identify
                                            the copyright word from the input
                                            copyright message string
        @param copyrightSearchTag (string): Regular expresssion string used to identify
                                            the copyright tag marker from the input
                                            copyright message string
        @param copyrightSearchDate (string): Regular expresssion string used to parse the
                                             date vaule(s) from the input copyright
                                             message string
        @param copyrightOwnerSpec (string): Regular expresssion containing the allowed owner
                                            characters
        @param useUnicode (bool) - Set to true if unicode matching is required.
                                   Default is ASCII only processing
        """

        ## Actual text of the copyright message line
        self.copyrightText = ""

        if not useUnicode:
            regxFlags = re.ASCII
        else:
            regxFlags = re.UNICODE

        ## Regex expression for the copyright part of the copyright string
        self.copyrightRegxMsg = re.compile(copyrightSearchMsg, regxFlags)
        ## Regex expression for the copyright tag of the copyright string
        self.copyrightRegxTag = re.compile(copyrightSearchTag, regxFlags)
        ## Regex expression for the copyright year(s) of the copyright string
        self.copyrightRegxYear = re.compile(copyrightSearchDate, regxFlags)
        ## Regex expression for the copyright owner text of the copyright string
        self.copyrightRegxOwner = re.compile(copyrightOwnerSpec, regxFlags)

        ## Copyright message valid flag. False until a valid copyright message is found
        self.copyrightTextValid = False
        ## Any text preceeding the valid copyright string
        self.copyrightTextStart = ""
        ## Any non-white text following the valid copyright string
        self.copyrightTextEol = None

        ## Text from the input copyright string that matched the self.copyrightRegxMsg criteria
        self.copyrightTextMsg = None
        ## Text from the input copyright string that matched the self.copyrightRegxTag criteria
        self.copyrightTextTag = None
        ## Text from the input copyright string that matched the self.copyrightRegxOwner criteria
        self.copyrightTextOwner = None

        ## List of years from the input copyright string that matched the self.copyrightRegxYear criteria
        self.copyrightYearList = []

    def isCopyrightTextValid(self)->bool:
        """!
        @brief Determine if a previous parse was run and valid

        @return Bool - True, Copyright line was parsed and was valid
        """
        return self.copyrightTextValid

    def getCopyrightText(self)->str:
        """!
        @brief Get the last valid parsed copyright text

        @return string - Last parsed copyright text original string
        """
        return self.copyrightText

    def getCopyrightDates(self)->list:
        """!
        @brief Get the last valid parsed copyright date list

        @return int list - List of parsed copyright years
        """
        return self.copyrightYearList

    def addOwner(self, newOwner:str)->bool:
        """!
        @brief Add an owner to the ownership string

        @param newOwner (string): New owner name

        @return bool - True if successfully added, else False
        """
        if self.copyrightTextValid:
            self.copyrightTextOwner += ", "
            self.copyrightTextOwner += newOwner
            return True
        else:
            return False

    def replaceOwner(self, newOwner:str)->bool:
        """!
        @brief Replace the ownership string with a new ownership string

        @param newOwner (string): New owner name

        @return bool - True if successfully added, else False
        """
        self.copyrightTextOwner = newOwner
        return True

    def _parseEolString(self, testString:str, baseIndex:int = 0)->SubTextMarker|None:
        """!
        @brief Parse the EOL text string out of the message substring.

        The owner string is defined as any regex match in the
        copyrightEolTag constructor input parameter.

        @param testString (string): Sub-string to parse
        @param baseIndex (integer): Starting index value of the input sub-string
                                    to parse within the full copyright string.
                                    Used to properly set 'start' values within
                                    the full string.  Default = 0.

        @return SubTextMarker object containing EOL text data or
                None if there is no EOL text.
        """
        # Determine if an EOL marker exists
        eolMarker = testString
        eolMarker = eolMarker.strip()

        # ignore all spaces pad.
        if eolMarker == '':
            eolData = None
        else:
            eolStartIndex = baseIndex + re.search(r'[^ ]', testString).start()
            eolData = SubTextMarker(eolMarker, eolStartIndex)

        return eolData

    def _parseOwnerString(self, testString:str, baseIndex:int = 0)->SubTextMarker|None:
        """!
        @brief Parse the owner string out of the message substring.

        The owner string is defined as any regex match in the
        copyrightEolTag constructor input parameter.

        @param testString (string): Sub-string to parse
        @param baseIndex (integer): Starting index value of the input sub-string
                                    to parse within the full copyright string.
                                    Used to properly set 'start' values within
                                    the full string.  Default = 0.

        @return SubTextMarker object containing owner text data or
                None if there is no valid owner string
        """
        index = 0
        while index < len(testString):
            if re.match(self.copyrightRegxOwner, testString[index]) is None:
                break
            index += 1

        # Found end of owner, find start of owner string
        owner = testString[:index]
        owner = owner.strip()

        if owner == '':
            ownerData = None
        else:
            ownerStartIndex = baseIndex + re.search(r'[^ ]', testString[:index]).start()
            ownerData = SubTextMarker(owner, ownerStartIndex)

        return ownerData

    def _parseYears(self, currentMsg:str)->CopyrightYearsList:
        """!
        @brief Parse the dates from the input string

        @param currentMsg (string): Current copyright message

        @return CopyrightYearsList object list of matching date values
        """
        return CopyrightYearsList(currentMsg, self.copyrightRegxYear, 0)

    def _parseCopyrightComponents(self, currentMsg:str)->tuple:
        """!
        @brief Parse the copyright line into it's components

        @param currentMsg (string): Current copyright message

        @return re.Match - Copyright match output or None if no match found
        @return re.Match - Copyright tag match output or None if no match found
        @return CopyrightYearsList object - List of copyright year matches
        """
        msgMarker = re.search(self.copyrightRegxMsg, currentMsg)
        tagMarker = re.search(self.copyrightRegxTag, currentMsg)
        yearList  = self._parseYears(currentMsg)

        return msgMarker, tagMarker, yearList

    def _checkComponents(self, msgMarker:re.Match|None, tagMarker:re.Match|None,
                         yearList:CopyrightYearsList, owner:SubTextMarker|None)->bool:
        """!
        @brief Determine if the current line matches the copyright search criteria

        @param msgMarker {re.Match} - Copyright match output or None if no match found
        @param tagMarker {re.Match} - Copyright tag match output or None if no match found
        @param yearList {CopyrightYearsList} - List of copyright year matches
        @param owner {SubTextMarker} - Owner SubTextMarker object

        @return bool - True if regx search criteria matched, else False
        """

        # Check if all the components exist
        if ((msgMarker is not None) and
            (tagMarker is not None) and
            (yearList.isValid()) and
            (owner is not None)):

            return True
        else:
            # Missing one or more components
            return False

    def _setParsedCopyrightData(self, currentMsg:str, msgMarker:re.Match|None, tagMarker:re.Match|None,
                                yearList:CopyrightYearsList, owner:SubTextMarker|None, solText:str,
                                eolMarker:SubTextMarker):
        """!
        @brief Set the parsed copyright data elements

        @param currentMsg {string} - Current message
        @param msgMarker {re.Match} - Copyright match output or None if no match found
        @param tagMarker {re.Match} - Copyright tag match output or None if no match found
        @param yearList {CopyrightYearsList} - List of copyright year matches
        @param owner {SubTextMarker} - Owner SubTextMarker object or None if owner text
                                       was not found
        @param solText {string} - Start of line (SOL) text
        @param eolMarker {SubTextMarker} - End of line (EOL) SubTextMarker object or
                                           None if no EOL text exists
        """
        self.copyrightTextValid = True

        if msgMarker is not None:
            self.copyrightTextStart = solText
            self.copyrightTextMsg = msgMarker.group()
        else:
            self.copyrightTextValid = False

        if tagMarker is not None:
            self.copyrightTextTag = tagMarker.group()
        else:
            self.copyrightTextValid = False

        if yearList.isValid():
            self.copyrightYearList.clear()
            self.copyrightYearList.extend(yearList.getNumericYearList())
        else:
            self.copyrightTextValid = False

        if owner is not None:
            self.copyrightTextOwner = owner.text
        else:
            self.copyrightTextValid = False

        if eolMarker is not None:
            self.copyrightTextEol = eolMarker.text

        if self.copyrightTextValid:
            self.copyrightText = currentMsg

    def _addEolText(self, newCopyRightMsg:str)->str:
        """!
        @brief Append the EOL text to the new copyright message

        @param newCopyRightMsg (string) Current copyright message to append to

        @return string newCopyRightMsg with self.copyrightTextEol appended
        """
        # Determine if eol text exists and should be added
        if self.copyrightTextEol is not None:
            eolMarker = self.copyrightText.rfind(self.copyrightTextEol)
            padLen = eolMarker - len(newCopyRightMsg)

            count = 0
            while count < padLen:
                newCopyRightMsg += " "
                count+=1

            newCopyRightMsg += self.copyrightTextEol

        return newCopyRightMsg

    def _buildCopyrightYearString(self, createYear:int, lastModYear:int|None = None)->str:
        """!
        @brief Build the proper copyright year string
        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date or None
        @return string : proper constructed year string
        """
        if lastModYear is not None:
            if createYear == lastModYear:
                yearString = str(createYear)
            else:
                yearString = str(createYear)+"-"+str(lastModYear)
        else:
            yearString = str(createYear)

        return yearString

class CopyrightParseOrder1(CopyrightParse):
    """!
    @brief Copyright order parsing and new message class

    Add order setup to the copyright parsing and generation functions.
    Expected order1 = CopyrightMsg CopyrightTag CopyrightYears CopyrightOwner
    """

    def isCopyrightLine(self, copyrightString:str)->bool:
        """!
        @brief Check if the input text is a copyright message with
               all the required components and in the correct order
        @param copyrightString (string) Line of text to check
        @return boolean - True if contents match regex criteria and order is correct, else False
        """
        match = False   # assume failure

        # Get base components
        msgMarker, tagMarker, yearList = self._parseCopyrightComponents(copyrightString)

        # Get owner data
        if yearList.isValid():
            endOfDates = yearList.getEndingStringIndex()
            ownerData = self._parseOwnerString(copyrightString[endOfDates:], endOfDates)

            # Check components
            if self._checkComponents(msgMarker, tagMarker, yearList, ownerData):
                # Check if the fields are in the correct order
                if ((msgMarker.end() < tagMarker.start()) and
                    (tagMarker.end() < yearList.getStartingStringIndex()) and
                    (endOfDates < ownerData.start)):
                    # Correct order
                    match = True

        return match

    def parseCopyrightMsg(self, copyrightString:str):
        """!
        @brief Parse the input copyright string into it's components

        @param copyrightString - Current copyright message
        """
        # Get base components
        msgMarker, tagMarker, yearList = self._parseCopyrightComponents(copyrightString)

        # Get owner data
        endOfDates = yearList.getEndingStringIndex()
        ownerData = self._parseOwnerString(copyrightString[endOfDates:], endOfDates)

        # Get end of line data
        endOfOwner = ownerData.start + len(ownerData.text)
        eolData = self._parseEolString(copyrightString[endOfOwner:], endOfOwner)

        # Get start of line text data
        solText = copyrightString[:msgMarker.start()]

        # Assign data values
        self._setParsedCopyrightData(copyrightString, msgMarker, tagMarker, yearList, ownerData, solText, eolData)

    def _createCopyrightMsg(self, owner:str, copyrightMsgText:str, copyrightTagText:str,
                            createYear:int, lastModYear:int|None = None)->str:
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Copyright owner text
        @param copyrightMsgText (string): Copyright message text
        @param copyrightTagText (string): Copyright tag text
        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date

        @return string : New copyright message
        """
        yearString = self._buildCopyrightYearString(createYear, lastModYear)
        newCopyRightMsg = copyrightMsgText+" "
        newCopyRightMsg += copyrightTagText+" "
        newCopyRightMsg += yearString+" "
        newCopyRightMsg += owner

        return newCopyRightMsg

    def buildNewCopyrightMsg(self, createYear:int, lastModYear:int|None = None, addStartEnd:bool = False)->str:
        """!
        @brief Generate a new copyright message for the input years

        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date or None
        @param addStartEnd (bool): True (default), add the start and eol text to the message
                                   False, ignore the start and eol text

        @return string : New copyright message or None if no copyright message was parsed
        """
        if self.copyrightTextValid:
            # Determine if start of line text should be added
            if addStartEnd:
                newCopyRightMsg = self.copyrightTextStart
            else:
                newCopyRightMsg = ""

            # Output text in order
            newCopyRightMsg += self._createCopyrightMsg(self.copyrightTextOwner, self.copyrightTextMsg,
                                                        self.copyrightTextTag, createYear, lastModYear)

            # Determine if eol text exists and should be added
            if addStartEnd:
                newCopyRightMsg = self._addEolText(newCopyRightMsg)

        else:
            newCopyRightMsg = None

        return newCopyRightMsg


class CopyrightParseOrder2(CopyrightParse):
    """!
    @brief Copyright order parsing and new message class

    Add order setup to the copyright parsing and generation functions
    Expected order2 = CopyrightOwner CopyrightMsg CopyrightTag CopyrightYears
    """
    def _findOwnerStart(self, copyrightString:str, copyrightStart:int):
        """!
        @brief Find the start of the owner text between the start of line
               and Copyright message start
        @param copyrightString (string) Possible copyright string to parse
        @param copyrightStart (int) Starting string position of the "Copyright" text
        @return int - Starting position from the start of the string where the owner
                          text might start
        """
        ownerStart = re.search(r'[a-zA-Z0-9]', copyrightString[:copyrightStart])
        if ownerStart is not None:
            ownerStrStart = ownerStart.start()
        else:
            ownerStrStart = 0
        return ownerStrStart

    def isCopyrightLine(self, copyrightString:str)->bool:
        """!
        @brief Check if the input text is a copyright message with
               all the required components and in the correct order
        @param copyrightString (string) Line of text to check
        @return boolean - True if contents match regex criteria and order is correct, else False
        """
        match = False   # assume failure

        # Get base components
        msgMarker, tagMarker, yearList = self._parseCopyrightComponents(copyrightString)

        # Get owner data
        if msgMarker is not None:
            ownerStrStart = self._findOwnerStart(copyrightString, msgMarker.start())
            ownerData = self._parseOwnerString(copyrightString[ownerStrStart:msgMarker.start()], ownerStrStart)
        else:
            ownerData = None

        # Check components
        if self._checkComponents(msgMarker, tagMarker, yearList, ownerData):
            # Check if the fields are in the correct order
            if ((ownerData.start < msgMarker.start()) and
                (msgMarker.end() < tagMarker.start()) and
                (tagMarker.end() < yearList.getStartingStringIndex())):
                # Correct order
                match = True

        return match

    def parseCopyrightMsg(self, copyrightString:str):
        """!
        @brief Parse the input copyright string into it's components

        @param copyrightString - Current copyright message
        """
        # Get base components
        msgMarker, tagMarker, yearList = self._parseCopyrightComponents(copyrightString)

        # Get owner data
        if msgMarker is not None:
            ownerStrStart = self._findOwnerStart(copyrightString, msgMarker.start())
            ownerData = self._parseOwnerString(copyrightString[ownerStrStart:msgMarker.start()], ownerStrStart)
            solText = copyrightString[:ownerStrStart]
        else:
            solText = ""
            ownerData = None

        # Get end of line data
        endOfDates = yearList.getEndingStringIndex()
        eolData = self._parseEolString(copyrightString[endOfDates:], endOfDates)

        # Assign data values
        self._setParsedCopyrightData(copyrightString, msgMarker, tagMarker, yearList, ownerData, solText, eolData)

    def _createCopyrightMsg(self, owner:str, copyrightMsgText:str, copyrightTagText:str,
                            createYear:int, lastModYear:int|None = None)->str:
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Copyright owner text
        @param copyrightMsgText (string): Copyright message text
        @param copyrightTagText (string): Copyright tag text
        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date

        @return string : New copyright message
        """
        yearString = self._buildCopyrightYearString(createYear, lastModYear)
        newCopyRightMsg = owner+" "
        newCopyRightMsg += copyrightMsgText+" "
        newCopyRightMsg += copyrightTagText+" "
        newCopyRightMsg += yearString

        return newCopyRightMsg

    def buildNewCopyrightMsg(self, createYear:int, lastModYear:int|None = None, addStartEnd:bool = False)->str:
        """!
        @brief Generate a new copyright message for the input years

        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date or None
        @param addStartEnd (bool): True (default), add the start and eol text to the message
                                   False, ignore the start and eol text

        @return string : New copyright message or None if no copyright message was parsed
        """
        if self.copyrightTextValid:
            # Determine if start of line text should be added
            if addStartEnd:
                newCopyRightMsg = self.copyrightTextStart
            else:
                newCopyRightMsg = ""

            # Output text in order
            newCopyRightMsg += self._createCopyrightMsg(self.copyrightTextOwner, self.copyrightTextMsg,
                                                        self.copyrightTextTag, createYear, lastModYear)

            # Determine if eol text exists and should be added
            if addStartEnd:
                newCopyRightMsg = self._addEolText(newCopyRightMsg)

        else:
            newCopyRightMsg = None

        return newCopyRightMsg


class CopyrightParseEnglish(CopyrightParseOrder1):
    """!
    @brief English copyright parsing and new message class

    Utility class used to parse the existing copyright message into it's
    component parts and generate a new copyright message if the copyright
    years change.
    """

    ## Default copyright message text
    defaultCopyrightMsgText = "Copyright"
    ## Default copyright tag text
    defaultCopyrightTagText = "(c)"

    def __init__(self,
                 copyrightSearchMsg = r'Copyright|COPYRIGHT|copyright',
                 copyrightSearchTag = r'\([cC]\)',
                 copyrightSearchDate = r'(\d{4})',
                 copyrightOwnerSpec = r'[a-zA-Z0-9,\./\- @]',
                 useUnicode = False):
        """!
        @brief Constructor

        @param copyrightSearchMsg (string): Regular expresssion string used to identify
                                            the copyright word from the input
                                            copyright message string
        @param copyrightSearchTag (string): Regular expresssion string used to identify
                                            the copyright tag marker from the input
                                            copyright message string
        @param copyrightSearchDate (string): Regular expresssion string used to parse the
                                             date vaule(s) from the input copyright
                                             message string
        @param copyrightOwnerSpec (string): Regular expresssion containing the allowed owner
                                            characters
        @param useUnicode (bool): Set to true if unicode matching is required.
                                  Default is ASCII only processing
        """
        super().__init__(copyrightSearchMsg, copyrightSearchTag, copyrightSearchDate,
                         copyrightOwnerSpec, useUnicode)

    def createCopyrightMsg(self, owner:str, createYear:int, lastModYear:int|None = None):
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Owner string to use
        @param createYear (integer): File creation date
        @param lastModYear (integer): File last modification date

        @return string : New copyright message
        """
        return self._createCopyrightMsg(owner, CopyrightParseEnglish.defaultCopyrightMsgText,
                                        CopyrightParseEnglish.defaultCopyrightTagText,
                                        createYear, lastModYear)

class CopyrightGenerator(object):
    """!
    @brief Copyright message generator

    This class is used to generate new copyright message values based
    on a previously parsed copyright message and new dates or completely
    new copyright messages if a previously parsed message is unavailable.
    """
    def __init__(self, parser = None):
        """!
        @brief Constructor
        """
        ## Copyright parser object for parsed data, default copyright text and order specification
        self.parser = parser
        if parser is None:
            self.parser = CopyrightParseEnglish()

    @staticmethod
    def _isMultiYear(createYear:int, lastModYear:int|None)->bool:
        """!
        Determine if this is a multi or single year message

        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file or None

        @return bool - True if lastModYear is not None and lastModYear != createYear
        """
        if lastModYear is not None:
            if lastModYear != createYear:
                return True
            else:
                return False
        else:
            return False

    def _getNewCopyrightMsg(self, createYear:int, lastModYear:int|None = None)->tuple:
        """
        @brief Determine if a new copyright message is required and return if message changed
               and the new copyright message

        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        copyrightyearList = self.parser.getCopyrightDates()

        # Convert match text to year integers
        currentStartYear = int(copyrightyearList[0])

        # Don't move copyright forward
        if currentStartYear < createYear:
            startYear = currentStartYear
        else:
            startYear = createYear

        # Test if input is multiyear or current is multiyear
        if ((CopyrightGenerator._isMultiYear(createYear, lastModYear)) or
            (len(copyrightyearList) > 1)):

            # Convert match text to year integers
            currentLastModYear = int(copyrightyearList[-1])
            if lastModYear is None:
                if createYear > currentLastModYear:
                    lastModYear = createYear
                else:
                    lastModYear = currentLastModYear

            # Check for change
            if ((currentStartYear == startYear) and
                (currentLastModYear == lastModYear)):
                # No need to change return the old line
                newCopyRightMsg = self.parser.getCopyrightText()
                msgChanged = False
            else:
                # Generate the new message
                newCopyRightMsg = self.parser.buildNewCopyrightMsg(startYear, lastModYear, True)
                msgChanged = True
        else:
            if ((len(copyrightyearList) == 1) and
                (startYear == currentStartYear)):
                # No need to change return the old line
                newCopyRightMsg = self.parser.getCopyrightText()
                msgChanged = False
            else:
                # Update with a new line
                newCopyRightMsg = self.parser.buildNewCopyrightMsg(startYear, lastModYear, True)
                msgChanged = True

        return msgChanged, newCopyRightMsg

    def _getDefaultCopyrightMsg(self, createYear:int, lastModYear:int|None = None)->tuple:
        """!
        @brief Generate a new multiyear copyright message using default values

        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        newCopyRightMsg =  self.parser.createCopyrightMsg("None", createYear, lastModYear)
        return True, newCopyRightMsg

    def getNewCopyrightMsg(self, createYear:int, lastModYear:int|None = None)->tuple:
        """!
        @brief Determine if a new copyright message is required and return if message changed
               and the new copyright message

        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file or None

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        """
        if self.parser.isCopyrightTextValid():
            return self._getNewCopyrightMsg(createYear, lastModYear)
        else:
            return self._getDefaultCopyrightMsg(createYear, lastModYear)

    def createCopyrightTransition(self, createYear:int, transitionYear:int, lastModYear:int, newOwner:str)->tuple:
        """!
        @brief Modify the old copyright message to end with the transition year input and
               create a new copyright message with the transition year and new owner

        @param createYear (integer): File creation date
        @param transitionYear (integer): Last year of first message, first year of new message
        @param lastModYear (integer): Last modification date of the file
        @param newOwner (string): Owner for the new message

        @return bool: True is the copyright dates changed, else false
        @return string : New or old copyright message
        @return string : New owner copyright message
        """
        msgChanged, originalCopyright = self.getNewCopyrightMsg(createYear, transitionYear)
        self.parser.replaceOwner(newOwner)
        newCopyRightMsg = self.parser.buildNewCopyrightMsg(transitionYear, lastModYear, True)
        return msgChanged, originalCopyright, newCopyRightMsg

    def addCopyrightOwner(self, createYear:int, lastModYear:int, newOwner:str)->tuple:
        """!
        @brief Modify the old copyright message to end with the transition year input and
               create a new copyright message with the transition year and new owner

        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file
        @param newOwner (string): Owner for the new message

        @return bool: True is the copyright dates changed, else false
        @return string : New owner copyright message
        """
        if self.parser.addOwner(newOwner):
            newCopyRightMsg = self.parser.buildNewCopyrightMsg(createYear, lastModYear, True)
            return True, newCopyRightMsg
        else:
            return False, None

    def createNewCopyright(self, owner:str, createYear:int, lastModYear:int|None = None)->str:
        """!
        @brief Create a new copyright message from scratch

        @param owner (string): Owner for the new message
        @param createYear (integer): File creation date
        @param lastModYear (integer): Last modification date of the file

        @return string : New owner copyright message
        """
        return self.parser.createCopyrightMsg(owner, createYear, lastModYear)


class CopyrightFinder(object):
    """!
    Copyright message finder class
    """
    def __init__(self, parser = None):
        """!
        @brief Constructor

        @param parser (CopyrightParse object) - Copyright parser object to use
                                                or None to use a default parser
        """
        ## Copyright parser object for regex search criteria, default copyright text and order specification
        self._parser = parser
        if parser is None:
            self._parser = CopyrightParseEnglish()

    def findNextCopyrightMsg(self, inputFile, startOffset:int, endOffset:int|None = None)->tuple:
        """!
        @brief Scan the current file from the startOffset location to find the next copyright messag

        @param inputFile (file object): File object, open for reading
        @param startOffset (file offset): File offset to begin the scan at.
        @param endOffset (file offset): File offset to end the scan at or None to continue to end of file

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright message location data dictionary {'lineOffset': file offset of the copy right line,
                                                                        'text': Copyright text line from the file}
        """

        copyrightFound = False
        locationDict = None
        inputFile.seek(startOffset)

        while not copyrightFound:
            # Read the test line
            currentLineOffset = inputFile.tell()
            currentLine = inputFile.readline()

            # Check for end of file
            if not currentLine:
                break

            # check for search end
            if endOffset is not None:
                if currentLineOffset >= endOffset:
                    break

            # Check for match
            if self._parser.isCopyrightLine(currentLine):
                locationDict = {'lineOffset': currentLineOffset, 'text': currentLine}
                copyrightFound = True

        return copyrightFound, locationDict

    def findCopyrightMsg(self, inputFile)->tuple:
        """!
        @brief Scan the current file from the current location to find a copyright messge

        @param inputFile (file object): File object, open for reading

        @return bool: True if copyright block is found, else false
        @return dictionary: Copyright message location data dictionary {'lineOffset': file offset of the copy right line,
                                                                        'text': Copyright text line from the file}
        """
        return self.findNextCopyrightMsg(inputFile, 0, None)

    def findAllCopyrightMsg(self, inputFile)->tuple:
        """!
        @brief Scan the current file from the current location to find a copyright comment block
        @return bool: True if copyright block is found, else false
        @return list of dictionary: Copyright message location data dictionary
                                    {'lineOffset': file offset of the copy right line,
                                     'text': Copyright text line from the file}
        """
        copyrightDictList = []
        startLocation = 0
        while True:
            copyrightFound, locationDict = self.findNextCopyrightMsg(inputFile, startLocation, None)
            if copyrightFound:
                copyrightDictList.append(locationDict)
                startLocation = locationDict['lineOffset'] + len(locationDict['text'])
            else:
                break

        if not copyrightDictList:
            return False, None
        else:
            return True, copyrightDictList
