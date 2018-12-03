# -*- coding: utf-8 -*-

import mido
import random
import time
import os
from datetime import datetime


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
        flag = random.random()
        for j, (msg1, msg2) in enumerate(zip(track1, track2)):
            if(msg1 is None or msg2 is None):
                break
            if(flag):
                newTrack.append(msg1)
            else:
                newTrack.append(msg2)
            if(j >= numberOfNotes and msg1.type == 'note_on'):
                flag = not flag
    return newSingle



random.seed()

port = mido.open_output(mido.get_output_names()[0])
print("тестовый звук")
msg = mido.Message('note_on', note=60)
port.send(msg)

midi_files = [f for f in os.listdir() if f.endswith('.mid')]

single1 = mido.MidiFile('Пираты Карибского моря - piano.mid')
single2 = mido.MidiFile(
    'Red Alert — Soviet March Piano Version [MIDISTOCK.RU].mid')
newSingle = mido.MidiFile()

print("Компазиции")
print(single1.filename)
print(single2.filename)
#print("количество нот в блоке для скрещевания - ", numberOfNotes)
while (single1 is not None and single2 is not None):
    #numberOfNotes = int(
    #    input("Введите количество нот в блоке для скрещевания от 4 до 15: "))
    singles = []
    for i in range(0, 4):
        singles.append(сrossoverSigles(single1, single2, random.randint(4,15)))
    
    for i, single in enumerate(singles):
        print("single - #", i)
        #trackcount = int(single.tracks[0].length/10.0)
        #print("trakcount ", trackcount)
        time.sleep(3)
        
        for j, msg in enumerate(single.play()):
            port.send(msg)
            if j == 300:
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
for msg in single1.play():
    port.send(msg)
single1.save("winer_" + datetime.strftime(datetime.now(),
                                          "%Y-%m-%d %H.%M.%S") + ".mid")

# print(msg)

""" for track in single1.tracks:
    print('Track: {}'.format(track.name))
    # for msg in track:
    # print(msg)
    #    port.send(msg)
print(single2.filename)
for track in single2.tracks:
    print('Track: {}'.format(track.count)) """
