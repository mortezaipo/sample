"""Abstract site class."""
from abc import ABCMeta
import requests
from parser import parse_html_content, parse_json_content


class Site(metaclass=ABCMeta):
    """Abstract site class."""

    # These variables must be override by implemented classes.
    site_name = None
    site_url = None
    site_search_url = None
    enable = False

    # Site content type (html or json)
    site_content_type = "html"

    # These variables should be "xpath" or "json key" based on the site returned content
    title = None
    command = None
    description = None

    # Do not manipulate it
    _limit = 5

    def search(self, query: str, consider_description=False, limit=5):
        """Searching query in the site.

        :param str query: query string
        :param bool consider_description: show command explain
        :param int limit: limit the searching result
        """
        if not consider_description:
            self.description = None

        self._limit = limit
        search_url = self.site_search_url.format(query)
        return self.send_request(search_url)

    def send_request(self, url: str):
        """Send GET request to the site and fetch its content

        :param str url: url string
        """
        headers = {}
        if self.site_content_type == "json":
            headers.update({"content-type": "application/json"})
        elif self.site_content_type == "html":
            headers.update({"content-type": "text/html"})

        request = requests.get(url, headers=headers)  # FIXME: need more exceptions handler
        return self.parse(request.content)

    def parse(self, content):
        """Start to crawl and find results."""
        data = {}
        if self.site_content_type == "html":
            data.update({"records": parse_html_content(content, self.title, self.command, self.description, self._limit)})
        elif self.site_content_type == "json":
            data.update({"records": parse_json_content(content, self.title, self.command, self.description, self._limit)})

        data.update({"site_name": self.site_name})
