import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.utils import to_categorical

# Data (replace this with reading from a file if necessary)
with open("data.txt", "r") as file:
    data = file.read().splitlines()

# Step 1: Map characters to integers
unique_chars = sorted(set("".join(data)))  # Get all unique characters
char_to_int = {char: idx for idx, char in enumerate(unique_chars)}
int_to_char = {idx: char for char, idx in char_to_int.items()}

# Step 2: Convert dataset to numerical representation
numerical_data = [[char_to_int[char] for char in row] for row in data]

# Step 3: Prepare training data
sequence_length = 5  # Number of characters in each input sequence
X, y = [], []

for row in numerical_data:
    for i in range(len(row) - sequence_length):
        X.append(row[i:i + sequence_length])  # Input sequence
        y.append(row[i + sequence_length])   # Next character (label)

X = np.array(X)
y = np.array(y)

# Convert labels to one-hot encoding
y_onehot = to_categorical(y, num_classes=len(unique_chars))

# Step 4: Build the model
model = Sequential([
    Embedding(input_dim=len(unique_chars), output_dim=50, input_length=sequence_length),
    LSTM(128, return_sequences=False),
    Dense(len(unique_chars), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Step 5: Train the model
model.fit(X, y_onehot, epochs=20, batch_size=64)

# Step 6: Predict the next character
def predict_next_character(input_sequence, model):
    input_sequence = np.array([[char_to_int[char] for char in input_sequence]])
    prediction = model.predict(input_sequence, verbose=0)
    predicted_char = int_to_char[np.argmax(prediction)]
    return predicted_char

# Step 7: Generate a longer pattern
def generate_pattern(start_sequence, model, length=50):
    current_sequence = start_sequence
    generated_pattern = start_sequence

    for _ in range(length):
        next_char = predict_next_character(current_sequence, model)
        generated_pattern += next_char
        current_sequence = current_sequence[1:] + next_char  # Shift sequence

    return generated_pattern

# Test the model
start_sequence = "BFBFF"  # Example starting sequence
generated = generate_pattern(start_sequence, model, length=50)
print("Generated Pattern:", generated)

# Save the model
model.save("pattern_model.h5")
print("Model saved as 'pattern_model.h5'")
