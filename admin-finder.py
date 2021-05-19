import argparse
import asyncio
import logging
import random
import time
from typing import Optional

import aiohttp
from aiohttp import ClientResponse

from lib.robot import RobotHandler
from lib.wordlist import WordListGenerator


AGENT_FILE = "config/agents.ini"


async def fetch(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> ClientResponse:
    """Fetch the url with the semaphore and return the response"""
    try:
        await semaphore.acquire()
        async with session.get(url, timeout = 15) as response:
            if response.status != 404:
                semaphore.release()
                return response
    except aiohttp.ClientResponseError as e:
        logging.warning(e.code)
    except asyncio.TimeoutError:
        logging.warning("Timeout")
    except Exception as e:
        logging.warning(e)
    finally:
        semaphore.release()


async def fetch_async(urls: [str], semaphore: asyncio.Semaphore) -> [Optional[str]]:
    """Function that calls the fetch() and await for task completion"""
    tasks = []
    header = {"User-Agent": random.choice(load_agents())}

    async with aiohttp.ClientSession(headers = header) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(session, url, semaphore))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

    return responses


def load_agents() -> [str]:
    """loads all the user agents"""
    with open(AGENT_FILE) as fp:
        agents = [line.strip("\n") for line in fp.readlines()]
    return agents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog = "admin-finder.py", description = "Admin panel finder")
    parser.add_argument("-u", "--url", help = "Target url/website")
    parser.add_argument("-w", "--wordlist", help = "Wordlist to use, default 'wordlist.txt'",
        default = "wordlists/wordlist.txt")
    parser.add_argument("-t", "--threadcount", help = "Number of threads to use", default = 1000)
    return parser


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


def main() -> None:
    banner()
    parser = build_parser()
    args = parser.parse_args()

    if args.url is None:
        parser.print_help()
        print("[-] -u URL paremeter required")
        exit()

    if not args.url.startswith("https://"):
        args.url = "https://" + args.url

    args.threadcount = int(args.threadcount)

    # scan for robot file
    robot_handler = RobotHandler(args.url)
    result = robot_handler.scan()

    if result:
        print("[+] Detected keywords in robot file")
        print("-" * 30)
        print("\n".join(result))
        print("-" * 30)
        print("Would you like to continue scanning?")
        choice = input("[y]/n: ")
        if choice == "n":
            exit()

    try:
        semaphore = asyncio.Semaphore(args.threadcount)
        urls = WordListGenerator(args.url, args.wordlist)

        print(f"[+] Scanning {urls.max} urls with {args.threadcount} threads")

        start = time.time()
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_async(urls, semaphore))
        loop.run_until_complete(future)
        results = future.result()

        end = time.time()
        elapsed = end - start
        print(f"[+] Elapsed: {elapsed:.2f} seconds")
        print(f"[+] Processed: {urls.max}")

        found = [result for result in results if result is not None]

        if len(found) == 0:
            print("[-] Unable to find admin panel")
        else:
            for result in found:
                print(f"[+] {result.status}: {result.url}")
    except KeyboardInterrupt:
        print("[~] Terminating")

        
if __name__ == '__main__':
    main()
