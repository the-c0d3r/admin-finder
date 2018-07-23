import random
import re
import requests


class HTTP(object):
    """Handles the http connection"""
    def __init__(self):
        """initialize the http connection object"""
        self.agents = [line.strip("\n") for line in open("lib/agents.ini").readlines()]

    def get_headers(self):
        """ Returns randomly chosen UserAgent """
        return {
            "User-Agent": random.choice(self.agents)
        }

    def connect(self, url):
        """
        connect to the url and return the response
        Args:
            url: the url to open
        RetVal:
            dict: the string response or empty string
        """
        request = requests.get(url, headers=self.get_headers())
        return {
            "code" : request.status_code,
            "response" : request.text
        }

class URL(object):
    """A url class to handle all the URL related operation"""
    def __init__(self, url):
        """initialize URL object"""
        if url.startswith("http://"):
            self.fullurl = url
        else:
            self.fullurl = "http://" + url
        if not self.fullurl.endswith("/"):
            self.fullurl += "/"

    def geturl(self):
        """Get the formatted url"""
        return self.fullurl


class URLHandler(HTTP):
    """General URL handler"""
    def __init__(self):
        super()



class RobotHandler(HTTP):
    def __init__(self):
        super()
        self.robotFiles = ["robot.txt", "robots.txt"]
        self.keywords = [
            "admin", "Administrator", "login", "user", "controlpanel",
            "wp-admin", "cpanel", "userpanel", "client", "account"
        ]
        self.dir_pattern = re.compile(r".+: (.+)\n")

    def scan(self, url):
        """
        Scan the url for robot file
        Args:
            url: the target url
        RetVal:
            list: list of matched keywords or []
        """
        matched = []
        urls = list(map(lambda fname: url + "/" + fname, self.robotFiles))
        for link in urls:
            result = self.connect(link)
            if result["code"] == 200:
                matched.append(self.analyze(result["response"]))

        return matched

    def analyze(self, data):
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



