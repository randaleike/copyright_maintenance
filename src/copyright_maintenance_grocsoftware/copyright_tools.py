"""@package copyright_maintenance
@brief Copyright message parser tools

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

class SubTextMarker():
    """!
    @brief Regex trimmed substrng text and location information
    """
    def __init__(self, new_text:str, original_start:int):
        """!
        * @brief Process the input string to remove leading and trailing white space
        *        and store the results
        *
        * @param new_text {string} - String data.
        * @param original_start {int} - starting index new_text within the base string
        """
        trimed_text = new_text.lstrip()

        ## Trimmed text value
        self.text = trimed_text.rstrip()
        ## Starting position from the start of the input string plus original_start value
        self.start = original_start + (len(new_text) - len(trimed_text))
        ## Ending position from the start of the input string plus original_start value
        self.end = self.start + len(self.text)

    def get_text(self)->str:
        """!
        @brief Get the trimmed text value
        @return string - Trimmed text value
        """
        return self.text

    def get_start(self)->int:
        """!
        @brief Get the starting text position in the original string
        @return int - Original string starting position
        """
        return self.start

    def get_end(self)->int:
        """!
        @brief Get the ending text position in the original string
        @return int - Original string ending position
        """
        return self.end

class CopyrightYearsList():
    """!
    Parse dates return data structure
    """
    def __init__(self, year_string:str, year_regex:str, base_index:int = 0):
        """!
        Default constructor

        @param year_string {string} - String to parse years from
        @param year_regex {RegExp} - Regex year matching criteria
        @param base_index {int} - Index of the year data substring within the original string
        """
        ## List of found years as strings
        self._years = []
        ## List of found years as integers
        self._intyears = []
        ## Start index of the first date text within the parsed input string
        self._start = -1
        ## End index of the last date text within the parsed input string
        self._end = -1

        for year_match in re.finditer(year_regex, year_string):
            # Get the found year
            self._years.append(year_match.group())
            self._intyears.append(self._parse_year_from_date_str(year_match.group()))

            if self._start == -1:
                self._start = year_match.start() + base_index
            self._end = max(year_match.end() + base_index, self._end)

    def _parse_year_from_date_str(self, year_str:str)->int:
        """!
        @brief Convert year text to year int
        @param year_str {string} - Date string to convert
        @returns int - Year as a numeric value
        """
        year_match = re.search(r'(\d{4})', year_str)
        if year_match is not None:
            int_year = int(year_match.group())
        else:
            int_year = 1970
        return int_year

    def is_valid(self)->bool:
        """!
        @brief - Determine if anything was added to the list

        @returns - True if list is not empty, else false
        """
        return bool(self._intyears)

    def get_numeric_year_list(self)->list:
        """!
        @brief Pull the numeric year data from the years list

        @returns int[] - Numeric List of years
        """
        return self._intyears

    def get_first_entry(self)->int:
        """!
        @brief Get the first year entry

        @returns Entry 0 or None if the list is empty
        """
        if len(self._intyears) > 0:
            return_data = self._intyears[0]
        else:
            return_data = None
        return return_data

    def get_last_entry(self)->int:
        """!
        @brief Get the last year entry

        @returns Last year entry or None if the list is empty
        """
        if len(self._intyears) > 0:
            return_data = self._intyears[-1]
        else:
            return_data = None
        return return_data

    def get_starting_string_index(self)->int:
        """!
        @brief Return the starting index of first year in the year list.
               Returns -1 if the list is empty.

        @returns int - Starting index of the first entry or -1 if list is empty
        """
        return self._start

    def get_ending_string_index(self)->int:
        """!
        @brief Return the ending index of last year in the year list.
               Returns -1 if the list is empty.

        @returns int - Starting index of the first entry or -1 if list is empty
        """
        return self._end

class CopyrightParse():
    """!
    @brief Copyright parsing and new message class

    Utility class used to parse the existing copyright message into it's
    component parts and generate a new copyright message if the copyright
    years change.
    """
    def __init__(self, copyright_search_msg:str, copyright_search_tag:str,
                 copyright_search_date:str, copyright_owner_spec:str,
                 use_unicode:bool = False):
        """!
        @brief Constructor

        @param copyright_search_msg (string): Regular expresssion string used to identify
                                            the copyright word from the input
                                            copyright message string
        @param copyright_search_tag (string): Regular expresssion string used to identify
                                            the copyright tag marker from the input
                                            copyright message string
        @param copyright_search_date (string): Regular expresssion string used to parse the
                                             date vaule(s) from the input copyright
                                             message string
        @param copyright_owner_spec (string): Regular expresssion containing the allowed owner
                                            characters
        @param use_unicode (bool) - Set to true if unicode matching is required.
                                   Default is ASCII only processing
        """

        ## Actual text of the copyright message line
        self.copyright_text = ""

        if not use_unicode:
            regx_flags = re.ASCII
        else:
            regx_flags = re.UNICODE

        ## Regex expression for the copyright part of the copyright string
        self.copyright_regx_msg = re.compile(copyright_search_msg, regx_flags)
        ## Regex expression for the copyright tag of the copyright string
        self.copyright_regx_tag = re.compile(copyright_search_tag, regx_flags)
        ## Regex expression for the copyright year(s) of the copyright string
        self.copyright_regx_year = re.compile(copyright_search_date, regx_flags)
        ## Regex expression for the copyright owner text of the copyright string
        self.copyright_regx_owner = re.compile(copyright_owner_spec, regx_flags)

        ## Copyright message valid flag. False until a valid copyright message is found
        self.copyright_text_valid = False
        ## Any text preceeding the valid copyright string
        self.copyright_text_start = ""
        ## Any non-white text following the valid copyright string
        self.copyright_text_eol = None

        ## Text from the input copyright string that matched the self.copyright_regx_msg criteria
        self.copyright_text_msg = None
        ## Text from the input copyright string that matched the self.copyright_regx_tag criteria
        self.copyright_text_tag = None
        ## Text from the input copyright string that matched the self.copyright_regx_owner criteria
        self.copyright_text_owner = None

        ## List of years from the input copyright string that matched the self.copyright_regx_year
        ## criteria
        self.copyright_year_list = []

    def is_copyright_text_valid(self)->bool:
        """!
        @brief Determine if a previous parse was run and valid

        @return Bool - True, Copyright line was parsed and was valid
        """
        return self.copyright_text_valid

    def get_copyright_text(self)->str:
        """!
        @brief Get the last valid parsed copyright text

        @return string - Last parsed copyright text original string
        """
        return self.copyright_text

    def get_copyright_dates(self)->list:
        """!
        @brief Get the last valid parsed copyright date list

        @return int list - List of parsed copyright years
        """
        return self.copyright_year_list

    def add_owner(self, new_owner:str)->bool:
        """!
        @brief Add an owner to the ownership string

        @param new_owner (string): New owner name

        @return bool - True if successfully added, else False
        """
        return_status = False
        if self.copyright_text_valid:
            self.copyright_text_owner += ", "
            self.copyright_text_owner += new_owner
            return_status = True

        return return_status

    def replace_owner(self, new_owner:str)->bool:
        """!
        @brief Replace the ownership string with a new ownership string

        @param new_owner (string): New owner name

        @return bool - True if successfully added, else False
        """
        self.copyright_text_owner = new_owner
        return True

    def _parse_eol_string(self, test_string:str, base_index:int = 0)->SubTextMarker:
        """!
        @brief Parse the EOL text string out of the message substring.

        The owner string is defined as any regex match in the
        copyrightEolTag constructor input parameter.

        @param test_string (string): Sub-string to parse
        @param base_index (integer): Starting index value of the input sub-string
                                    to parse within the full copyright string.
                                    Used to properly set 'start' values within
                                    the full string.  Default = 0.

        @return SubTextMarker object containing EOL text data or
                None if there is no EOL text.
        """
        # Determine if an EOL marker exists
        eol_marker = test_string
        eol_marker = eol_marker.strip()

        # ignore all spaces pad.
        if eol_marker == '':
            eol_data = None
        else:
            eol_start_index = base_index + re.search(r'[^ ]', test_string).start()
            eol_data = SubTextMarker(eol_marker, eol_start_index)

        return eol_data

    def _parse_owner_string(self, test_string:str, base_index:int = 0)->SubTextMarker:
        """!
        @brief Parse the owner string out of the message substring.

        The owner string is defined as any regex match in the
        copyrightEolTag constructor input parameter.

        @param test_string (string): Sub-string to parse
        @param base_index (integer): Starting index value of the input sub-string
                                    to parse within the full copyright string.
                                    Used to properly set 'start' values within
                                    the full string.  Default = 0.

        @return SubTextMarker object containing owner text data or
                None if there is no valid owner string
        """
        index = 0
        while index < len(test_string):
            if re.match(self.copyright_regx_owner, test_string[index]) is None:
                break
            index += 1

        # Found end of owner, find start of owner string
        owner = test_string[:index]
        owner = owner.strip()

        if owner == '':
            owner_data = None
        else:
            owner_start_index = base_index + re.search(r'[^ ]', test_string[:index]).start()
            owner_data = SubTextMarker(owner, owner_start_index)

        return owner_data

    def _parse_years(self, current_msg:str)->CopyrightYearsList:
        """!
        @brief Parse the dates from the input string

        @param current_msg (string): Current copyright message

        @return CopyrightYearsList object list of matching date values
        """
        return CopyrightYearsList(current_msg, self.copyright_regx_year, 0)

    def _parse_copyright_components(self, current_msg:str)->tuple:
        """!
        @brief Parse the copyright line into it's components

        @param current_msg (string): Current copyright message

        @return re.Match - Copyright match output or None if no match found
        @return re.Match - Copyright tag match output or None if no match found
        @return CopyrightYearsList object - List of copyright year matches
        """
        msg_marker = re.search(self.copyright_regx_msg, current_msg)
        tag_marker = re.search(self.copyright_regx_tag, current_msg)
        year_list  = self._parse_years(current_msg)

        return msg_marker, tag_marker, year_list

    def _check_components(self, msg_marker:re.Match, tag_marker:re.Match,
                         year_list:CopyrightYearsList, owner:SubTextMarker)->bool:
        """!
        @brief Determine if the current line matches the copyright search criteria

        @param msg_marker {re.Match} - Copyright match output or None if no match found
        @param tag_marker {re.Match} - Copyright tag match output or None if no match found
        @param year_list {CopyrightYearsList} - List of copyright year matches
        @param owner {SubTextMarker} - Owner SubTextMarker object

        @return bool - True if regx search criteria matched, else False
        """
        check_status = False

        # Check if all the components exist
        if ((msg_marker is not None) and
            (tag_marker is not None) and
            (year_list.is_valid()) and
            (owner is not None)):

            check_status = True
        return check_status

    def _set_parsed_copyright_data(self, current_msg:str, msg_marker:re.Match,
                                   tag_marker:re.Match, year_list:CopyrightYearsList,
                                   owner:SubTextMarker, sol_text:str,
                                   eol_marker:SubTextMarker):
        """!
        @brief Set the parsed copyright data elements

        @param current_msg {string} - Current message
        @param msg_marker {re.Match} - Copyright match output or None if no match found
        @param tag_marker {re.Match} - Copyright tag match output or None if no match found
        @param year_list {CopyrightYearsList} - List of copyright year matches
        @param owner {SubTextMarker} - Owner SubTextMarker object or None if owner text
                                       was not found
        @param sol_text {string} - Start of line (SOL) text
        @param eol_marker {SubTextMarker} - End of line (EOL) SubTextMarker object or
                                           None if no EOL text exists
        """
        self.copyright_text_valid = True

        if msg_marker is not None:
            self.copyright_text_start = sol_text
            self.copyright_text_msg = msg_marker.group()
        else:
            self.copyright_text_valid = False

        if tag_marker is not None:
            self.copyright_text_tag = tag_marker.group()
        else:
            self.copyright_text_valid = False

        if year_list.is_valid():
            self.copyright_year_list.clear()
            self.copyright_year_list.extend(year_list.get_numeric_year_list())
        else:
            self.copyright_text_valid = False

        if owner is not None:
            self.copyright_text_owner = owner.text
        else:
            self.copyright_text_valid = False

        if eol_marker is not None:
            self.copyright_text_eol = eol_marker.text

        if self.copyright_text_valid:
            self.copyright_text = current_msg

    def _add_eol_text(self, new_copyright_msg:str)->str:
        """!
        @brief Append the EOL text to the new copyright message

        @param new_copyright_msg (string) Current copyright message to append to

        @return string new_copyright_msg with self.copyright_text_eol appended
        """
        # Determine if eol text exists and should be added
        if self.copyright_text_eol is not None:
            eol_marker = self.copyright_text.rfind(self.copyright_text_eol)
            pad_length = eol_marker - len(new_copyright_msg)

            count = 0
            while count < pad_length:
                new_copyright_msg += " "
                count+=1

            new_copyright_msg += self.copyright_text_eol

        return new_copyright_msg

    def _build_copyright_year_string(self, create_year:int, last_modify_year:int = None)->str:
        """!
        @brief Build the proper copyright year string
        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date or None
        @return string : proper constructed year string
        """
        if last_modify_year is not None:
            if create_year == last_modify_year:
                year_string = str(create_year)
            else:
                year_string = str(create_year)+"-"+str(last_modify_year)
        else:
            year_string = str(create_year)

        return year_string

class CopyrightParseOrder1(CopyrightParse):
    """!
    @brief Copyright order parsing and new message class

    Add order setup to the copyright parsing and generation functions.
    Expected order1 = CopyrightMsg CopyrightTag CopyrightYears CopyrightOwner
    """

    def is_copyright_line(self, copyright_string:str)->bool:
        """!
        @brief Check if the input text is a copyright message with
               all the required components and in the correct order
        @param copyright_string (string) Line of text to check
        @return boolean - True if contents match regex criteria and order is correct, else False
        """
        match = False   # assume failure

        # Get base components
        msg_marker, tag_marker, year_list = self._parse_copyright_components(copyright_string)

        # Get owner data
        if year_list.is_valid():
            end_of_dates = year_list.get_ending_string_index()
            owner_data = self._parse_owner_string(copyright_string[end_of_dates:], end_of_dates)

            # Check components
            if self._check_components(msg_marker, tag_marker, year_list, owner_data):
                # Check if the fields are in the correct order
                if ((msg_marker.end() < tag_marker.start()) and
                    (tag_marker.end() < year_list.get_starting_string_index()) and
                    (end_of_dates < owner_data.start)):
                    # Correct order
                    match = True

        return match

    def parse_copyright_msg(self, copyright_string:str):
        """!
        @brief Parse the input copyright string into it's components

        @param copyright_string - Current copyright message
        """
        # Get base components
        msg_marker, tag_marker, year_list = self._parse_copyright_components(copyright_string)

        # Get owner data
        end_of_dates = year_list.get_ending_string_index()
        owner_data = self._parse_owner_string(copyright_string[end_of_dates:], end_of_dates)

        # Get end of line data
        end_of_owner = owner_data.start + len(owner_data.text)
        eol_data = self._parse_eol_string(copyright_string[end_of_owner:], end_of_owner)

        # Get start of line text data
        sol_text = copyright_string[:msg_marker.start()]

        # Assign data values
        self._set_parsed_copyright_data(copyright_string, msg_marker, tag_marker,
                                        year_list, owner_data, sol_text, eol_data)

    def _create_copyright_msg(self, owner:str, copyright_msg_text:str,
                              copyright_tag_text:str, create_year:int,
                              last_modify_year:int = None)->str:
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Copyright owner text
        @param copyright_msg_text (string): Copyright message text
        @param copyright_tag_text (string): Copyright tag text
        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date

        @return string : New copyright message
        """
        year_string = self._build_copyright_year_string(create_year, last_modify_year)
        new_copyright_msg = copyright_msg_text+" "
        new_copyright_msg += copyright_tag_text+" "
        new_copyright_msg += year_string+" "
        new_copyright_msg += owner

        return new_copyright_msg

    def build_new_copyright_msg(self, create_year:int, last_modify_year:int = None,
                                add_start_end:bool = False)->str:
        """!
        @brief Generate a new copyright message for the input years

        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date or None
        @param add_start_end (bool): True (default), add the start and eol text to the message
                                   False, ignore the start and eol text

        @return string : New copyright message or None if no copyright message was parsed
        """
        if self.copyright_text_valid:
            # Determine if start of line text should be added
            if add_start_end:
                new_copyright_msg = self.copyright_text_start
            else:
                new_copyright_msg = ""

            # Output text in order
            new_copyright_msg += self._create_copyright_msg(self.copyright_text_owner,
                                                            self.copyright_text_msg,
                                                            self.copyright_text_tag,
                                                            create_year,
                                                            last_modify_year)

            # Determine if eol text exists and should be added
            if add_start_end:
                new_copyright_msg = self._add_eol_text(new_copyright_msg)

        else:
            new_copyright_msg = None

        return new_copyright_msg

class CopyrightParseOrder2(CopyrightParse):
    """!
    @brief Copyright order parsing and new message class

    Add order setup to the copyright parsing and generation functions
    Expected order2 = CopyrightOwner CopyrightMsg CopyrightTag CopyrightYears
    """
    def _find_owner_start(self, copyright_string:str, copyright_start:int):
        """!
        @brief Find the start of the owner text between the start of line
               and Copyright message start
        @param copyright_string (string) Possible copyright string to parse
        @param copyright_start (int) Starting string position of the "Copyright" text
        @return int - Starting position from the start of the string where the owner
                          text might start
        """
        owner_start = re.search(r'[a-zA-Z0-9]', copyright_string[:copyright_start])
        if owner_start is not None:
            owner_str_start_index = owner_start.start()
        else:
            owner_str_start_index = 0
        return owner_str_start_index

    def is_copyright_line(self, copyright_string:str)->bool:
        """!
        @brief Check if the input text is a copyright message with
               all the required components and in the correct order
        @param copyright_string (string) Line of text to check
        @return boolean - True if contents match regex criteria and order is correct, else False
        """
        match = False   # assume failure

        # Get base components
        msg_marker, tag_marker, year_list = self._parse_copyright_components(copyright_string)

        # Get owner data
        if msg_marker is not None:
            owner_str_start_index = self._find_owner_start(copyright_string, msg_marker.start())
            owner_text = copyright_string[owner_str_start_index:msg_marker.start()]
            owner_data = self._parse_owner_string(owner_text, owner_str_start_index)
        else:
            owner_data = None

        # Check components
        if self._check_components(msg_marker, tag_marker, year_list, owner_data):
            # Check if the fields are in the correct order
            if ((owner_data.start < msg_marker.start()) and
                (msg_marker.end() < tag_marker.start()) and
                (tag_marker.end() < year_list.get_starting_string_index())):
                # Correct order
                match = True

        return match

    def parse_copyright_msg(self, copyright_string:str):
        """!
        @brief Parse the input copyright string into it's components

        @param copyright_string - Current copyright message
        """
        # Get base components
        msg_marker, tag_marker, year_list = self._parse_copyright_components(copyright_string)

        # Get owner data
        if msg_marker is not None:
            owner_str_start_index = self._find_owner_start(copyright_string, msg_marker.start())
            owner_text = copyright_string[owner_str_start_index:msg_marker.start()]
            owner_data = self._parse_owner_string(owner_text, owner_str_start_index)
            sol_text = copyright_string[:owner_str_start_index]
        else:
            sol_text = ""
            owner_data = None

        # Get end of line data
        end_of_dates = year_list.get_ending_string_index()
        eol_data = self._parse_eol_string(copyright_string[end_of_dates:], end_of_dates)

        # Assign data values
        self._set_parsed_copyright_data(copyright_string, msg_marker, tag_marker,
                                        year_list, owner_data, sol_text, eol_data)

    def _create_copyright_msg(self, owner:str,
                              copyright_msg_text:str,
                              copyright_tag_text:str,
                              create_year:int,
                              last_modify_year:int = None)->str:
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Copyright owner text
        @param copyright_msg_text (string): Copyright message text
        @param copyright_tag_text (string): Copyright tag text
        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date

        @return string : New copyright message
        """
        year_string = self._build_copyright_year_string(create_year, last_modify_year)
        new_copyright_msg = owner+" "
        new_copyright_msg += copyright_msg_text+" "
        new_copyright_msg += copyright_tag_text+" "
        new_copyright_msg += year_string

        return new_copyright_msg

    def build_new_copyright_msg(self, create_year:int, last_modify_year:int = None,
                                add_start_end:bool = False)->str:
        """!
        @brief Generate a new copyright message for the input years

        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date or None
        @param add_start_end (bool): True (default), add the start and eol text to the message
                                   False, ignore the start and eol text

        @return string : New copyright message or None if no copyright message was parsed
        """
        if self.copyright_text_valid:
            # Determine if start of line text should be added
            if add_start_end:
                new_copyright_msg = self.copyright_text_start
            else:
                new_copyright_msg = ""

            # Output text in order
            new_copyright_msg += self._create_copyright_msg(self.copyright_text_owner,
                                                            self.copyright_text_msg,
                                                            self.copyright_text_tag,
                                                            create_year,
                                                            last_modify_year)

            # Determine if eol text exists and should be added
            if add_start_end:
                new_copyright_msg = self._add_eol_text(new_copyright_msg)

        else:
            new_copyright_msg = None

        return new_copyright_msg


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
                 copyright_search_msg = r'Copyright|COPYRIGHT|copyright',
                 copyright_search_tag = r'\([cC]\)',
                 copyright_search_date = r'(\d{4})',
                 copyright_owner_spec = r'[a-zA-Z0-9,\./\- @]',
                 use_unicode = False):
        """!
        @brief Constructor

        @param copyright_search_msg (string): Regular expresssion string used to identify
                                            the copyright word from the input
                                            copyright message string
        @param copyright_search_tag (string): Regular expresssion string used to identify
                                            the copyright tag marker from the input
                                            copyright message string
        @param copyright_search_date (string): Regular expresssion string used to parse the
                                             date vaule(s) from the input copyright
                                             message string
        @param copyright_owner_spec (string): Regular expresssion containing the allowed owner
                                            characters
        @param use_unicode (bool): Set to true if unicode matching is required.
                                  Default is ASCII only processing
        """
        super().__init__(copyright_search_msg, copyright_search_tag, copyright_search_date,
                         copyright_owner_spec, use_unicode)

    def create_copyright_msg(self, owner:str, create_year:int, last_modify_year:int = None):
        """!
        @brief Generate a new multiple year copyright message for the input
               creation year with the parsed copyright message, tag and owner

        @param owner (string): Owner string to use
        @param create_year (integer): File creation date
        @param last_modify_year (integer): File last modification date

        @return string : New copyright message
        """
        return self._create_copyright_msg(owner,
                                          CopyrightParseEnglish.defaultCopyrightMsgText,
                                          CopyrightParseEnglish.defaultCopyrightTagText,
                                          create_year,
                                          last_modify_year)
