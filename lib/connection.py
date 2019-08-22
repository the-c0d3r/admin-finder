import random
import re
import requests
import logging
from requests.auth import HTTPBasicAuth

AGENT_FILE="config/agents.ini"
ROBOT_FILE="wordlists/robot.txt"


class HTTP:
    """Handles the http connection"""
    def __init__(self) -> None:
        """initialize the http connection object"""
        self.agents = [line.strip("\n") for line in open(AGENT_FILE).readlines()]
        self.session = requests.Session()
        self.session.headers = self.get_headers()
        self.logger = logging.getLogger("admin-finder")

    def get_headers(self) -> dict:
        """ Returns randomly chosen UserAgent """
        return {
            "User-Agent": random.choice(self.agents)
        }

    def connect(self, url: str) -> int:
        """
        connect to the url and return the response
        Args:
            url: the url to open
        RetVal:
            int: the status code
        """
        try:
            return self.session.get(url).status_code
        except requests.exceptions.ConnectionError as error:
            print("Connection error: ", error.args)
            return -1


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

    def scan(self, url: str) -> int:
        """Scans the website by connecting, and return status code"""
        return self.connect(url)


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
        self.keywords = [line.strip('\n') for line in open(ROBOT_FILE).readlines()]
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

