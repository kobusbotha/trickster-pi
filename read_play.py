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

sounds = [0 for j in range(0,16)]
stubbed_data = [0, 1, 0, 1];
try: 
	stubbed = False;
	ser = Serial('/dev/ttyACM0', 9600)
except serial.serialutil.SerialException:
	stubbed = True;
	
data = [0 for j in range(0,4)]

#Initialize Pygame
def init():
	def sound_init():
		for i in range(0,16):
			sounds[i] = pygame.mixer.Sound("/home/pi/trickster-pi/wav" + str(i) + ".wav")
	pygame.init()
	pygame.mixer.init()
	sound_init()


def playall():
	global data
	if stubbed:
		data = stubbed_data
	while 1:
		for i in range(0, 4):
			if data[i] != 0:
				sounds[data[i]].play()
			time.sleep(0.4)

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
	while True:
		frame = (yield)
		print 'Got frame:', frame.encode('hex')
		print 'Length:', len(frame)
		if len(frame) == 4:
			for i in range(0,4):
				data[i]=int(frame[i].encode('hex')[1])
				print '%s : %s' % (i,data[i])
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
