import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # it remove all the tensorflow warnings

import pickle
import tensorflow as tf
from generate_note import processing
from music21 import instrument, note, chord, stream

""" Load the nodes """
with open('notes', 'rb') as handle:
    notes = pickle.load(handle)

# getting the pitches and vocabulary size
pitches = sorted(set(notes))
vocab = len(set(notes))

''' Process the test data '''
arc = processing(notes, vocab, features=100)

''' Generate test data sequence for prediction '''
test_inputs = arc.prepare_test_sequences(pitches)

''' Load the model '''
model = tf.keras.models.load_model('generator/')

''' Do Prediction '''
output_notes = arc.notes_prediction(model, test_inputs, pitches, num_notes=500)

''' Midi File '''
# convert the predicted output into midi audio file
offset = 0
output = []

# create note and chord objects one by one
# based on the values generated by the model
for item in output_notes:
    # for chord in item
    if ('.' in item) or item.isdigit():
        # split the notes from (.) mark
        notes_in_chord = item.split('.')
        
        # collect every note from each instrumental sequence
        notes = []
        for start_note in notes_in_chord:
            start_note = note.Note(int(start_note))
            start_note.storedInstrument = instrument.Piano()
            notes.append(start_note)
        
        # store the final chord to the output
        final_chord = chord.Chord(notes)
        final_chord.offset = offset
        output.append(final_chord)
        
    # for note in item
    else:
        # store the final note to the output
        final_note = note.Note(item)
        final_note.offset = offset
        final_note.storedInstrument = instrument.Piano()
        output.append(final_note)

    # increase offset to prevent stacking
    offset += 0.5

# form the stream object
midi_stream = stream.Stream(output)

# save the midi file
midi_stream.write('midi', fp='test_audio.mid')