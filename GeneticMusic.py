# -*- coding: utf-8 -*-

import getopt
import os
import random
import sys
import time
from datetime import datetime

import keyboard
import mido


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

def track_info(track, debug=False):
    time_sum = 0
    sign = None
    for msg in track:
        if(debug):
            print(msg)
        if(not msg.is_meta):
            time_sum += msg.time
        else:
            if(msg.type == "time_signature"):
                sign = msg
    return time_sum, sign

def beats(single):
    time_max = 0
    tact_size = 0
    numerator = 0
    denominator = 0
    
    for track in single.tracks:
        time, sign = track_info(track)
        if(sign is not None):
            tact_size = 1920/sign.denominator*sign.numerator #1920 тиков в целой делим на размер
            denominator = sign.denominator
            numerator = sign.numerator
        if(time>time_max):
            time_max = time
        print("meta", sign)
    return time_max / tact_size, tact_size, numerator, denominator

def takts_check(track,debug=False):   
    time_sum = 0
    time_min = 1000000000000000000
    time_max = 0
    for msg in track:
        if(debug):
            print(msg)
        if(not msg.is_meta):
            time_sum += msg.time
            if(msg.time != 0 and msg.time < time_min):
                time_min = msg.time
            if(msg.time > time_max):
                time_max = msg.time
        #keyboard.wait(hotkey='esc')

    print("TimeSum:", time_sum)
    print("TimeMin:", time_min) 
    print("TimeMax:", time_max)

    if(time_sum % time_max == 0):
        print("Тиков в такте", time_max)
        print("тактов:", time_sum / time_max)


def get_tacts(track,tact_size):
    tacts = []
    tact = []
    tickts = 0

    for msg in track:
        if(tickts >= tact_size and msg.type == 'note_on' and len(tact) > 0):
            tacts.append(tact)
            tact = []
            tickts = 0
        tact.append(msg)
        tickts += msg.time
    tacts.append(tact)

    return tacts


def change_time_signature(track, numerator, denominator):
    for i, msg in enumerate(track):
        if(msg.is_meta and msg.type == "time_signature"):
            temp = msg.dict()
            temp.update({"numerator": numerator, "denominator":denominator})
            track.remove(msg)
            track.insert(i, mido.MetaMessage.from_dict(temp))
            break
        if(i>10):
            break
        
def add_tact(track,tact):
    for msg in tact:
        track.append(msg)


def сrossoverSigles4(single1, single2):
    tact_size = 0 #размер такта
    tacts_num = 0 #количество тактов
    single1_info1 = beats(single1)
    single1_info2 = beats(single2)
    numerator = 0
    denominator = 0

    if(single1_info1[1] > single1_info2[1]):
        tacts_num, tact_size, numerator, denominator = single1_info1
    else:
        tacts_num, tact_size, numerator, denominator = single1_info2
    print("tacts =",tacts_num)
    mask_end = int(2**tacts_num - 1)
    print("mask_end", mask_end)
    singles = [mido.MidiFile() for i in range(mask_end)]
    for j, (track1, track2) in enumerate(zip(single1.tracks, single2.tracks)):

        change_time_signature(track1,numerator,denominator)
        change_time_signature(track2,numerator,denominator) 
        mask = 1
        
        if(j == 0):
            n = int(0) 
            n_end = int(tacts_num)
            while (mask < len(singles)):
                new_track=singles[int(mask-1)].add_track("Acoustic Piano " + str(j))
                for i, (tact1, tact2) in enumerate(zip(get_tacts(track1, tact_size), get_tacts(track2, tact_size))):
                    try:
                        if(bin(mask)[i+2] == '1'):
                            add_tact(new_track, tact1)
                        else:
                            add_tact(new_track, tact2)
                    except IndexError:
                        add_tact(new_track, tact2)
                """ for single in singles:
                    track = single.add_track("Acoustic Piano " + str(j))
                    #for msg in newTrack:
                    track.append(new_track) """
                mask+=1
                if(mask/tacts_num % 100 == 0):
                    print("n =", mask, "track1")
                n=n_end
                n_end += tacts_num
        else:
            n = 0
            n_end = int(tacts_num)
            step = int(j * tacts_num)
            while (mask < len(singles)):
                new_track = singles[n].add_track("Acoustic Piano " + str(j))
                for i, (tact1, tact2) in enumerate(zip(get_tacts(track1, tact_size), get_tacts(track2, tact_size))):
                    try:
                        if(str(mask)[i] == '1'):
                            add_tact(new_track, tact1)
                        else:
                            add_tact(new_track, tact2)
                    except IndexError:
                        add_tact(new_track, tact2)
                for single in singles[n:len(singles):step]:
                    track = single.add_track("Acoustic Piano " + str(j))
                    for msg in new_track:
                        track.append(msg)
                mask += 1
                if(mask % 100 == 0):
                    print("n =", mask, "track2")
                n += 1
    return singles


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

    
    print("Компазиции")

    print(single1.filename)
    print("single length ", single1.length)
    print("Beats:", beats(single1))

    for track in single1.tracks:
        print(str(track),'\n')
        takts_check(track)
    
    print(single2.filename)
    print("single length ", single2.length)

    print("Beats:",beats(single2))
    for track in single2.tracks:
        print(str(track),'\n')
        takts_check(track)
    singles = сrossoverSigles4(single1,single2)
    for msg in singles[1000].play():
        port.send(msg)
        if(keyboard.is_pressed('esc')):  # пропустить проигрование трека
            break

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
