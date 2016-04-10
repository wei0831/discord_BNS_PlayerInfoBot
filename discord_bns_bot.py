################################################################################
#   FileName: discord_bns_bot.py
#   Author: Jack (https://github.com/wei0831)
#   Date: 04/10/2016
################################################################################
from aiohttp import get
from lxml.html import fromstring
import discord
import getpass

################################################################################
#   USER INFO
################################################################################
# 'na' or 'eu'
BNS_REGION = 'na'
DISCORD_USER_EMAIL = None
DISCORD_USER_PSW = None

################################################################################
#   Data Class
################################################################################
class Character:
    """ This represent player's character data scraping from accessing BNS web API.
    """
    def __init__(self, name):
        """ Initializing properties of a character
        Feel free to add more properties as you needed.

        Args:
            name (str): Character name to search
        """
        self.name = name
        self.id = None
        self.class_name = None
        self.server = None
        self.level = None
        self.hmlevel = None
        self.faction = None
        self.factionLevel = None
        self.guild = None
        self.weapon_name = None
        self.weapon_durability = None
        self.attack_power = None
        self.error = False

    async def parse(self):
        """ Parsing character data from accessing BNS web API
        """
        error_str = b'<h1>This service is temporarily unavailable.</h1>'
        url = 'http://{region}-bns.ncsoft.com/ingame/bs/character/profile?c={name}'
        # Need to convert space to URL encoding character
        page = await get(url.format(name=self.name.replace(' ', '%20'), region=BNS_REGION))
        content = await page.read()
        content = fromstring(str(content))

        # Player ID
        playerID = content.xpath('//dl[@class="signature"]/dt/a/text()')
        if len(playerID) != 0:
            self.id = playerID[0]
        else:
            # Not found, Skip the rest
            self.error = True
            return

        # Player HM Level
        playerHMLv = content.xpath('//span[@class="masteryLv"]/text()')
        if len(playerHMLv) != 0:
            self.hmlevel = playerHMLv[0]

        # Player Weapon
        playerWeapon = content.xpath('//div[@class="wrapWeapon"]/div/p/img')
        if len(playerWeapon) != 0:
            self.weapon_name = playerWeapon[0].get('alt')
            #self.weapon_link = weapon_node[0].get('src')

        # Player Weapon Durability
        playerWeaponDurability = content.xpath('//div[@class="wrapWeapon"]/div/div[@class="quality"]/span[@class="text"]/text()')
        if len(playerWeaponDurability) != 0:
            self.weapon_durability = playerWeaponDurability[0]

        # Player Info
        playerInfo = content.xpath('//dd[@class="desc"]/ul/li/text()')

        if self.hmlevel == None:
            if len(playerInfo) == 3:
                # [CLASS NAME] [LEVEL] [SERVER]
                self.class_name, self.level, self.server = [x.replace('[', '').replace(']', '') for x in playerInfo]
            elif len(playerInfo) == 4:
                # [CLASS NAME] [LEVEL] [SERVER] [FACTION]
                self.class_name, self.level, self.server, self.faction = [x.replace('[', '').replace(']', '') for x in playerInfo]
            elif len(playerInfo) == 5:
                # [CLASS NAME] [LEVEL] [SERVER] [FACTION] [GUILD]
                self.class_name, self.level, self.server, self.faction, self.guild = [x.replace('[', '').replace(']', '') for x in playerInfo]
        else:
            if len(playerInfo) == 4:
                # [CLASS NAME] [LEVEL] [] [SERVER]
                self.class_name, self.level, _, self.server = [x.replace('[', '').replace(']', '') for x in playerInfo]
            elif len(playerInfo) == 5:
                # [CLASS NAME] [LEVEL] [] [SERVER] [FACTION]
                self.class_name, self.level, _, self.server, self.faction = [x.replace('[', '').replace(']', '') for x in playerInfo]
            elif len(playerInfo) == 6:
                # [CLASS NAME] [LEVEL] [] [SERVER] [FACTION] [GUILD]
                self.class_name, self.level, _, self.server, self.faction, self.guild = [x.replace('[', '').replace(']', '') for x in playerInfo]

        # Faction and Faction Level
        if self.faction != None:
            faction_texts = self.faction.split('\xa0')
            self.faction = faction_texts[0]
            self.factionLevel = faction_texts[1]

        # Player Attack Power
        playerAP = content.xpath('//div[@class="attack"]/h3/span[@class="stat-point"]/text()')
        if len(playerAP) != 0:
            self.attack_power = playerAP[0]

    def format(self):
        """ Output character data as string
        """
        if self.error:
            return '```\n' \
                   '==== Character Profile ====\n' \
                   'Character Not Found !!' \
                   '============================\n' \
                   '```\n'

        result =  '```\n' \
               '==== Character Profile ====\n' \
               'Name: {name} [{ID}]\n' \
               'Server: {server} \n' \
               'Class: {class_name}\n' \
               'Level: {level} | {hmlevel}\n' \
               'Faction: {faction} | {factionLevel}\n' \
               'Guild: {guild}\n' \
               'Weapon: {weapon} [{weapon_durability}]\n' \
               'Attack Power: {attack_power}\n' \
               '============================\n' \
               '```\n'
        return result.format(name=self.name, ID=self.id, server=self.server, class_name=self.class_name, level=self.level, hmlevel = self.hmlevel, faction=self.faction, factionLevel=self.factionLevel, guild=self.guild, weapon=self.weapon_name, weapon_durability=self.weapon_durability, attack_power=self.attack_power)

################################################################################
#   Discord
################################################################################
print("==== Discord BNS Character Info Search Bot ====")
print("[SYS] Initializing discord client...")
client = discord.Client(cache_auth=False)

@client.event
async def on_message(msg):
    ''' Detect message in discord
    '''
    if msg.content.startswith('!help'):
        result = '```\n' \
              '==== Command Lists ====\n' \
              '\t!p [Character Name] - Show Character Stats\n' \
              '```\n'
        await client.send_message(msg.channel, result)

    elif msg.content.startswith('!p'):
        args = msg.content.split(' ')
        character = Character(' '.join(args[1:]))
        await character.parse()
        await client.send_message(msg.channel, character.format())

@client.event
async def on_ready():
    print("[SYS] Successfully login as the user: '{user}'".format(user=client.user.name))
    print("[SYS] Monitoring...")

################################################################################
#   Main
################################################################################
userID = DISCORD_USER_EMAIL
userPSW = DISCORD_USER_PSW
if userID == None:
    userID = input("Enter Discord Email: ")
else:
    print("Your Discord ID is {userID}".format(userID=userID))
if userPSW == None:
    userPSW = getpass.getpass("Enter Discord Password: ")

try:
    client.run(userID, userPSW)
except:
    print("[ERROR] Login Fail...")

client.close()