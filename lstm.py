import numpy as np
from numpy import newaxis
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential

def gen_data(data, seq_len, test_len, y_len=1, normalise_window=True):
    sequence_length = seq_len + y_len
    result = []
    for index in range(len(data) - sequence_length + 1):
        result.append(data[index: index + sequence_length])

    if normalise_window:
        result = normalise_windows(result)

    result = np.array(result)
    print('Window Data Shape: ', result.shape)

    row = len(result) - test_len
    train = result[:row,:]
    test = result[row:,:]
    np.random.shuffle(train)
    x_train = train[:,:seq_len]
    y_train = train[:,seq_len:, 0]
    x_test = test[:,:seq_len]
    y_test = test[:,seq_len:, 0]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], x_train.shape[2]))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], x_train.shape[2]))

    return [x_train, y_train, x_test, y_test]

# def normalise_windows(window_data):
#     normalised_data = []
#     for window in window_data:
#         normalised_window = [((float(p) / float(window[0])) - 1) for p in window]
#         normalised_data.append(normalised_window)
#     return normalised_data

def normalise_windows(window_data):
    normalised_data = []
    for window in window_data:
        norm_window = np.zeros_like(window)
        for i in range(window.shape[1]):
            # mean = np.mean(window[:, i])
            # std = np.std(window[:, i])
            # norm_window[:, i] = (window[:, i] - mean) / std
            norm_window[:, i] = window[:, i] / window[0, i]
        normalised_data.append(norm_window)
    return normalised_data

def build_model(layers):
    model = Sequential()
    model.add(LSTM(layers[1],
                    input_shape = (layers[1], layers[0]),
                    return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(layers[2],return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(layers[3]))
    model.add(Activation("linear"))

    model.compile(loss="mse", optimizer='adam')
    return model

def predict_point_by_point(model, data):
    predicted = model.predict(data)
    predicted = np.reshape(predicted, (predicted.size,))
    return predicted

def predict_sequence_full(model, data, window_size):
    curr_frame = data[0]
    predicted = []
    for i in range(len(data)):
        predicted.append(model.predict(curr_frame[newaxis,:,:])[0,0])
        curr_frame = curr_frame[1:]
        curr_frame = np.insert(curr_frame, [window_size-1], predicted[-1], axis=0)
    return predicted

def predict_sequences_multiple(model, data, window_size, prediction_len):
    prediction_seqs = []
    for i in range(int(len(data)/prediction_len)):
        curr_frame = data[i*prediction_len]
        predicted = []
        for j in range(prediction_len):
            predicted.append(model.predict(curr_frame[newaxis,:,:])[0,0])
            curr_frame = curr_frame[1:]
            curr_frame = np.insert(curr_frame, [window_size-1], predicted[-1], axis=0)
        prediction_seqs.append(predicted)
    return prediction_seqs
