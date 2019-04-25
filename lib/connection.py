import random
import re
import requests
import logging
from requests.auth import HTTPBasicAuth


class HTTP:
    """Handles the http connection"""
    def __init__(self) -> None:
        """initialize the http connection object"""
        self.agents = [line.strip("\n") for line in open("lib/agents.ini").readlines()]
        self.logger = logging.getLogger("admin-finder")

    def get_headers(self) -> dict:
        """ Returns randomly chosen UserAgent """
        return {
            "User-Agent": random.choice(self.agents)
        }

    def connect(self, url: str, creds: [str, str]) -> dict:
        """
        connect to the url and return the response
        Args:
            url: the url to open
            creds: basic auth credentials
        RetVal:
            dict: the string response or empty string
        """
        if creds is not None:
            request = requests.get(url, headers=self.get_headers(), auth=HTTPBasicAuth(creds[0], creds[1]))
        else:
            request = requests.get(url, headers=self.get_headers())
        return {
            "code" : request.status_code,
            "response" : request.text
        }


class URLFormatter:
    """A url class to handle all the URL related operation"""
    def __init__(self, url: str) -> None:
        """initialize URL object"""
        self.url = url

    def geturl(self) -> str:
        """Get the formatted url"""
        if self.url.startswith("http://") or self.url.startswith("https://"):
            self.fullurl = self.url
        else:
            self.fullurl = "http://" + self.url
        if not self.fullurl.endswith("/"):
            self.fullurl += "/"
        return self.fullurl


class URLHandler(HTTP):
    """General URL handler"""
    def __init__(self) -> None:
        super().__init__()

    def scan(self, url: str, creds: [str, str]) -> int:
        """Scans the website by connecting, and return status code"""
        if creds is not None:
            return self.connect(url, creds)["code"]
        else:
            return self.connect(url, None)["code"]

class RobotHandler(HTTP):
    """Class for handling/analyzing robots.txt"""
    def __init__(self, url: str, creds: [str, str]) -> None:
        """
        connect to the url and return the response
        Args:
            creds: basic auth credentials
        RetVal:
            dict: the string response or empty string
        """
        super().__init__()
        self.robotFiles = ["robot.txt", "robots.txt"]
        self.keywords = [line.strip('\n') for line in open('robot.txt').readlines()]
        # you can add more keywords above to detect custom keywords
        self.dir_pattern = re.compile(r".+: (.+)")
        self.url = url
        self.creds = creds

    def scan(self) -> list:
        """
        Scan the url for robot file and return the matched keywords
        RetVal:
            list: list of matched keywords or []
        """
        pages = []
        matched = []
        urls = list(map(lambda fname: self.url + fname, self.robotFiles))
        # generate URL list with robot file names

        for link in urls:
            result = self.connect(link, self.creds)
            if result["code"] == 200:
                self.logger.info("Detected robot file at %s", link)
                pages.append(result["response"].split('\n'))

        for page in pages:
            result = self.analyze(page)
            for i in result:
                matched.append(i)
        return matched

    def analyze(self, data: list) -> list:
        """
        Analyze the content for interesting keywords
        Args:
            data: the content of the file
        RetVal:
            list: list of matched keywords, or []
        """
        matched = []
        dirs = []
        # extract all directory pattern
        for line in data:
            result = self.dir_pattern.findall(line)
            if result:
                dirs.append(result[0])

        # look for keywords
        for keyword in self.keywords:
            for directory in dirs:
                if keyword in directory.lower():
                    matched.append(directory)
        return matched

