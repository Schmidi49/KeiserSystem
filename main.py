import keyboard
import os
import time
import json

maxVal = -1
backTrack = 3


class Player:
    def __init__(self, id, name, score=0, active=True):
        self.id = id
        self.name = name
        self.value = maxVal - id
        self.score = score
        self.history = []
        self.active = active
        self.malus = 0

    def eval(self, playerlist):
        self.score = self.value
        for res in self.history:
            self.score += playerlist[res[0]] * res[1] / 6

    def print(self):
        print("{}: Name: {}, Score: {}".format(self.id, self.name, self.score))

    def colorAVG(self):
        sum = 0
        for res in self.history:
            sum += res[3]
        return sum

    def legalPairing(self, matched):
        length = len(self.history)
        if length <= backTrack:
            for res in self.history:
                if res[0] == matched:
                    return False
            return True
        for i in range(backTrack):
            if self.history[length - i][0] == matched:
                return False
        return True

    def toJSON(self):
        dic = {"id": self.id, "name": self.name, "score": self.score, "value": self.value, "malus": self.malus,
               "history": self.history, "active": self.active}
        return json.dumps(dic)

    def fromJSON(self, playerjson):
        # TODO: Errorhandling: Keyerror
        dic = json.loads(playerjson)
        self.id = dic["id"]
        self.name = dic["name"]
        self.value = dic["value"]
        self.score = dic["score"]
        self.history = dic["history"]
        self.active = dic["active"]
        self.malus = dic["malus"]


class Playerlist:
    def __init__(self, listofplayers=None):
        if listofplayers is None:
            listofplayers = []
        self.cur = listofplayers
        self.cur.sort(key=lambda x: x.score, reverse=True)
        self.sortedByID = sorted(self.cur, key=lambda x: x.score, reverse=True)
        self.assignment = []
        for player in self.cur:
            if type(player) != Player:
                raise ValueError("Inserted a none-Player into Playerlist")
        global maxVal
        if maxVal < 0:
            maxVal = 3 * len(self.cur) // 2 + 1
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i - self.cur[i].malus
            self.cur[i].id = i

    def __len__(self):
        return len(self.sortedByID)

    def print(self):
        for player in self.sortedByID:
            player.print()

    def reEval(self):
        self.cur.sort(key=lambda x: x.score, reverse=True)
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i
        for player in self.cur:
            player.eval(self.sortedByID)
            player.score -= player.malus


def menu_main(playerlist: Playerlist = None):
    """
    Menu points:
    0: New tournament
    1: Load
    2: Save
    3: Exit
    4: New round
    5: Stats
    6-n: Active Players

    :param playerlist: currently used Playerlist
    :return:
    """
    MAXMENUPOINT = 5
    pos = 0

    while keyboard.is_pressed("enter"):
        pass

    if not playerlist:
        os.system('cls')
        print('*' if pos == 0 else ' ', "New tournament")
        print('*' if pos == 1 else ' ', "Load")
        while True:
            pressed = keyboard.read_key()
            time.sleep(0.005)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.005)
            if pressed == "nach-oben" or pressed == "nach-unten":
                pos ^= True
            elif pressed == "enter":
                break
            else:
                continue
            os.system('cls')
            print('*' if pos == 0 else ' ', "New tournament")
            print('*' if pos == 1 else ' ', "Load")
            # print(pressed)
        if pos == 0:
            playerlist = newGame()
            playerlist.print()
            return playerlist
        else:
            load(playerlist)
    else:
        os.system('cls')
        print('*' if pos == 0 else ' ', "New tournament")
        print('*' if pos == 1 else ' ', "Load")
        print('*' if pos == 2 else ' ', "Save")
        print('*' if pos == 3 else ' ', "Exit")
        print('*' if pos == 4 else ' ', "New Round")
        print('*' if pos == 5 else ' ', "Stats")
        for player in playerlist.sortedByID:
            print('*' if pos == MAXMENUPOINT + 1 + player.id else ' ', 'A' if player.active else 'P', player.name + ':',
                  'score: ' + str(player.score) + ',', 'malus: ' + str(player.malus))

        while True:
            pressed = keyboard.read_key()
            time.sleep(0.005)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.005)
            if pressed == "nach-oben":
                pos = down(pos, MAXMENUPOINT + len(playerlist))
            elif pressed == "nach-unten":
                pos = up(pos, MAXMENUPOINT + len(playerlist))
            elif pressed == "enter":
                if pos > MAXMENUPOINT:
                    playerlist.sortedByID[pos - MAXMENUPOINT - 1].active ^= True
                else:
                    break
            elif pressed == "tab":
                # TODO: enter some editing tool for a player, for example tweak elo/malus/results/name
                pass
            else:
                continue
            os.system('cls')
            print('*' if pos == 0 else ' ', "New tournament")
            print('*' if pos == 1 else ' ', "Load")
            print('*' if pos == 2 else ' ', "Save")
            print('*' if pos == 3 else ' ', "Exit")
            print('*' if pos == 4 else ' ', "New Round")
            print('*' if pos == 5 else ' ', "Stats")
            for player in playerlist.sortedByID:
                print('*' if pos == 6 + player.id else ' ', 'A' if player.active else 'P', player.name + ':',
                      'score: ' + str(player.score) + ',', 'malus: ' + str(player.malus))
            # print(pressed)

        if pos == 0:
            # TODO: question if game should be saved
            playerlist = newGame()
            playerlist.print()
            return playerlist
        elif pos == 1:
            load(playerlist)
        elif pos == 2:
            save(playerlist)
        elif pos == 3:
            close(playerlist)
        elif pos == 4:
            newRound(playerlist)
        elif pos == 5:
            stats()

        return pos


def menu_round(playerlist: Playerlist):
    print("new round menu")
    pass


def up(pos, max, min=0):
    pos += 1
    if pos > max:
        pos = min
    return pos


def down(pos, max, min=0):
    pos -= 1
    if pos < min:
        pos = max
    return pos


def load(playerlist: Playerlist):
    print("loading . . .")
    pass


def save(playerlist: Playerlist):
    print("saving . . .")
    print(maxVal, backTrack, len(playerlist), len(playerlist.assignment))
    for player in playerlist.sortedByID:
        print(player.toJSON())
    for sign in playerlist.assignment:
        print(sign)
    return True


def close(playerlist: Playerlist):
    save(playerlist)
    print("exiting . . .")
    exit()


def newGame():
    print("Insert Players: ")
    playerlist = []
    while True:
        name = input("Name: ")
        if name == "\\":
            if len(playerlist) == 0:
                continue
            else:
                playerlist.pop()
                print("removed last entry")
                continue
        elif name == ";":
            break
        elif name == "":
            print("Empty Name")
            continue

        score = input("Elo: ")
        if score == "\\":
            continue
        elif score == ";":
            break
        try:
            score = int(score)
        except ValueError:
            print("illegal input for Elo")
            continue

        playerlist.append(Player(len(playerlist), name, score))

    return Playerlist(playerlist)


def newRound(playerlist: Playerlist):
    toMatch = []
    for player in playerlist.cur:
        if player.active:
            toMatch.append(player.id)
        else:
            playerlist.assignment.append((player.id, -2, 0))

    if len(toMatch) < 2:
        return AttributeError("Insufficient number of players")

    # TODO: make backtrack continuously smaller
    if not match(playerlist, toMatch):
        return ValueError("no valid round possible with given configuration")


def match(playerlist: Playerlist, toMatch, startindex=0, matched=None):
    if matched is not None:
        for i in range(startindex, len(toMatch)):
            if playerlist.sortedByID[matched].legalPairing(i):
                curtry = toMatch.pop(startindex + i)
                if match(playerlist, toMatch, 0):
                    playerlist.assignment.append((matched, curtry, 0))
                    return True
                toMatch.insert(startindex + i, curtry)
        return False

    else:
        if len(toMatch) == 0:
            return True
        elif len(toMatch) == 1:
            playerlist.assignment.append((toMatch[0], -1, 0))
            return True
        else:
            for i in range(startindex, len(toMatch) - 1):
                curtry = toMatch.pop(startindex + i)
                if match(playerlist, toMatch, startindex + i, curtry):
                    return True
                toMatch.insert(startindex + i, curtry)
            return False


def stats():
    print("stats uwu")
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    playerslist = [Player(0, "Willi", 15),
                   Player(1, "Jonny", 7),
                   Player(2, "Erik", 20),
                   Player(3, "Annika", 3)]
    curTournament = Playerlist(playerslist)
    curTournament.sortedByID[1].active = False
    newRound(curTournament)
    save(curTournament)

    """
    while True:
        if menu_main(curTournament):
            pass
    """