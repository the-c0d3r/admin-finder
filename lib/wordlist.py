
class URLGenerator(object):
    """Generator that generates the url list"""
    def __init__(self, url, filename="wordlist.txt"):
        self.url = url
        self.filename = filename
        self.wordlist = [line.strip('\n') for line in open(filename).readlines()]
        self.index = 0
        self.max = len(self.wordlist)

    def __iter__(self):
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

