#!/usr/bin/python
# -*- coding: utf-8 -*-

from serial import Serial
import pygame
from pygame.locals import *
import pygame.mixer
import sys
import array
import time
import threading
import serial
import os
import os.path

sounds = {}
wave_set = 0
stubbed_data = [0, 1, 0, 1, 1];
wav_delay = 0.8
try: 
	stubbed = False;
	ser = Serial('/dev/ttyACM0', 9600)
except serial.serialutil.SerialException:
	stubbed = True;
	
data = [0 for j in range(0,5)]

#Initialize Pygame
def init():
	def sound_init():
		k = 0
		path = "/home/pi/trickster-pi/wav/"
		for x in os.listdir(path):
			if os.path.isdir(os.path.join(path, x)):
				waves = []
				for i in range(4):
					print os.path.join(path, x,  str(i) + ".wav")	
					waves.append(pygame.mixer.Sound(os.path.join(path, x,  str(i) + ".wav")))
				sounds[k] = waves
				k += 1
		print sounds

	pygame.init()
	pygame.mixer.init()
	sound_init()


def playall():
	global data
	global wave_set
	if stubbed:
		data = stubbed_data
	while 1:
		command = data[4]
		print "cmd", command, "set", wave_set
		if command != 1:
			for i in range(0, 4):
				if data[i] != 0:
					binary = "{0:b}".format(data[i]).rjust(4,"0")
					print data[i], binary
					if binary[0] == '1':
						sounds[wave_set][0].play()
                                        if binary[1] == '1':
                                                sounds[wave_set][1].play()
                                        if binary[2] == '1':
                                                sounds[wave_set][2].play()
                                        if binary[3] == '1':
                                                sounds[wave_set][3].play()
				time.sleep(sounds[wave_set][0].get_length()/2)
	
def coroutine(func):
    def start(*args,**kwargs):
	cr = func(*args,**kwargs)
	cr.next()
	return cr
    return start


@coroutine
def unwrap_protocol(header='\x61',
		    footer='\x62',
		    dle='\xAB',
		    after_dle_func=lambda x: x,
		    target=None):
    """ Simplified framing (protocol unwrapping)
	co-routine.
    """
    # Outer loop looking for a frame header
    #
    while True:
	byte = (yield)
	frame = ''

	if byte == header:
	    # Capture the full frame
	    #
	    while True:
		byte = (yield)
		if byte == footer:
		    target.send(frame)
		    break
		elif byte == dle:
		    byte = (yield)
		    frame += after_dle_func(byte)
		else:
		    frame += byte
	else:
		frame = ''

@coroutine
def frame_receiver():
	global data
	global wave_set
	while True:
		frame = (yield)
		print 'Got frame:', frame.encode('hex')
		print 'Length:', len(frame)
		if len(frame) == 5:
			for i in range(0,5):
				data[i]=int(frame[i].encode('hex')[1], 16)
				print '%s : %s' % (i,data[i])
			if data[4] == 2:
                        	wave_set = (wave_set + 1) % len(sounds)
                        elif data[4] == 3:
                                wave_set = (wave_set - 1) % len(sounds)
		else:
			print "Wrong Length"

unwrapper = unwrap_protocol(target=frame_receiver())

def main():
	init()
	threading.Thread(target=playall).start()
	while 1:
		if not stubbed:
			x=ser.read()
			unwrapper.send(x)


if __name__ == "__main__": main()
