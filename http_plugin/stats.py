# Drop into REPL:
# python3.10 -i http_plugin/stats.py

import requests

class Stats:
    def __init__(self):
        self.reload()

    def reload(self):
        r = requests.get('http://localhost:8080/stats')
        self.i = r.json()

    def level(self, index):
        self.reload()
        return self.i[index]['boostedLevel'], self.i[index]['level']

    def prayer(self):
        return self.level(PRAYER)
    
    def hp(self):
        return self.level(HITPOINTS)

    def __str__(self):
        output = ""
        for slot in self.i:
            output += f"{slot['stat']}: {slot['boostedLevel']}/{slot['level']} "
            output += "\n"
        return output
    
ATTACK = 0
DEFENCE = 1
STRENGTH = 2
HITPOINTS = 3
RANGED = 4
PRAYER = 5
MAGIC = 6
COOKING = 7
WOODCUTTING = 8
FLETCHING = 9
FISHING = 10
FIREMAKING = 11
CRAFTING = 12
SMITHING = 13
MINING = 14
HERBLORE = 15
AGILITY = 16
THIEVING = 17
SLAYER = 18
FARMING = 19
RUNECRAFT = 20
HUNTER = 21
CONSTRUCTION = 22

if __name__ == '__main__':
    stats = Stats()
    print("Prayer: ", stats.prayer())
    print("HP: ", stats.hp())



        