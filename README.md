# admin-finder

```
╔════════════════════════════════════════════╗
║               .          .                 ║
║ ,-. ,-| ,-,-. . ,-.   ," . ,-. ,-| ,-. ,-. ║
║ ,-| | | | | | | | |   |- | | | | | |-' |   ║
║ `-^ `-^ ' ' ' ' ' '   |  ' ' ' `-^ `-' '   ║
║                       '          the-c0d3r ║
╚════════════════════════════════════════════╝
```

## Usage

```
usage: admin-finder.py [-h] [-u URL] [-w WORDLIST] [-t THREADCOUNT]

Admin panel finder

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Target url/website
  -w WORDLIST, --wordlist WORDLIST
                        Wordlist to use, default 'wordlist.txt'
  -t THREADCOUNT, --threadcount THREADCOUNT
                        Number of threads to use
[-] -u URL paremeter required
```

**Disclaimer: For educational purpose only. Use at your own risk, it is very easy to detect such attempts**

## Features
- Check the robots.txt file, see if there is any useful information in it
- Locates admin webpage using over 800 lines of dictionary list
- asynchronous http client, allowing 10x faster scanning speed than threading

## Config
- `robot.txt` contains the keyword to scan for on the target website's robot file. If they are found, it will be shown on screen.
- `wordlist.txt` contains the wordlist that is used to build the urls for scanning

## Contributors
@the-c0d3r, @Taimander, @B4DF4C3

