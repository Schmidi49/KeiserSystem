import random
import sys

import keyboard
import os
import time
import json

maxVal = -1
backTrack = 3
tournamentName = "default"
path = ".\\"


class Player:
    def __init__(self, ID=-1, name="", score=0, active=True):
        self.id = ID
        self.name = name
        self.value = maxVal - self.id
        self.score = score
        self.history = []
        self.active = active
        self.malus = 0

    def __str__(self):
        return "{}: Name: {}, Score: {:.2f}".format(self.id, self.name, self.score)

    def eval(self, listOfPlayers):
        self.score = self.value
        for res in self.history:
            self.score += listOfPlayers[res[0]].value * res[1] / 6
        pass

    def print(self):
        print("{:2d}: Name: {}, Score: {:.2f}, Malus: {:.1f}".format(self.id, self.name, self.score, self.malus))

    def colorAVG(self):
        sum = 0
        for res in self.history:
            sum += res[2]
        return sum

    def legalPairing(self, matched):
        length = len(self.history)
        if length <= backTrack:
            for res in self.history:
                if res[0] == matched:
                    return False
            return True
        for i in range(backTrack):
            if self.history[length - 1 - i][0] == matched:
                return False
        return True

    def toJSON(self):
        dic = {"id": self.id, "name": self.name, "score": self.score, "value": self.value, "malus": self.malus,
               "history": self.history, "active": self.active}
        return json.dumps(dic)

    def fromJSON(self, playerjson):
        # TODO: Errorhandling: Keyerror
        try:
            dic = json.loads(playerjson)
        except json.decoder.JSONDecodeError:
            return False
        try:
            self.id = int(dic["id"])
            self.name = dic["name"]
            self.value = int(dic["value"])
            self.score = float(dic["score"])
            self.history = dic["history"]
            self.active = bool(dic["active"])
            self.malus = float(dic["malus"])
        except ValueError:
            return False
        return self


class Playerlist:
    """
    cur: list of players sorted by their current score
    sortedByID: list of players sorted by their ID
    assignment: the assignment is a list of arrays size 3, containing the current games between two players
                first two argument are the players in order, third is the state of the Game
                possible states:
                0: no result
                1: first player won
                2: second player won
                3: remi
                4: 0-0
                5: no result (only for not matched players so the game counts as finished)
    """
    def __init__(self, listofplayers=None):
        global maxVal
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
        if maxVal < 3:
            maxVal = 3 * len(self.cur) // 2 + 1
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i - self.cur[i].malus
            self.cur[i].score = self.cur[i].value
            self.cur[i].id = i

    def __len__(self):
        return len(self.sortedByID)

    def __str__(self):
        strng = "["
        for player in self.cur:
            strng += player.name + ","
        return strng[:-1]+"]" if len(strng) > 1 else "[]"

    def add_Player(self, player: Player):
        if player.id != len(self):
            raise IndexError("Player has incorrect ID")
        self.sortedByID.append(player)
        self.cur.append(player)

    def print(self):
        for player in self.sortedByID:
            player.print()

    def evalRound(self):
        for sign in self.assignment:
            if sign[2] == 1:
                self.sortedByID[sign[0]].history.append([sign[1], 6, 1])
                self.sortedByID[sign[1]].history.append([sign[0], 0, -1])
            elif sign[2] == 2:
                self.sortedByID[sign[0]].history.append([sign[1], 0, 1])
                self.sortedByID[sign[1]].history.append([sign[0], 6, -1])
            elif sign[2] == 3:
                self.sortedByID[sign[0]].history.append([sign[1], 3, 1])
                self.sortedByID[sign[1]].history.append([sign[0], 3, -1])
            elif sign[2] == 4:
                self.sortedByID[sign[0]].history.append([sign[1], 0, 1])
                self.sortedByID[sign[1]].history.append([sign[0], 0, -1])
            elif sign[2] == 5:
                if sign[1] == -1:
                    self.sortedByID[sign[0]].history.append([sign[0], 4, 0])
                elif sign[1] == -2:
                    self.sortedByID[sign[0]].history.append([sign[0], 2, 0])
                else:
                    ValueError("a none free match got a no result")
            else:
                raise ValueError("illegal result for match")
        self.assignment.clear()

    def calcRound(self):
        for player in self.cur:
            player.eval(self.sortedByID)
        self.cur.sort(key=lambda x: x.score, reverse=True)
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i
        for player in self.cur:
            player.score -= player.malus

    def assign(self, a: int, b: int):
        if b < 0:
            self.assignment.append([a, b, 5])
            return
        col_a = self.sortedByID[a].colorAVG()
        col_b = self.sortedByID[a].colorAVG()
        if col_a == col_b:
            if random.randint(0, 1):
                self.assignment.append([a, b, 0])
            else:
                self.assignment.append([b, a, 0])
        elif col_a < col_b:
            self.assignment.append([a, b, 0])
        else:
            self.assignment.append([b, a, 0])


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
    :return: playerlist
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
            time.sleep(0.02)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.02)
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
        else:
            return load()
    elif len(playerlist.assignment) > 0:
        if menu_round(playerlist):
            playerlist.evalRound()
            playerlist.calcRound()
        else:
            playerlist.assignment.clear()
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
                  'score: ' + "{:.2f}".format(player.score) + ',', 'malus: ' + str(player.malus))

        while True:
            pressed = keyboard.read_key()
            time.sleep(0.02)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.02)
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
                      'score: ' + "{:.2f}".format(player.score) + ',', 'malus: ' + str(player.malus))
            # print(pressed)

        if pos == 0:
            # TODO: question if game should be saved
            playerlist = newGame()
            return playerlist
        # TODO: messages for successful loading/saving
        elif pos == 1:
            return load()
        elif pos == 2:
            save(playerlist)
        elif pos == 3:
            close(playerlist)
        elif pos == 4:
            #TODO use this sorting in reading
            playerlist.calcRound()
            if newRound(playerlist
                        ):
                playerlist.evalRound()
                playerlist.calcRound()
            else:
                playerlist.assignment.clear()
        elif pos == 5:
            stats(playerlist)

    return playerlist


def menu_round(playerlist: Playerlist):
    """
    Menu points:
    0: Truncate Round
    1: Evaluate Round
    2: Save
    3: Exit
    4-n: Active Players

    :param playerlist: currently used Playerlist
    :return: True if round is finished
             False if round got truncated
    """
    resultDir = {0: "_-_",
                 1: "1-0",
                 2: "0-1",
                 3: "½-½",
                 4: "0-0",
                 5: "/3"}
    MAXMENUPOINT = 3
    pos = 0
    visibleAssignments = []
    for i in range(len(playerlist.assignment)):
        if playerlist.assignment[i][1] >= 0:
            visibleAssignments.append(i)

    while keyboard.is_pressed("enter"):
        pass

    os.system('cls')
    print('*' if pos == 0 else ' ', "Truncate Round")
    print('*' if pos == 1 else ' ', "Evaluate Round")
    print('*' if pos == 2 else ' ', "Save")
    print('*' if pos == 3 else ' ', "Exit")
    for i in range(len(visibleAssignments)):
        print('*' if pos == MAXMENUPOINT + 1 + i else ' ',
              playerlist.sortedByID[playerlist.assignment[visibleAssignments[i]][0]].name, "-",
              playerlist.sortedByID[playerlist.assignment[visibleAssignments[i]][1]].name + ":",
              resultDir[playerlist.assignment[visibleAssignments[i]][2]])

    while True:
        pressed = keyboard.read_key()
        time.sleep(0.02)
        while keyboard.is_pressed(pressed):
            pass
        time.sleep(0.02)
        if pressed == "nach-oben":
            pos = down(pos, MAXMENUPOINT + len(visibleAssignments))
        elif pressed == "nach-unten":
            pos = up(pos, MAXMENUPOINT + len(visibleAssignments))
        elif pressed == "enter":
            if pos == 0:
                return False
            elif pos == 1:
                unfinishedMatch = False
                for sign in playerlist.assignment:
                    if sign[2] == 0:
                        unfinishedMatch = True
                        break
                if unfinishedMatch:
                    print("\nNot all matched have results")
                    continue
                else:
                    return True
            elif pos == 2:
                save(playerlist)
            elif pos == 3:
                close(playerlist)
            else:
                playerlist.assignment[visibleAssignments[pos-1-MAXMENUPOINT]][2] = \
                    up(playerlist.assignment[visibleAssignments[pos-1-MAXMENUPOINT]][2], 4)
        else:
            continue
        os.system('cls')
        print('*' if pos == 0 else ' ', "Truncate Round")
        print('*' if pos == 1 else ' ', "Evaluate Round")
        print('*' if pos == 2 else ' ', "Save")
        print('*' if pos == 3 else ' ', "Exit")
        for i in range(len(visibleAssignments)):
            print('*' if pos == MAXMENUPOINT + 1 + i else ' ',
                  playerlist.sortedByID[playerlist.assignment[visibleAssignments[i]][0]].name, "-",
                  playerlist.sortedByID[playerlist.assignment[visibleAssignments[i]][1]].name + ":",
                  resultDir[playerlist.assignment[visibleAssignments[i]][2]])


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


def load():
    global path, tournamentName, maxVal, backTrack
    filepath = path + tournamentName + ".kst"
    flush_input()
    if not os.path.isfile(filepath):
        print("No legal file specified")
        temp = input("tournament file: ")
        if not os.path.isfile(temp):
            print("File not found, loading failed")
            return False
        end = temp.rfind('\\')
        if end == -1:
            path = ".\\"
            tournamentName = temp.split('.')[0]
        else:
            path = temp[:end]
            tournamentName = temp[:end].split('.')[0]
        filepath = temp

    newListOfPlayers = Playerlist()
    f = open(filepath, 'r')
    line = f.readline()
    params = line.split(' ')
    try:
        maxVal = int(params[0])
        backTrack = int(params[1])
        players = int(params[2])
        matches = int(params[3])
    except (KeyError, ValueError):
        print("input file has corrupted parameters")
        return False

    for i in range(players):
        newPlayer = Player(0, "").fromJSON(f.readline())
        if not newPlayer:
            print("input file has corrupted players")
            return False
        newListOfPlayers.add_Player(newPlayer)
        del newPlayer
    for i in range(matches):
        try:
            match = [int(i) for i in f.readline().split(' ')]
        except ValueError:
            print("input file has corrupted assignments")
            return False
        if len(match) != 3:
            print("input file has corrupted assignments")
            return False
        newListOfPlayers.assignment.append(match)
        del match
    f.close()

    return newListOfPlayers


def save(playerlist: Playerlist):
    print("saving . . .")
    # TODO: file dialog
    global path
    if not path:
        temp = input("path for tournament")
        if os.path.isdir(temp):
            path = temp
        else:
            print("illegal path inserted")
            return False
    elif not os.path.exists(path):
        print("illegal path, cannot save tournament")
        path = ""
        return False
    filepath = path + tournamentName + ".kst"
    f = open(filepath, "w")

    f.write(str(maxVal) + " ")
    f.write(str(backTrack) + " ")
    f.write(str(len(playerlist)) + " ")
    f.write(str(len(playerlist.assignment)) + "\n")
    for player in playerlist.sortedByID:
        f.write(player.toJSON() + "\n")
    for sign in playerlist.assignment:
        f.write(str(sign[0]) + " " + str(sign[1]) + " " + str(sign[2]) + "\n")
    f.close()
    return True


def close(playerlist: Playerlist):
    save(playerlist)
    print("exiting . . .")
    flush_input()
    exit()


def newGame():
    flush_input()
    global tournamentName
    tournamentName = input("Tournament Name: ")
    # TODO: path for tournament
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
        elif score == "":
            score = 0
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
            playerlist.assign(player.id, -2)

    if len(toMatch) < 2:
        return AttributeError("Insufficient number of players")

    # TODO: make backtrack continuously smaller
    if not match(playerlist, toMatch):
        return ValueError("no valid round possible with given configuration")

    playerlist.assignment.reverse()

    return menu_round(playerlist)


def match(playerlist: Playerlist, toMatch, startindex=0, matched=None):
    if matched is not None:
        for i in range(startindex, len(toMatch)):
            if playerlist.sortedByID[matched].legalPairing(toMatch[i]):
                curtry = toMatch.pop(startindex + i)
                if match(playerlist, toMatch, 0):
                    playerlist.assign(matched, curtry)
                    return True
                toMatch.insert(startindex + i, curtry)
        return False

    else:
        if len(toMatch) == 0:
            return True
        elif len(toMatch) == 1:
            playerlist.assign(toMatch[0], -1)
            return True
        else:
            for i in range(startindex, len(toMatch) - 1):
                curtry = toMatch.pop(startindex + i)
                if match(playerlist, toMatch, startindex + i, curtry):
                    return True
                toMatch.insert(startindex + i, curtry)
            return False


def stats(playerlist: Playerlist):
    while keyboard.is_pressed("enter"):
        pass
    
    os.system('cls')

    playerlist.cur.sort(key=lambda x: x.score-x.malus, reverse=True)
    for player in playerlist.cur:
        player.print()

    pressed = keyboard.read_key()
    while keyboard.is_pressed(pressed):
        pass
    time.sleep(0.02)


    pass


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios  # for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


def debug1():
    global tournamentName
    tournamentName = "testcase"
    playerslist = [Player(0, "Willi", 15),
                   Player(1, "Jonny", 7),
                   Player(2, "Erik", 20),
                   Player(3, "Annika", 3)]
    curTournament = Playerlist(playerslist)
    curTournament.sortedByID[1].active = False
    curTournament.sortedByID[0].history.append((2, 6, -1))
    curTournament.sortedByID[1].history.append((1, 2, 0))
    curTournament.sortedByID[2].history.append((0, 0, 1))
    curTournament.sortedByID[3].history.append((3, 4, 0))
    curTournament.calcRound()
    curTournament.sortedByID[1].active = True
    save(curTournament)
    newRound(curTournament)
    curTournament.evalRound()
    curTournament.calcRound()
    save(curTournament)
    close(curTournament)

    while True:
        curTournament = menu_main(curTournament)
        print("PENIS")


def debug0():
    global tournamentName
    tournamentName = "testcase"
    curTournament = Playerlist()
    curTournament = load()
    curTournament.calcRound()
    while True:
        curTournament = menu_main(curTournament)
        pass


if __name__ == '__main__':
    # TODO: fix/test argument handling
    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            path = sys.argv[1]
        elif os.path.isfile(sys.argv[1]):
            endOfPath = sys.argv[1].rfind('\\')
            if endOfPath == -1:
                tournamentName = sys.argv[1].split('.')[0]
            else:
                path = sys.argv[1][:endOfPath]
                tournamentName = sys.argv[1][:endOfPath].split('.')[0]

    curTournament = Playerlist()
    while True:
        curTournament = menu_main(curTournament)
