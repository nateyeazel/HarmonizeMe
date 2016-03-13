
#Alexander Fang; 3/7/2016

import sys
from aubio import source, pitch, freqtomidi, onset
# from __future__ import print_function

import argparse
import librosa
import numpy

#gets midi number of the pitch
#this file should only hold one note
def determine_pitch(pitchfile):
	notes = delete_zeros(getpitches(pitchfile, 44100))
	midi_num = numpy.around(numpy.median(notes))
	#print notes
	#print midi_num
	return midi_num #midi_num is the tonic

#given a pitch in midi, return the sd of it in relation to the tonic in midi
def pitch_in_sd(pitch, tonic):
	half_steps_above = (pitch - tonic) % 12
	if half_steps_above == 0:
		return 1
	elif half_steps_above == 2:
		return 2
	elif half_steps_above == 4:
		return 3
	elif half_steps_above == 5:
		return 4
	elif half_steps_above == 7:
		return 5
	elif half_steps_above == 9:
		return 6
	elif half_steps_above == 11:
		return 7

#given a pitch in sd, returns how many halfsteps above the tonic is
def sd_to_halfstepsabove(sd):
	if sd == 1:
		return 0
	elif sd == 2:
		return 2
	elif sd == 3:
		return 4
	elif sd == 4:
		return 5
	elif sd == 5:
		return 7
	elif sd == 6:
		return 9
	elif sd == 7:
		return 11

#asdf
#given chord, sets mid and bass to halfstep distance away from melody
def sd_to_halfsteps(chord):
	hs_above_chord = []
	for pitch in chord:
		hs_above_chord.append(sd_to_halfstepsabove(pitch))

	hs_chord = []
	top = hs_above_chord[0]
	mid = hs_above_chord[1]
	bass = hs_above_chord[2]

	#top note
	hs_chord.append(0)

	#middle note
	mid_hs = mid - top
	#if sd of mid is larger than top
	if mid > top:
		hs_chord.append(mid_hs - 12)
	else:
		hs_chord.append(mid_hs)

	#bass note
	hs_chord.append(bass - top - 12)
	return hs_chord


def delete_zeros(alist):
	newlist = []
	for element in alist:
		if element != 0.0:
			newlist.append(element)
	return newlist

def getpitches(filename, samplerate):

	#downsample = 1
	#samplerate = 44100 / downsample	
	win_s = 4096 / downsample # fft size
	hop_s = 512  / downsample # hop size

	s = source(filename, samplerate, hop_s)
	samplerate = s.samplerate

	tolerance = 0.8

	pitch_o = pitch("yin", win_s, hop_s, samplerate)
	pitch_o.set_unit("midi")
	pitch_o.set_tolerance(tolerance)

	o = onset("default", win_s, hop_s, samplerate)
	onsets = []

	pitches = []
	confidences = []
	number = 0
	# total number of frames read
	total_frames = 0
	while True:
	    samples, read = s()
	    pitch1 = pitch_o(samples)[0]
	    #pitch = int(round(pitch))
	    confidence = pitch_o.get_confidence()
	    if o(samples):
        	# print "%f" % o.get_last_s()
        	onsets.append(o.get_last())
	    #if confidence < 0.8: pitch = 0.
	    #print "%f %f %f" % (total_frames / float(samplerate), pitch, confidence)
	    pitches += [pitch1]
	    confidences += [confidence]
	    total_frames += read
	    number = number + 1
	    if read < hop_s: break

	if 0: sys.exit(0)

	'''
	print onsets
	print pitches
	print confidences
	print number
	'''

	return pitches

# 


def adjust_tuning(input_file, output_file):
    '''Load audio, estimate tuning, apply pitch correction, and save.'''
    print('Loading ', input_file)
    y, sr = librosa.load(input_file)

    print('Separating harmonic component ... ')
    y_harm = librosa.effects.harmonic(y)

    print('Estimating tuning ... ')
    # Just track the pitches associated with high magnitude
    tuning = librosa.estimate_tuning(y=y_harm, sr=sr)

    print('{:+0.2f} cents'.format(100 * tuning))
    print('Applying pitch-correction of {:+0.2f} cents'.format(-100 * tuning))
    y_tuned = librosa.effects.pitch_shift(y, sr, -tuning)

    print('Saving tuned audio to: ', output_file)
    librosa.output.write_wav(output_file, y_tuned, sr)


def process_arguments(args):
    '''Argparse function to get the program parameters'''

    parser = argparse.ArgumentParser(description='Tuning adjustment example')

    parser.add_argument('input_file',
                        action='store',
                        help='path to the input file (wav, mp3, etc)')

    parser.add_argument('output_file',
                        action='store',
                        help='path to store the output wav')

    return vars(parser.parse_args(args))



if len(sys.argv) < 2:
    print "Usage: %s <inputfilename1>  <inputfilename2> [samplerate]" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]
melodyfilename = sys.argv[2]
downsample = 1
samplerate = 44100 / downsample
if len( sys.argv ) > 3: samplerate = int(sys.argv[3])
# adjust_tuning(input_file, output_file)
getpitches(filename, samplerate)

'''
GETTING TONIC AND EXPITCH
'''

tonic = determine_pitch(filename)
expitch = determine_pitch(melodyfilename)
print tonic
print expitch

# if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

# if __name__ == '__main__':
#     # Run the beat tracker
#     adjust_tuning(params['input_file'], params['output_file'])






#sd = scale_degree
#chord: [top voice, middle voice, bass]

#Takes in a melody, which is an array of pitches, written in scale degrees.
#Returns suggestions for possible chords. Each array in 'options' contains chords that the user can pick for the corresponding pitch in the melody.
#example: when melody is [1, 2, 3, 2, 1, 7, 1], it returns [['I', 'IV'], ['ii6', 'V'], ['I'], ['ii6', 'V'], ['I', 'IV'], ['V'], ['I', 'IV']]


def possible_chords(melody):
	options = []
	for sd in melody:
		assert (sd >= 1 and sd <= 7), "scale degree must be integer from 1 to 7"
		if sd == 1:
			poss_chords = []
			poss_chords.append('I')
			poss_chords.append('IV')
		elif sd == 2:
			poss_chords = []	
			poss_chords.append('ii6')
			poss_chords.append('V')
		elif sd == 3:
			poss_chords = []
			poss_chords.append('I')
		elif sd == 4 or sd == 6:
			poss_chords = []
			poss_chords.append('ii6')
			poss_chords.append('IV')
		elif sd == 5:
			poss_chords = []
			poss_chords.append('I')
			poss_chords.append('V')
		elif sd == 7:
			poss_chords = []
			poss_chords.append('V')
		options.append(poss_chords)
	return options

#Calls possible_chords from given melody, and asks user to choose a chord for each pitch in the melody.
#example:
# Choices: I or IV
# Please enter a chord: I
# Choices: ii6 or V
# Please enter a chord: V
# Choice: I
# Please enter a chord: I
# Choices: ii6 or V
# Please enter a chord: ii6
# Choices: I or IV
# Please enter a chord: IV
# Choice: V
# Please enter a chord: V
# Choices: I or IV
# Please enter a chord: I
# You have picked this progression:
# ['I', 'V', 'I', 'ii6', 'IV', 'V', 'I']
def choose_chords(melody):
	progression = []
	chord_options = possible_chords(melody)
	for options in chord_options:
		if len(options) == 1:
			print 'Choice: ' + options[0]
			choice = str(raw_input('Please enter a chord: '))
			progression.append(choice)
		elif len(options) == 2:
			print 'Choices: ' + options[0] + ' or ' + options[1]
			choice = str(raw_input('Please enter a chord: '))
			progression.append(choice)
	print 'You have picked this progression:'
	print progression
	return progression


#Returns the scale degree of the middle voice, given the pitch of the melody and the bass.
#When sd and chord don't imply the same pitch, it returns the only remaining pitch.
#When sd and chord imply the same pitch, it returns the third above the bass.
def mid_voice(sd, chord):
	if sd == 1:
		if chord == 'I':
			return 3
		elif chord == 'IV':
			return 6
	elif sd == 2:
		if chord == 'ii6':
			return 6
		elif chord == 'V':
			return 7
	elif sd == 3:
		return 5
	#do we want to add a V7? sd == 4 only gives us one option..
	elif sd == 4:
		return 6
	elif sd == 5:
		if chord == 'I':
			return 3
		elif chord == 'V':
			return 7
	elif sd == 6:
		if chord == 'ii6':
			return 2
		elif chord == 'IV':
			return 1
	elif sd == 7:
		return 2

#Returns the scale degree of the bass voice, given the chord.
def bass_voice(chord):
	if chord == 'I':
		return 1
	elif chord == 'ii6' or chord == 'IV':
		return 4
	elif chord == 'V':
		return 5

#Returns a filled chord, given the sd of a melody and the chord.
#example of chord: array of size 3, each index being a scale degree = [1, 3, 5]
#[melody, middle voice, bass]
def fill_chord(sd, chord):
	filled = []
	filled.append(sd)
	filled.append(mid_voice(sd, chord))
	filled.append(bass_voice(chord))
	return filled


#returns the progression but with pitches in halfsteps above tonic
#returns [[0, 4, 0], [2, 11, 7], [4, 7, 0], [2, 9, 5], [0, 9, 5], [11, 2, 7], [0, 4, 0]]
#when given [[1, 3, 1], [2, 7, 5], [3, 5, 1], [2, 6, 4], [1, 6, 4], [7, 2, 5], [1, 3, 1]]
def progression_halfsteps(progression):
	prog_halfstep = []
	for chord in progression:
		chrd = []
		for pitch in chord:
			chrd.append(sd_to_halfstepsabove(pitch))
		prog_halfstep.append(chrd)
	return prog_halfstep

#returns the progression in chords with how much to shift from the melodic note
#returns [[0, -8, -12], [0, -3, -7], [0, -9, -16], [0, -5, -9], [0, -3, -7], [0, -9, -16], [0, -8, -12]]
#when given [[1, 3, 1], [2, 7, 5], [3, 5, 1], [2, 6, 4], [1, 6, 4], [7, 2, 5], [1, 3, 1]]
def progression_hs_away(progression):
	prog_hsaway = []
	for chord in progression:
		prog_hsaway.append(sd_to_halfsteps(chord))
	return prog_hsaway


#Takes in a melody and chosen progression by user and returns the realized form of the progression.
#example: with the melody [1, 2, 3, 2, 1, 7, 1]
# You have picked this progression:
# ['I', 'V', 'I', 'ii6', 'IV', 'V', 'I']
# Here is your realized progression: 
# [[1, 3, 1], [2, 7, 5], [3, 5, 1], [2, 6, 4], [1, 6, 4], [7, 2, 5], [1, 3, 1]]
def harmonize(melody, progression, tonic):
	realized = []
	for pitch, chord_choice in zip(melody, progression):
		realized.append(fill_chord(pitch, chord_choice))
	print 'Here is your realized progression: '
	print realized
	print 'Here is your realized progression in halfsteps away from melodic note: '
	prog_hs = progression_hs_away(realized)
	print prog_hs

	'''
	making the new pitches, assuming this melody is only one pitch long
	'''
	sounding_pitch_in_melody, sr = librosa.core.load(melodyfilename, sr=44100)
	almost_sounding_chord = []
	#top note
	almost_sounding_chord.append(sounding_pitch_in_melody)

	#middle note
	almost_sounding_chord.append(librosa.effects.pitch_shift(sounding_pitch_in_melody, sr,
		n_steps = prog_hs[0][1]))

	#bottom note
	almost_sounding_chord.append(librosa.effects.pitch_shift(sounding_pitch_in_melody, sr,
		n_steps = prog_hs[0][2]))
	outputname = str(raw_input('Please enter a file name for your output file (include .wav): '))

	sounding_chord = almost_sounding_chord[0] + almost_sounding_chord[1] + almost_sounding_chord[2]
	librosa.output.write_wav(outputname, sounding_chord, sr)

#fdsa
	return realized
'''
tonic, sr = librosa.core.load(filename, sr=44100)
librosa.output.write_wav('c#554.wav', librosa.effects.pitch_shift(tonic, sr,
	n_steps = 4), sr)
librosa.output.write_wav('d587.wav', librosa.effects.pitch_shift(tonic, sr,
	n_steps = 5), sr)
librosa.output.write_wav('e659.wav', librosa.effects.pitch_shift(tonic, sr,
	n_steps = 7), sr)
librosa.output.write_wav('f#740.wav', librosa.effects.pitch_shift(tonic, sr,
	n_steps = 9), sr)
librosa.output.write_wav('g#831.wav', librosa.effects.pitch_shift(tonic, sr,
	n_steps = 11), sr)
'''

#has this above:
#tonic = determine_pitch(filename)
#expitch = determine_pitch(melodyfilename)
#

#print pitch_in_sd(expitch, tonic)


#running example
ex1_melody = []
ex1_melody.append(pitch_in_sd(expitch, tonic))
ex1_prog = choose_chords(ex1_melody)
harmonize(ex1_melody, ex1_prog, tonic)




'''
#running
ex_melody = [1, 2, 3, 2, 1, 7, 1]
ex_prog = choose_chords(ex_melody)
harmonize(ex_melody, ex_prog)
'''