# -*- coding: utf-8 -*-

import getopt
import os
import random
import sys
import time
from datetime import datetime

import keyboard
import mido
import math

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


def get_notes(tact):
    arr = []
    for msg in tact:
        if(hasattr(msg, "note") and msg.note not in arr):
            arr.append(msg.note)
    return arr

def compare_with_note_list(note,notes_list):
    for note1 in notes_list:
        if ((note1-note)%12 == 0):
            return True
    return False

def check_tacts(tact1,tact2):
    """Ищет совпадение нот из нижней партии tact2 с верхней tact1"""
    score=0
    notes = get_notes(tact1)
    for msg in tact2:
        if hasattr(msg, "note") and compare_with_note_list(msg.note, notes):
            score+=1
    return score

''' def copy_track(to_track, from_track):
    for msg in to_track:
        from_track.append(msg) '''

def сrossoverSigles4(single1, single2,score_filter=0):
    """Равномерное скрещивание"""
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

    track_size = tact_size * tacts_num

    print("tacts =",tacts_num)
    mask_end = int(2**tacts_num - 2)
    print("mask_end", mask_end)
    singles = [mido.MidiFile() for i in range(mask_end)]
    print("количество комбинаций",len(singles))
    for j, (track1, track2) in enumerate(zip(single1.tracks, single2.tracks)):

        change_time_signature(track1,numerator,denominator)
        change_time_signature(track2,numerator,denominator) 
        mask = 1
        
        if(j == 0):
            n = int(0) 
            n_end = int(tacts_num)
            for mask in range(1,mask_end+1):
                new_track=singles[int(mask-1)].add_track("Acoustic Piano " + str(j))
                for i, (tact1, tact2) in enumerate(zip(get_tacts(track1, tact_size), get_tacts(track2, tact_size))):
                    try:
                        if(bin(mask)[i+2] == '1'):
                            add_tact(new_track, tact1)
                        else:
                            add_tact(new_track, tact2)
                    except IndexError:
                        add_tact(new_track, tact2)
                if(mask % 1000 == 0):
                    print("n =", mask, "track1")
                n=n_end
                n_end += tacts_num
        else:
            n = 0
            step = int(j * tacts_num)
            print("track2")
            print("Для выхода из перебора нажмите на клавишу <esc>")
            for mask in range(1, mask_end + 1):
                for t in range(0,mask_end):
                    new_track = singles[n].add_track("Acoustic Piano " + str(j))
                    singles.append(mido.MidiFile())
                    temp_track = singles[n].tracks[0]
                    singles[len(singles)-1].tracks.append(temp_track)
                    for i, (tact1, tact2, tact3) in enumerate(zip(get_tacts(track1, tact_size), get_tacts(track2, tact_size), get_tacts(singles[n].tracks[0], tact_size))):
                        try:
                            if(bin(mask)[i+2] == '1'):
                                if(check_tacts(tact3, tact1) >= score_filter):
                                    add_tact(new_track, tact1)
                                else:
                                    break
                            else:
                                if(check_tacts(tact3, tact2) >= score_filter):
                                    add_tact(new_track, tact2)
                                else:
                                    break
                        except IndexError:
                            if(check_tacts(tact3, tact2) >= score_filter):
                                add_tact(new_track, tact2)
                            else:
                                break

                    if((len(singles[n].tracks)>0) and track_info(new_track)[0] == track_size):
                        n += 1
                    else:
                        del singles[n]
                if(mask % 100 == 0):
                    print("Track2: mask =", mask)
                if(n>0 and n % 10 == 0):
                    print("Track2: singles_size =", n)
                if(keyboard.is_pressed('esc')):
                    keyboard.release('esc')
                    break
                    
            del singles[n:len(singles)]
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

    print(single2.filename)
    print("single length ", single2.length)
    print("Beats:",beats(single2))

    singles = сrossoverSigles4(single1,single2,3)
    time.sleep(2)
    print("Итоговое количество синглов", len(singles))
    print("Для пропуска композиции нажмите на клавишу <esc>")
    single = None
    if (len(singles) > 0):
        single = singles[len(singles)//4*3]
        for msg in single.play():
            port.send(msg)
            if(keyboard.is_pressed('esc')):  # пропустить проигрование трека
                keyboard.release('esc')
                break
        single.save("winer_" + datetime.strftime(datetime.now(),
                                              "%Y-%m-%d %H.%M.%S") + ".mid")
    else:
        print("С такими параметрами компазиций нет!")
    print("Ожидание 'ESC'")
    time.sleep(3)
    keyboard.wait('esc')
    return
    
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
