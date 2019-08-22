#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import queue

from lib.connection import URLFormatter
from lib.log import setupLogger
from lib.worker import WorkerThread
from lib.wordlist import WordListGenerator


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog = "http-scanner.py", description = "HTTP scanner")
    parser.add_argument("-u", "--url", help = "Target base url", required = True)
    parser.add_argument("-w", "--wordlist", help = "Wordlist to use, default to 'wordlist.txt'", default = "wordlist.txt")
    parser.add_argument("-t", "--threadcount", help = "Number of threads to use, default 20", default = 20)
    return parser


def main():
    logger = setupLogger()
    parser = _get_parser()
    args = parser.parse_args()

    if args.url is None or args.url == "":
        parser.print_help()
        exit()

    args.url = URLFormatter(args.url).geturl()

    try:
        workQueue = queue.Queue()
        workerPool = []
        for _ in range(int(args.threadcount)):
            thread = WorkerThread(workQueue)
            thread.daemon = True
            thread.start()
            workerPool.append(thread)

        for url in WordListGenerator(args.url, filename = args.wordlist):
            workQueue.put(url)

        logger.info("Scanner started")

        while not workQueue.empty():
            pass
        # prevents the main thread from exiting

    except KeyboardInterrupt:
        logger.info("Detected interrupt signal, terminating")
        for worker in workerPool:
            worker.work = False


def banner() -> None:
    """Prints the banner"""
    print("HTTP Scanner")
    print("- the-c0d3r")


if __name__ == '__main__':
    banner()
    main()
