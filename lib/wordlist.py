
class URLGenerator(object):
    """Generator that generates the url list"""
    def __init__(self, url, filename="wordlist.txt"):
        self.url = url
        self.filename = filename
        self.wordlist = [line.strip('\n') for line in open(filename).readlines()]
        self.index = 0
        self.max = len(self.wordlist)

    def __iter__(self):
        """Makes a iterator object out of this class"""
        return self

    def __next__(self):
        """Returns the next url in the list"""
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
