# -*- coding: utf-8 -*-

import sys
import getopt
import mido
import random
import time
import os
from datetime import datetime
import keyboard

def сrossoverSigles(single1, single2, numberOfNotes):
    newSingle = mido.MidiFile()
    notesSwitcher = numberOfNotes
    for i, (track1, track2) in enumerate(zip(single1.tracks, single2.tracks)):
        if(track1 is None or track1 is None):
            break
        newTrack = newSingle.add_track("Acoustic Piano " + str(i))
        flag = random.random()
        for j, (msg1, msg2) in enumerate(zip(track1, track2)):
            ''' if(msg1.tempo > msg2("tempo")):
                print("msg1:", msg1)
                print("msg2:", msg2)
                newTrack.append(msg2)
                continue
            else:
                newTrack.append(msg1)
                continue '''
            if(msg1 is None or msg2 is None):
                break
            if(flag):
                newTrack.append(msg1)
            else:
                newTrack.append(msg2)
            if(j >= notesSwitcher and msg1.type == 'note_on'):
                #print("split ",notesSwitcher)
                notesSwitcher = j + numberOfNotes
                flag = not flag
    return newSingle

def сrossoverSigles2(single1, single2, numberOfNotes):
    newSingle = mido.MidiFile()
    for i, (track1, track2) in enumerate(zip(single1.tracks, single2.tracks)):
        if(track1 is None or track1 is None):
            break
        newTrack = newSingle.add_track("Acoustic Piano " + str(i))
        #print(newTrack.name)
        flag = random.random()
        for j, (msg1, msg2) in enumerate(zip(track1, track2)):
            if(msg1 is None or msg2 is None):
                break
            if(flag):
                newTrack.append(msg1)
                #print(msg1)
            else:
                newTrack.append(msg2)
                #print(msg2)
            if(numberOfNotes != -1 and j >= numberOfNotes):
                print("switch", numberOfNotes)
                flag = not flag
                numberOfNotes = -1
            
    return newSingle

#Равномерное скрещивание
def сrossoverSigles3(single1, single2, numberOfNotes):
    newSingle = mido.MidiFile()
    print("switch", numberOfNotes)
    for i, (track1, track2) in enumerate(zip(single1.tracks, single2.tracks)):
        if(track1 is None or track1 is None):
            break
        newTrack = newSingle.add_track("Acoustic Piano " + str(i))
        flag = random.random()
        print("track ",i)
        for j, (msg1, msg2) in enumerate(zip(track1, track2)):
            if(msg1 is None or msg2 is None):
                break
            if(flag):
                newTrack.append(msg1)
                #print(msg1)
            else:
                newTrack.append(msg2)
                #print(msg2)
            if(j>10 and not (j % numberOfNotes)and random.random()):#меняем дорожку после каждого j вызова
                flag = not flag
            
    return newSingle


def main(argv=None):
    single1 = None
    single2 = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(
                argv[1:], "hl:r:", ["help", "left=", "right=" ])
        except getopt.GetoptError:
            print(argv[0], ' -l <file_1.mid> -r <file_2.mid>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print(argv[0], ' -l <file_1.mid> -r <file_2.mid>')
                sys.exit()
            elif opt in ("-l", "--left"):
                if(arg == ""):
                    raise Exception("-l no parametr"+arg)
                single1 = mido.MidiFile(arg)
            elif opt in ("-r", "--right"):
                if(arg == "" or arg is None):
                    raise Exception("-r no parametr"+arg)
                print("arg:",arg,".")
                single2 = mido.MidiFile(arg)
        # more code, unchanged
    except Exception as e:
        print(str(e))
        print("for help use --help")
        return 2
    random.seed()

    port = mido.open_output(mido.get_output_names()[0])
    print("тестовый звук")
    msg = mido.Message('note_on', note=60, velocity=80)
    port.send(msg)
    
    for msg in single1.tracks[0]:
        print(msg)
        port.send(msg)
        #keyboard.wait(hotkey='esc')

    print("Компазиции")
    print(single1.filename)
    print(single2.filename)
    #print("количество нот в блоке для скрещевания - ", numberOfNotes)
    while (single1 is not None and single2 is not None):
        singles = []
        for i in range(0, 4):
            print("single ",i)
            singles.append(сrossoverSigles3(single1, single2, random.randint(2,10)))
        
        for i, single in enumerate(singles):
            print("single - #", i)
            time.sleep(3)
            for j, msg in enumerate(single.play()):
                port.send(msg)
                if(keyboard.is_pressed('esc')): #пропустить проигрование трека
                    break
        qFlaf = True
        while qFlaf:
            print("Выбрать победителя? (Д/Н)")
            s = input().lower()
            if(s == 'д' or s == 'y'):
                print("Выберете композицию и напишите номер")
                try:
                    single1 = singles[int(input())]
                    single2 = None
                except Exception:
                    print("введите корректный номер")
                    continue
                break
            print("Выберете 2 композиции и напишите их номер через пробел")
            try:
                (selectSingle1, selectSingle2) = list(map(int, input().split()))
            except Exception:
                print("выберете только 2 победителей")
                continue
            single1 = singles[selectSingle1]
            single2 = singles[selectSingle2]
            qFlaf = False

    print("winer!")
    print("Пропустить композицию - клавиша 'ESC'")
    for msg in single1.play():
        port.send(msg)
        if(keyboard.is_pressed('esc')):
            break
    single1.save("winer_" + datetime.strftime(datetime.now(),
                                            "%Y-%m-%d %H.%M.%S") + ".mid")

if __name__ == "__main__":
    exit(main())
