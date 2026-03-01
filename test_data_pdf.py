import os
import h5py
import numpy as np
from sheet_generator.apps import APP_DIR
from django_sopila.settings import BASE_DIR
from pydub import AudioSegment
from joblib import load
from sheet_generator.utils import ToneParser, make_prediction_file

def level_combined_recording(audio_file):
    # skip non stereo (uncombined) files
    if audio_file.channels <= 1:
        # skip whole folder
        return audio_file

    left, right = audio_file.split_to_mono()
    diff = abs(left.dBFS - right.dBFS)

    # compare left and right channel in dBFS
    get_gain = lambda l_ch, r_ch: 0 if l_ch > r_ch else diff

    left = left.apply_gain(get_gain(left.dBFS, right.dBFS))
    right = right.apply_gain(get_gain(right.dBFS, left.dBFS))

    audio_file = left.overlay(right)
    return audio_file

def normalize_amplitudes(amplitudes):
    # 50 db is like quiet restaurant
    # 10 * log10(x) = 50
    CUTOFF_THRESHOLD = 100000

    if amplitudes[amplitudes >= CUTOFF_THRESHOLD].any():
        amplitudes = abs(amplitudes) ** 2
        max_amplitude = amplitudes.max() if amplitudes.max() != 0 else 1.0
    else:
        # max threshold approx 20% of max value
        max_percentage = 0.2
        amplitudes = abs(amplitudes) * max_percentage
        max_amplitude = CUTOFF_THRESHOLD

    return amplitudes / max_amplitude

start = 0
# in miliseconds
step = 10
filename = "Mare_has_been_planting"
audio_file = AudioSegment.from_wav(os.path.join(BASE_DIR, filename + '.wav'))

# measured in miliseconds
duration = len(audio_file)
number_of_segments = int(duration / step)

print(f"Audio loaded for {filename}. Starting segmentation.")

all_norm_amplitudes = []
for i in range(0, number_of_segments):
    end = start + step
    audio_segment = audio_file[start:end]

    # one cut segment
    # level segment if needed
    audio_segment = level_combined_recording(audio_segment)
    fft = np.fft.fft(np.array(audio_segment.get_array_of_samples()))

    N = fft.size
    f = abs(np.fft.fftfreq(N) * audio_segment.frame_rate)
    norm_amplitudes = normalize_amplitudes(fft)

    all_norm_amplitudes.append(norm_amplitudes)

    # end of cut segment
    start += step

print("Ended segmentation.")

try:
    model_path = os.path.join(BASE_DIR, 'poly_rf_dft_900_gini_2_1_auto_80_False.joblib')
    rnd_clf = load(model_path)
except Exception as e:
    # Logs the error appropriately.
    print(f"Failed to load model from {model_path}: {e}")
    raise

print("Model loaded. Predicting...")
y_predicted = rnd_clf.predict(all_norm_amplitudes)

predicted_dir = os.path.join(APP_DIR, 'raw_predictions')
if not os.path.isdir(predicted_dir):
    print(f"Making a raw predictions directory: {predicted_dir}")
    os.makedirs(predicted_dir)

predicted_filename = os.path.join(predicted_dir, filename + '.hdf5')
print(f"Predictions saved to HDF5: {predicted_filename} frames.")

predicted_file = h5py.File(predicted_filename, 'w')
print(f"New raw predictions file: {predicted_filename}")

dt = h5py.special_dtype(vlen=str)
predicted_file.create_dataset(
    'predictions',
    data=y_predicted,
    dtype=dt
)

print(f"Predictions saved to HDF5: {len(y_predicted)} frames.")
predicted_file.close()

sheet = ToneParser(filename)
sheet.parse_tones()

try:
    print("Prediction successfully started.")
    make_prediction_file(filename)
    print("Prediction successfully created.")
    
    sheet = ToneParser(filename)
    sheet.parse_tones()
    
    pdf_dir = os.path.join(APP_DIR, 'pdf')
    if not os.path.isdir(pdf_dir):
        print(f"Making a pdf directory: {pdf_dir}")
        os.makedirs(pdf_dir)

    pdf_path = os.path.join(APP_DIR, 'pdf', filename + '.pdf')
    if not os.path.exists(pdf_path):
        print("PDF generation failed.")

except Exception as e:
    print(f"Error processing sheet: {str(e)}")
    print(f"Internal Error: {e}")