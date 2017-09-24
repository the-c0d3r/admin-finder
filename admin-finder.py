# -*- coding: utf-8 -*-
#!/usr/bin/env python3


import argparse
import multiprocessing
import os
import random
import re
import requests
import sys
import time
import threading
import Queue


global stateLock
stateLock = multiprocessing.Lock()
cpu_count = multiprocessing.cpu_count()


def urlFormatter(url):
    """ return properly formatted URLs """
    formatted_url = "http://" + url if not url.startswith("http") else url
    return formatted_url

def getHeader():
    """ Returns randomly chosen UserAgent """
    UserAgents = [
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
        'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51'
    ]
    return random.choice(UserAgents)

def scanner(url):
    header = {'User-Agent': getHeader()}
    request = requests.get(url, headers=header)
    code = request.status_code
    return code


class wordlist:
    """ This class loads the wordlist """

    def __init__(self, fileName):
        try:
            # read the file and remove \n at the line ending
            self.load = []
            for i in open(fileName).readlines():
                self.load.append(i.strip('\n'))

        except IOError:
            print("[!] I/O Error, wordlist.txt not found")
            exit()

    def generateList(self, address):
        """
        Generates a wordlist based on the address
        :param address: the address to generate based on
        """
        wordlist = []
        for path in self.load:
            wordlist.append(address + path if address.endswith("/") else address + "/" + path)
        return wordlist


class worker(multiprocessing.Process):
    """ A worker process blueprint """
    def __init__(self, taskQ, finish_event, found_event, quit_event):
        multiprocessing.Process.__init__(self)
        self.taskQ = taskQ
        self.finish_event = finish_event
        self.found_event = found_event
        self.quit_event = quit_event

    def run(self):
        while not self.quit_event.is_set():
            next_task = self.taskQ.get()

            if next_task == None:
                # self.found_event.set()
                self.finish_event.set()
                break

            with stateLock:
                sys.stdout.write("\r[=] Trying : {}{}".format(next_task, " " * 20))
                sys.stdout.flush()

            if scanner(next_task) == 200:
                # means the admin panel is found
                with stateLock:
                    # grab lock
                    print("\n[+] Admin Page Found => {}".format(next_task))
                    print("[+] Terminating")
                    self.found_event.set()
                    break


class controller:
    def __init__(self, config):
        """
        param
        :config: a settings class object for various settings
        """
        self.settings = config

        self.start_time = time.time()

        if self.settings.mass_scanning == True:
            self._init_mass_scanner()
        elif self.settings.mass_scanning == False:
            self._init_scanner()

    def _init_scanner(self):

        self.address      = urlFormatter(self.settings.target)
        self.wordlist     = wordlist(self.settings.wordlist).generateList(self.address)
        self.queue        = multiprocessing.Queue()
        self.processCount = self.settings.processCount
        self.processPool  = []

        self.finish_event = multiprocessing.Event() # To show the scanning is completed
        self.found_event  = multiprocessing.Event() # To show the admin page is found
        self.quit_event   = multiprocessing.Event() # To show the scanning jobs are done

        try:
            print("[+] Target : {}".format(self.address))
            print("[+] Wordlist : {} urls".format(len(self.wordlist)))
            self.createJobs()
            self.startWorkers()

            events_waiter(self.found_event, self.finish_event)
            # to wait for either found the admin panel event or the finish event

            self.quit_event.set()

            self.end_time = time.time()

            if not self.found_event.is_set():
                print("\n[-] Scanner cannot find the admin panel. Try another wordlist!")

            print("[-] Elasped : {} seconds".format(self.end_time - self.start_time))


        except KeyboardInterrupt:
            self.end_time = time.time()
            print("\r\n[-] Ctrl + C detected, terminating processes")
            print("[-] Elasped : {} seconds".format(self.end_time - self.start_time))
            for workerProc in self.processPool:
                workerProc.terminate()

    def _init_mass_scanner(self):
        pass

    def createJobs(self):
        """ Creates the job to scan """
        with stateLock:
            for path in self.wordlist:
                self.queue.put(path)

    def startWorkers(self):
        print("[+] Starting up [{}] processes".format(self.processCount))
        for i in range(self.processCount):
            workerProc = worker(self.queue, self.finish_event, self.found_event, self.quit_event)
            workerProc.start()
            self.processPool.append(workerProc)


class settings:
    """ Used to aggregate various settings """
    def __init__(self):
        """ Various settings can be overwritten here as default settings """
        self.file          = None           # input file for scanning
        self.outfile       = None           # output file for results, preferably csv file
        self.target        = None           # a single target for scanning
        self.processCount  = cpu_count * 2  # default process count is 2 times the cpu count
        self.wordlist      = 'wordlist.txt' # default wordlist

        self.mass_scanning = False          # switch for mass scanning
        self.write_output  = False          # switch for saving results


def events_waiter(*events):
    """ An event waiter for waiting 2 or more events """
    event_share = multiprocessing.Event()

    def set_event_share(event):
        event.wait()
        event.clear()
        event_share.set()

    for event in events:
        threading.Thread(target=set_event_share(event)).start()

    event_share.wait()



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

def handle_args():
    """
    A function to parse the command argument
    And control the main program
    """
    parser = argparse.ArgumentParser(prog="admin-finder.py", description="Admin panel finder")

    parser.add_argument("-t", "--target",       help="Target website")
    parser.add_argument("-p", "--processcount", help="Number of processes to generate")
    parser.add_argument("-f", "--file",         help="Input file for mass scanning")
    parser.add_argument("-o", "--out-file",     help="Output file for storing results")
    parser.add_argument("-w", "--wordlist",     help="To use custom wordlist")
    args = parser.parse_args()

    config = settings()

    if args.target == None and args.file == None:
        parser.print_help()
        print("[-] -t target paremeter required")
        exit()

    config.target       = args.target
    config.file         = args.file
    config.outfile      = args.out_file
    config.processCount = int(args.processcount) if args.processcount else cpu_count * 2

    config.wordlist     = args.wordlist if args.wordlist != None else config.wordlist
    config.write_output = True if args.out_file != None else False

    controller(config)


if __name__ == "__main__":
    banner()
    handle_args()
