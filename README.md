# Discord Bot for searching BNS Player Info
A discord bot for searching player profile in blade and soul

## Preview
![Preview](/preview.png?raw=true)

## Requirements
- Python 3.5
- [discord.py](https://github.com/Rapptz/discord.py)
```
  pip install git+https://github.com/Rapptz/discord.py@async
```
- [lxml](http://lxml.de/)  
If windows, please find the binary here: http://www.lfd.uci.edu/~gohlke/pythonlibs/  
Depends on your system, install **lxml-3.6.0-cp35-cp35m-win32.whl** or
**lxml-3.6.0-cp35-cp35m-win_amd64.whl**
```
  pip install lxml-3.6.0-cp35-cp35m-win_amd64.whl
```

## To Run
```
python discord_bns_bot.py
```
## Usage
```
!help
  - Show Command List  
!p [Character Name]
  - Show Character Stats
!b [Number of People] [Market Price]
  - Smart Bid
```
