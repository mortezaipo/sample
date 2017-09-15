#!/usr/bin/env python3
"""
                      .SampleCmd.
SampleCmd is a CLI application which prepares sample commands
for users based on search words.

Copyright (C) 2016  Morteza Nourelahi Alamdari (Mortezaipo)

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
import sys
import argparse
import json
from glob import glob
from configparser import ConfigParser
import random

from colorclass import Color
from lxml import html
import requests

term_colors = {
    "error": "{{autored}}{}{{/autored}}",
    "success": "{{autogreen}}{}{{/autogreen}}",
    "info": "{{autocyan}}{}{{/autocyan}}",
    "warning": "{{autoyellow}}{}{{/autoyellow}}",
}


class Out:
    """Print result on terminal"""

    @staticmethod
    def show(msg: str):
        """Print normal message with default terminal color

        :param str msg: message text
        """
        print(msg)

    @staticmethod
    def error(msg: str):
        """Print error message with red color

        :param str msg: message list
        """
        print(Color(term_colors["error"].format(msg)))

    @staticmethod
    def success(msg: str):
        """Print success message with green color

        :param str msg: message list
        """
        print(Color(term_colors["success"].format(msg)))

    @staticmethod
    def warning(msg: str):
        """Print warning message with yellow color

        :param str msg: message list
        """
        print(Color(term_colors["warning"].format(msg)))

    @staticmethod
    def info(msg: str):
        """Print info message with blue color

        :param str msg: message list
        """
        print(Color(term_colors["info"].format(msg)))


def parse_html_content(content, title, command, description, limit=5):
    """Parse content based on html format

    :param str content: content body
    :param str title: title pattern
    :param str command: command pattern
    :param str description: description pattern
    :param int limit: limiting the result of parsing
    """
    result = []
    tree = html.fromstring(content)
    try:
        all_titles = tree.xpath(title)
    except:
        all_titles = None

    try:
        all_commands = tree.xpath(command)
    except:
        all_commands = None

    try:
        all_descriptions = tree.xpath(description)
    except:
        all_descriptions = None

    for i in range(limit):
        tmp_title = all_titles[i].text if all_titles else ""
        tmp_command = all_commands[i].text if all_commands else ""
        tmp_description = all_descriptions[i].text if all_descriptions else ""
        result.append(
            (tmp_title, tmp_command, tmp_description),
        )

    return result


def parse_json_content(content, title_p, command_p, description_p, limit=5):
    """Parse content based on json format

    :param str content: content body
    :param str title: title pattern
    :param str command: command pattern
    :param str description: description pattern
    """
    result = []

    try:
        tree = json.loads(content)
    except:
        return None

    if len(tree) < limit:
        limit = len(content) - 1

    while limit >= 0:

        if title_p != "":
            title = tree[limit][title_p]
        else:
            title = ""

        if command_p != "":
            command = tree[limit][command_p]
        else:
            command = ""

        if description_p != "":
            description = tree[limit][description_p]
        else:
            description = ""

        result.append(
            (title, command, description)
        )
        limit -= 1

    return result


class SampleCmd:
    """SampleCmd main class"""

    _sites = []

    def query(self, args):
        """Try to find commands based on args

        :param list args: arguments
        """
        if '-d' in args:
            show_description = True
        else:
            show_description = False

        if '-m' in args:
            more_info = True
        else:
            more_info = False

        try:
            limit_index = args.index('-l')
            limit = limit_index + 1
        except ValueError:
            # -l not found in user arguments
            limit = 5

        keyword = args[-1]

        self.search_in_sites(keyword, limit-1, show_description, more_info)

    def search_in_sites(self, keyword, limit, show_description, more_info):
        """Import all sites from sites directory"""
        cf = ConfigParser()
        for site_file in glob("sites/*.ini"):
            cf.read(site_file)

            if cf["GENERAL"]["enable"] != "yes":
                continue

            title_p = cf["CONTENT PATTERN"]["title"]
            command_p = cf["CONTENT PATTERN"]["command"]
            description_p = cf["CONTENT PATTERN"]["description"]

            search_url = cf["SITE INFO"]["site_search_url"].format(keyword)

            try:
                raw_data = requests.get(search_url)
            except:
                # Request failed
                continue

            if raw_data.status_code != 200:
                # Something failed
                continue

            if cf["CONTENT INFO"]["site_content_type"] == "html":
                parsed_data = parse_html_content(raw_data.content, title_p, command_p, description_p, limit)
            elif cf["CONTENT INFO"]["site_content_type"] == "json":
                parsed_data = parse_json_content(raw_data.content, title_p, command_p, description_p, limit)

            if not parsed_data:
                # There is no data
                continue

            random.shuffle(parsed_data)

            for res in parsed_data:
                Out.show("  {}".format(res[0]))
                Out.success("  $ {}".format(res[1]))
                if show_description and res[2] != "":
                    Out.info("  {}".format(res[2]))
                if more_info:
                    Out.warning("  {}".format(cf["SITE INFO"]["site_name"]))
                    Out.warning("  {}".format(cf["SITE INFO"]["site_url"]))
                print()


def main(args: list):
    """Main start point

    :param list args: command line arguments
    """
    SampleCmd().query(args)


# Main
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Sample Command Finder")
    ap.add_argument('string',
                    metavar="C",
                    type=str,
                    help="Command name")
    ap.add_argument('-d',
                    action="store_true",
                    help="Show commands description")
    ap.add_argument('-m',
                    action="store_true",
                    help="Show commands description")
    ap.add_argument('-l',
                    default="5",
                    type=int,
                    help="Limit the result (default is 5)")
    args = ap.parse_args()
    main(sys.argv[1:])
