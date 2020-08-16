import asyncio
import aiohttp
import logging
import random
import sys
import time

from typing import Optional

from aiohttp import ClientSession, ClientResponseError

from lib.wordlist import WordListGenerator

logging.getLogger().setLevel(logging.INFO)

AGENT_FILE = "config/agents.ini"


async def fetch(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> Optional[str]:
    """Fetch the url with the semaphore and return the response"""
    try:
        async with session.get(url, timeout=15) as response:
            return response
    except ClientResponseError as e:
        logging.warning(e.code)
    except asyncio.TimeoutError:
        logging.warning("Timeout")
    except Exception as e:
        logging.warning(e)


async def fetch_async(urls: [str], semaphore: asyncio.Semaphore) -> [Optional[str]]:
    """Function that calls the fetch() and await for task completion"""
    tasks = []
    header = {"User-Agent": random.choice(load_agents())}

    async with ClientSession(headers=header) as session:
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


def main(url: str, wordlist: str, concurrent: int = 1000) -> None:
    try:

        semaphore = asyncio.Semaphore(concurrent)
        urls = WordListGenerator(url, wordlist)

        start = time.time()
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_async(urls, semaphore))
        loop.run_until_complete(future)
        results = future.result()

        end = time.time()
        elapsed = end - start
        print("[+] Elapsed: ", elapsed)
        print("[+] Processed: ", urls.max)

        found = []

        for result in results:
            if not result:
                continue
            if result.status != 404:
                found.append(result)

        if len(found) == 0:
            print("[-] Unable to find admin panel")
        else:
            for result in found:
                print(f"[+] {result.status}: {result.url}")
    except KeyboardInterrupt:
        print("[~] Terminating")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
