import logging


class WordListGenerator(object):
    """Generator that generates the url list"""
    def __init__(self, url, filename="wordlist.txt"):
        self.url = url
        self.wordlist = [line.strip('\n') for line in open(filename).readlines()]
        self.index = 0
        self.max = len(self.wordlist)
        self.logger = logging.getLogger("admin-finder")

    def openFile(self, filename):
        try:
            with open(filename) as filehandle:
                return [line.strip('\n') for line in filehandle.readlines()]
        except IOError:
            self.logger.error("Wordlist file not found")

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        """Creates iterable on the urls to be generated"""
        url = ""
        if self.index >= self.max:
            # TODO Check the index
            raise StopIteration
        else:
            word = self.wordlist[self.index]
            if word.startswith("/"):
                url = self.url + word.lstrip("/")
            else:
                url = self.url + word
            self.index += 1
            return url

