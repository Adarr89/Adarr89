from scipy.io import wavfile
import scipy.io
from numpy import fft
import numpy as np

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def findRMS(item):
    value = np.mean(item**2)
    if value < 0:
        exit(1)
    return np.sqrt(value)

def spectrum(chunk, samplerate):
	N = len(chunk)
	yf = fft.fft(chunk)
	xf = np.fft.fftfreq(N, 1/samplerate)
	xf = xf[:N//2]
	yf = np.abs(yf[:N//2])
	
	return xf, yf


def findFundamentalFrequency(xf, yf, threshold=0.1):
    if len(yf.shape) > 1:
        yf = np.mean(yf, axis=1)

    yf[0] = 0
    max_amplitude = np.max(yf)
    significant_amplitude_threshold = max_amplitude * threshold

    for i in range(1, len(yf)):
        if yf[i] > significant_amplitude_threshold:
            fundamental_freq = xf[i]
            break
    else:
        fundamental_freq = None  
    
    return fundamental_freq



def frequency_to_midi(frequency):
    if frequency <= 0:
        return None  
    
    midi_number = 69 + 12 * np.log2(frequency / 440.0)
    
    return round(midi_number)

def midi_to_pitch(midi_number):
    if midi_number is None:
        return None

    note_name = NOTE_NAMES[midi_number % 12]
    octave = (midi_number // 12) - 1  
    
    return f"{note_name}{octave}"

def frequency_to_pitch(frequency):
    midi_number = frequency_to_midi(frequency)
    pitch_name = midi_to_pitch(midi_number)
    
    return pitch_name



samplerate, data = wavfile.read('AudioSample.wav', 'rb')
data = data.astype(float)
chunkLength = samplerate/1000 * 38
chunkStep = int(chunkLength*0.19)
listRMS = []
RMStimes = []
 
for i in range(0, data.shape[0], chunkStep):
	upper = int(i+chunkLength)
	tempVar = abs(data[i:upper, 0])
	rmsVar = findRMS(tempVar)
	listRMS.append(rmsVar)
	RMStimes.append(i/samplerate)





notes = []

for j in range(4, len(listRMS)-1):
#	if listRMS[j] > listRMS[j-4]+380 and listRMS[j] > listRMS[j+1]:
		if len(notes) == 0:
			notes.append(j * chunkStep)
		elif j * chunkStep > notes[-1]+0.38*samplerate:
			notes.append(j * chunkStep)


outputs = []
for k in range(0, len(notes)):
      if k < len(notes)-1:
        tempVar = data[notes[k]:notes[k+1]].astype(np.int16)
        xf, yf = spectrum(tempVar, samplerate)
        fundamental = findFundamentalFrequency(xf, yf)
        tempNote = frequency_to_pitch(fundamental)
        wavfile.write("Note%i.wav"%k, samplerate, tempVar)
        outputs.append(tempNote)
      else:
        tempVar = data[notes[k]:].astype(np.int16)
        xf, yf = spectrum(tempVar, samplerate)
        fundamental = findFundamentalFrequency(xf, yf)
        tempNote = frequency_to_pitch(fundamental)
        wavfile.write("Note%i.wav"%k, samplerate, tempVar)
        outputs.append(tempNote)

for element in outputs:
     print(element)