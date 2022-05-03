# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import keyboard
import os
import time

maxVal = 50
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

        return self

    def eval(self, playerlist):
        score = self.value - self.malus
        for res in self.history:
            score += playerlist[res[0]] * res[1]

    def print(self):
        print("{}: Name: {}, Score: {}".format(self.id, self.name, self.score))

class Playerlist:
    def __init__(self, playerlist=None):
        if playerlist is None:
            playerlist = []
        self.cur = playerlist
        self.sortedbyID = sorted(self.cur, key=lambda x: x.score, reverse=True)
        for player in self.cur:
            if type(player) != Player:
                raise ValueError("Inserted a none-Player into Playerlist")
        self.cur.sort(key=lambda x: x.score, reverse=True)
        maxVal = 3 * len(self.cur) // 2 + 1
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i
            self.cur[i].id = i

    def print(self):
        for player in self.sortedbyID:
            player.print()


    def reeval(self):
        self.cur.sort(key=lambda x: x.score, reverse=True)
        for i in range(len(self.cur)):
            self.cur[i].value = maxVal - i
        for player in self.cur:
            player.eval(self.sortedbyID)

def menu(playerlist=None):
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

    if playerlist is None:
        playerlist = []
    pos = 0

    if playerlist == []:
        pressed = ""
        while True:
            os.system('cls')
            print('*' if pos == 0 else ' ', "New tournament")
            print('*' if pos == 1 else ' ', "Load")

            pressed = keyboard.read_key()
            time.sleep(0.005)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.005)
            if pressed == "nach-oben" or pressed == "nach-unten":
                pos ^= True
            elif pressed == "enter":
                break
            #print(pressed)
        if pos == 0:
            playerlist = newGame()
            playerlist.print()
            return playerlist
        else:
            load()
    else:
        while True:
            os.system('cls')
            print('*' if pos == 0 else ' ', "New tournament")
            print('*' if pos == 1 else ' ', "Load")
            print('*' if pos == 2 else ' ', "Save")
            print('*' if pos == 3 else ' ', "Exit")
            print('*' if pos == 4 else ' ', "New Round")
            print('*' if pos == 5 else ' ', "Stats")
            for player in playerlist.sortedbyID:
                print('*' if pos == 1 else ' ', 'A' if player.active else 'P', player.name + ':',
                      'score: '+player.score+',', 'malus: '+player.malus)

            pressed = keyboard.read_key()
            time.sleep(0.005)
            while keyboard.is_pressed(pressed):
                pass
            time.sleep(0.005)
            if pressed == "nach-oben":
                pos = up(pos, 5 + len(playerlist))
            elif pressed == "nach-unten":
                pos = down(pos, 5 + len(playerlist))
            elif pressed == "enter":
                break
            elif pressed == "tab":
                #TODO: enter some editing tool for a player, for example tweak elo/malus/results
                pass
            # print(pressed)

        if pos == 0:
            playerlist = newGame()
            playerlist.print()
            return playerlist
        elif pos == 1:
            load()
        elif pos == 2:
            save()
        elif pos == 3:
            close()
        elif pos == 4:
            newRound()
        elif pos == 5:
            stats()
        else:
            playerlist.sortedbyID[pos-5].active ^= True





def up(pos, max, min=0):
    pos+=1
    if pos > max:
        pos = min
    return pos

def down(pos, max, min=0):
    pos-=1
    if pos < min:
        pos = max
    return pos

def load():
    print("loading . . .")
    pass

def save():
    print("saving . . .")
    pass

def close():
    save()
    print("exiting . . .")
    exit()

def newGame():
    print("Insert Players: ")
    playerlist=[]
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
        elif type(score) is not int:
            print("illegal input for Elo")
            continue

        playerlist.append(Player(len(playerlist), name, int(score)))


    return Playerlist(playerlist)

def newRound():
    print("playing . . .")
    pass

def stats():
    print("stats uwu")
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    curTournament = menu()

    while True:
        if menu(curTournament):
            pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/>