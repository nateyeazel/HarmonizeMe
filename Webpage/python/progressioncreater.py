
#Alexander Fang; 3/7/2016

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

#Takes in a melody and chosen progression by user and returns the realized form of the progression.
#example: with the melody [1, 2, 3, 2, 1, 7, 1]
# You have picked this progression:
# ['I', 'V', 'I', 'ii6', 'IV', 'V', 'I']
# Here is your realized progression: 
# [[1, 3, 1], [2, 7, 5], [3, 5, 1], [2, 6, 4], [1, 6, 4], [7, 2, 5], [1, 3, 1]]

def harmonize(melody, progression):
	realized = []
	for pitch, chord_choice in zip(melody, progression):
		realized.append(fill_chord(pitch, chord_choice))
	print 'Here is your realized progression: '
	print realized
	return realized




#running
ex_melody = [1, 2, 3, 2, 1, 7, 1]
ex_prog = choose_chords(ex_melody)
harmonize(ex_melody, ex_prog)