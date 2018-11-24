import threading
import logging
import queue

from lib.connection import URLHandler


class WorkerThread(threading.Thread):
    """The threads that will be processing all the wordlist items"""
    def __init__(self, queue: queue.Queue) -> None:
        super().__init__()
        self.queue = queue
        self.urlHandler = URLHandler()
        self.logger = logging.getLogger("admin-finder")
        self.work = True

    def run(self) -> None:
        try:
            while self.work:
                url = self.queue.get()
                if self.urlHandler.scan(url) == 200:
                    self.logger.info("Admin page found: %s", url)
        except KeyboardInterrupt:
            self.logger.info("Ctrl+C Detected in Thread")
            self.work = False
