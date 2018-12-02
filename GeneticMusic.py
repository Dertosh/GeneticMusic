# -*- coding: utf-8 -*-

import mido
import random
import time
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
            if(msg1 is None or msg2 is None):
                break
            if(flag):
                newTrack.append(msg1)
            else:
                newTrack.append(msg2)
            if(j >= notesSwitcher and msg1.type == 'note_on'):
                track1, track2 = track2, track1
                notesSwitcher = j + numberOfNotes
                flag = not flag
    return newSingle


random.seed()
numberOfNotes = random.randint(10, 20)

port = mido.open_output()
print("тестовый звук")
msg = mido.Message('note_on', note=60)
port.send(msg)

single1 = mido.MidiFile('Пираты Карибского моря - piano.mid')
single2 = mido.MidiFile('Fringe - Title Sequence.mid')
newSingle = mido.MidiFile()
newSingle.save("newSingle.mid")

print("Компазиции")
print(single1.filename)
print(single2.filename)
print("количество нот в блоке для скрещевания - ", numberOfNotes)
while (single1 is not None and single2 is not None):
    singles = []
    for i in range(0, 5):
        singles.append(сrossoverSigles(single1, single2, numberOfNotes))

    for i, single in enumerate(singles):
        print("single - #", i)
        time.sleep(5)
        for msg in single.play():
            port.send(msg)
    qFlaf = True
    while qFlaf:
        print("Выбрать победителя? (Д/Н)")
        s = input().lower()
        if(s == 'д' or s == 'y'):
            print("Выберете композицию и напишите номер")
            single1 = singles[int(input())]
            single2 = None
            break
        print("Выберете 2 композиции и напишите их номер через пробел")
        try:
            (selectSingle1, selectSingle2) = list(map(int, input().split()))
        except ValueError:
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
