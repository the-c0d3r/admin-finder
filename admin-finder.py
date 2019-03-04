# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
import queue

from lib.log import setupLogger
from lib.wordlist import WordListGenerator
from lib.worker import WorkerThread
from lib.connection import URLFormatter
from lib.connection import RobotHandler


def main():
    """
    A function to parse the command argument
    And control the main program
    """

    logger = setupLogger()
    parser = argparse.ArgumentParser(prog="admin-finder.py", description="Admin panel finder")
    parser.add_argument("-u", "--url", help="target url/website")
    parser.add_argument("-w", "--wordlist", help="wordlist to use, default 'wordlist.txt'")
    parser.add_argument("-t", "--threadcount", help="Number of threads to use")

    args = parser.parse_args()

    if args.url is None:
        parser.print_help()
        print("[-] -u target paremeter required")
        exit()

    if args.threadcount is not None:
        if not args.threadcount.isdigit():
            print("[-] Process count parameter needs to be digit")
            exit()
    else:
        args.threadcount = 20

    if args.wordlist is None:
        args.wordlist = "wordlist.txt"

    args.url = URLFormatter(args.url).geturl()
    robot_handler = RobotHandler(args.url)
    result = robot_handler.scan()

    if result:
        logger.info("Detected keywords in robot file")
        print("-" * 30)
        print("\n".join(result))
        print("-" * 30)
        print("Would you like to continue scanning?")
        choice = input("[y]/n: ")
        if choice == "n":
            exit()

    try:
        workQueue = queue.Queue()
        workerPool = []
        for _ in range(int(args.threadcount)):
            thread = WorkerThread(workQueue)
            thread.daemon = True
            thread.start()
            workerPool.append(thread)

        for url in WordListGenerator(args.url, filename=args.wordlist):
            workQueue.put(url)

        logger.info("Scanner started")

        while not workQueue.empty():
            pass
        # to lock the main thread from exiting
    except KeyboardInterrupt:
        logger.info("Detected Ctrl + C, terminating")
        for i in workerPool:
            i.work = False



def banner():
    print('\033[91m' + """
    ╔════════════════════════════════════════════╗
    ║               .          .                 ║
    ║ ,-. ,-| ,-,-. . ,-.   ," . ,-. ,-| ,-. ,-. ║
    ║ ,-| | | | | | | | |   |- | | | | | |-' |   ║
    ║ `-^ `-^ ' ' ' ' ' '   |  ' ' ' `-^ `-' '   ║
    ║                       '          the-c0d3r ║
    ╚════════════════════════════════════════════╝
    """ + '\033[0m')

if __name__ == "__main__":
    banner()
    main()
