import re
import requests


class RobotHandler:
    """Class for handling/analyzing robots.txt"""

    def __init__(self, url: str) -> None:
        super().__init__()
        self.robot_files = ["robot.txt", "robots.txt"]
        self.keywords = [line.strip('\n') for line in open("wordlists/robot.txt").readlines()]
        # you can add more keywords above to detect custom keywords
        self.dir_pattern = re.compile(r".+: (.+)")

        self.url = url

        if not self.url.endswith("/"):
            self.url = self.url + "/"

    def scan(self) -> list:
        """
        Scan the url for robot file and return the matched keywords
        RetVal:
            list: list of matched keywords or []
        """
        pages = []
        matched = []
        urls = list(map(lambda fname: self.url + fname, self.robot_files))
        # generate URL list with robot file names

        try:
            for link in urls:
                result = requests.get(link)
                if result.status_code == 200:
                    print(f"[+] Detected robot file at {link}")

                    pages.append(result.text.split('\n'))

            for page in pages:
                result = self.analyze(page)
                for i in result:
                    matched.append(i)
            return matched
        except requests.exceptions.ConnectionError:
            print("[!] Unable to connect to server")
            exit()

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
