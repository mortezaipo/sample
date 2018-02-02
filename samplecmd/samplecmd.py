#!/usr/bin/env python3
"""
                      .SampleCMD.

SampleCMD is a CLI application which prepares sample commands
for users based on search words.

Copyright (C) 2016  Morteza Nourelahi Alamdari (me@mortezana.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import argparse
import random
import json
from glob import glob
from json.decoder import JSONDecodeError
from configparser import ConfigParser, MissingSectionHeaderError, ParsingError

import requests
from lxml.etree import ParserError
from lxml import html
from colorclass import Color


TERM_COLORS = {
    "red": "{{autored}}{}{{/autored}}",
    "green": "{{autogreen}}{}{{/autogreen}}",
    "yellow": "{{autoyellow}}{}{{/autoyellow}}",
    "blue": "{{autoblue}}{}{{/autoblue}}",
    "cyan": "{{autocyan}}{}{{/autocyan}}",
}


class Out:
    """Print result on console."""

    @staticmethod
    def show(msg: str, end="\n") -> None:
        """Print normal message with default console color.

        :param str msg: message text
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(msg, end=end)

    @staticmethod
    def red(msg: str, end="\n") -> None:
        """Print error message with red color.

        :param str msg: message list
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(Color(TERM_COLORS["red"].format(msg)), end=end)

    @staticmethod
    def green(msg: str, end="\n") -> None:
        """Print success message with green color.

        :param str msg: message list
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(Color(TERM_COLORS["green"].format(msg)), end=end)

    @staticmethod
    def yellow(msg: str, end="\n") -> None:
        """Print warning message with yellow color.

        :param str msg: message list
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(Color(TERM_COLORS["yellow"].format(msg)), end=end)

    @staticmethod
    def blue(msg: str, end="\n") -> None:
        """Print info message with blue color.

        :param str msg: message list
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(Color(TERM_COLORS["blue"].format(msg)), end=end)

    @staticmethod
    def cyan(msg: str, end="\n") -> None:
        """Print info message with blue color.

        :param str msg: message list
        :param str end: end of print line

        :return: None
        :rtype: None
        """
        print(Color(TERM_COLORS["cyan"].format(msg)), end=end)


class HTMLParser:
    """Parse html content."""

    def __init__(self):
        """Initialize HTMLParser class."""
        self._tree = None

    def parse_content(self, content: str) -> bool:
        """Parse html content.

        :param str content: web content

        :return: parsing status
        :rtype: bool
        """
        try:
            self._tree = html.fromstring(content)
        except ParserError:
            return False
        return True

    def find(self, parent: str, title: str,
             command: str, description: str) -> list:
        """Find commands with details in the parsed html content.

        :param str parent: parent tags identifier of commands (xpath query)
        :param str title: command title tag identifier (xpath query)
        :param str command: command tag identifier (xpath query)
        :param str description: command description identifier (xpath query)

        :return: list of commands with details
        :rtype: list
        """
        result = []
        parents = self._tree.xpath(parent)
        if not parents:
            return result

        for section in parents:
            section_title = section.xpath(title) if title else ""
            section_command = section.xpath(command) if command else ""
            section_description = \
                section.xpath(description) if description else ""

            if section_title and section_command:
                if section_description:
                    section_description = [d.text for d in section_description]
                    result.append(
                        (section_title[0].text,
                         section_command[0].text,
                         "\n   ".join(map(str, section_description))))
                else:
                    result.append((section_title[0].text,
                                   section_command[0].text, ""))
        return result


class JSONParser:
    """Parse json content."""

    def __init__(self):
        """Initialize JSONParser class."""
        self._json = None

    def parse_content(self, content: str) -> bool:
        """Parse json content.

        :param str content: web content

        :return: parsing status
        :rtype: bool
        """
        try:
            self._json = json.loads(content)
        except JSONDecodeError:
            return False
        return True

    def find(self, parent: str, title: str,
             command: str, description: str) -> list:
        """Find commands with details in the parsed json content.

        :param str parent: parent tag identifier of commands (json key name)
        :param str title: command title tag identifier (json key name)
        :param str command: command tag identifier (json key name)
        :param str description: command description identifier (json key name)

        :return: list of commands with details
        :rtype: list
        """
        if parent:
            parents = parent.split("/")
            for p in parents:
                if p:
                    self._json = self._json[p]

        result = []
        for section in self._json:
            section_title = section[title] if title else ""
            section_command = section[command] if command else ""
            section_description = \
                section.xpath(description) if description else ""

            if section_title and section_command:
                result.append((section_title,
                               section_command,
                               section_description))
        return result


class Command:
    """Command info object."""

    def __init__(self, site_name: str, site_url: str,
                 command_title: str, command: str, command_description: str):
        """Initialize Command class.

        :param str site_name: site name
        :param str site_url: site base url
        :param str command_title: command title
        :param str command: executable command
        :param str command_description: command description
        """
        self.site_name = site_name
        self.site_url = site_url
        self.command_title = command_title
        self.command = command
        self.command_description = command_description

    def __lt__(self, other_cmd) -> bool:
        """Less Than for sort functions.

        :param Command other_cmd: other Command object

        :return: comparison result
        :rtype: bool
        """
        if self.site_name < other_cmd.site_name:
            return True
        return False


class SampleCMD:
    """SampleCmd main class."""

    _sites = []

    def __init__(self):
        """Initialize SampleCMD class."""
        self._config = ConfigParser()

        # standard sites
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        standard_sites = os.path.join(file_path, "sites")
        self._sites.extend(glob(os.path.join(standard_sites, "*.ini")))

        # user's sites
        user_sites = os.path.join(os.path.expanduser("~"), ".samplecmd/sites")
        if os.path.exists(user_sites):
            self._sites.extend(glob(os.path.join(user_sites, "*.ini")))

    def fetch_and_print(self, keyword: str, show_description: bool,
                        show_source_links: bool,
                        limit_result: int = 5) -> None:
        """Try to find commands based on user's args.

        :param str keyword: search keyword
        :param bool show_description: show command description
        :param bool show_source_links: show commands source links
        :param int limit_result: limit results

        :return: prepared commands
        :rtype: str
        """
        result = self._search_in_sites(keyword, limit_result-1)
        if not result:
            Out.show("Not result found.")

        sorted(result)
        for index, cmd_obj in enumerate(result):
            Out.show("{}: ".format(index+1), "")
            Out.show(cmd_obj.command_title)
            Out.green("   {}".format(cmd_obj.command))
            if show_description and cmd_obj.command_description:
                Out.blue("   {}".format(cmd_obj.command_description))
            if show_source_links:
                Out.cyan("   {} <{}>".format(cmd_obj.site_name,
                                             cmd_obj.site_url))

    def _validate_config(self, config_obj: ConfigParser) -> bool:
        """Validate config file sections and variables.

        .. raises:: KeyError on any inconsistency

        :param ConfigParser config_obj: config parser object

        :return: validate config file
        :rtype: bool
        """
        validate_structure = {"GENERAL": ["enable"],
                              "SITE INFO": ["site_name",
                                            "site_url",
                                            "site_search_url"],
                              "CONTENT INFO": ["site_content_type",
                                               "site_content_action"],
                              "CONTENT PATTERN": ["parent",
                                                  "title",
                                                  "command",
                                                  "description"]}

        if sorted(validate_structure.keys()) != sorted(config_obj.sections()):
            raise KeyError()

        for section, keys in validate_structure.items():
            for key in keys:
                if not config_obj.has_option(section, key):
                    raise KeyError()
        return True

    def _search_in_sites(self, keyword: str, limit_result: int) -> list:
        """Search in all sites from sites list.

        :param str keyword: search keyword
        :param int limit_result: limit the result

        :return: list of prepared result
        :rtype: list
        """
        result = []
        for site in self._sites:
            try:
                self._config.read(site)
                self._validate_config(self._config)
            except MissingSectionHeaderError as e:
                Out.red("Invalid config file({}) structure: {}.".
                        format(site, e))
                continue
            except ParsingError as e:
                Out.red("Parsing config file({}) failed: {}.".format(site, e))
                continue
            except KeyError:
                Out.red("Inconsistency in config file({}) keys or sections.".
                        format(site))

            if not self._config.getboolean("GENERAL", "enable"):
                continue

            # site patterns
            parent_p = self._config["CONTENT PATTERN"]["parent"]
            title_p = self._config["CONTENT PATTERN"]["title"]
            command_p = self._config["CONTENT PATTERN"]["command"]
            description_p = self._config["CONTENT PATTERN"]["description"]

            site_name = self._config["SITE INFO"]["site_name"]
            site_url = self._config["SITE INFO"]["site_url"]
            search_url = self._config["SITE INFO"]["site_search_url"]

            # prepare http request headers
            headers = {}
            if self._config["CONTENT INFO"]["site_content_type"] == "json":
                headers.update({"content-type": "application/json"})
            elif self._config["CONTENT INFO"]["site_content_type"] == "html":
                headers.update({"content-type": "text/html"})

            try:
                action_type = \
                    self._config["CONTENT INFO"]["site_content_action"]
                if action_type == "get":
                    request = requests.get(search_url.format(keyword),
                                           headers=headers)
                elif action_type == "post":
                    request = requests.post(search_url.format(keyword),
                                            headers=headers)
                else:
                    Out.red("invalid request type: ({}) {}".
                            format(site, action_type))
                    continue
            except requests.exceptions.MissingSchema as e:
                Out.red("invalid search url: ({}) {}".format(site, e))
                continue
            except requests.exceptions.ConnectionError as e:
                Out.red("connection error: ({}) {}".format(site, e))
            except requests.exceptions.HTTPError as e:
                Out.red("http error: ({}) {}".format(site, e))
            except requests.exceptions.InvalidURL as e:
                Out.red("invalid search url: ({}) {}".format(site, e))
                continue

            if request.status_code != 200:
                Out.yellow("site returns error code: ({}) {}".
                           format(site, request.status_code))
                continue

            site_content_type = \
                self._config["CONTENT INFO"]["site_content_type"]
            if site_content_type == "html":
                parser_obj = HTMLParser()
            elif site_content_type == "json":
                parser_obj = JSONParser()
            else:
                Out.red("invalid parse type: ({}) {}".
                        format(site, site_content_type))
                continue

            if not parser_obj.parse_content(request.content):
                Out.yellow("invalid site content: ({})".format(site))

            t_result = parser_obj.find(parent_p, title_p,
                                       command_p, description_p)
            if not t_result:
                continue

            random.shuffle(t_result)
            for info in t_result:
                result.append(Command(site_name, site_url,
                                      info[0], info[1], info[2]))

        # prepare result
        random.shuffle(result)
        if len(result) <= limit_result:
            return result
        return random.sample(result, limit_result)


def main() -> None:
    """Main start function.

    :return: None
    :rtype: None
    """
    args = sys.argv[1:]
    ap = argparse.ArgumentParser(description="Sample Command Finder")
    ap.add_argument('string',
                    metavar="C",
                    type=str,
                    help="Command name")
    ap.add_argument('-d',
                    action="store_true",
                    help="Show commands description")
    # ap.add_argument('-m',
    #                 action="store_true",
    #                 help="Show more info about commands")
    ap.add_argument('-r',
                    action="store_true",
                    help="Show commands source links")
    ap.add_argument('--version',
                    action="store_true",
                    help="Show version")
    ap.add_argument('-l',
                    default="5",
                    type=int,
                    help="Limit the result (default is 5)")
    ap.parse_args()

    show_description = True if '-d' in args else False
    show_source_links = True if '-r' in args else False
    # more_info = True if '-m' in args else False

    try:
        limit_index = int(args.index('-l'))
        limit_result = int(args[limit_index + 1]) + 1
    except (ValueError, AttributeError):  # -l not found in user arguments
        limit_result = 6

    keyword = args[0]
    SampleCMD().fetch_and_print(keyword, show_description,
                                show_source_links, limit_result)
