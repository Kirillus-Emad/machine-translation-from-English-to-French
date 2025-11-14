import numpy as np
import pickle
from tensorflow.keras.models import load_model
import os

path=os.getcwd()
# Global variables
encoder_model = None
decoder_model = None
input_token_index = None
reverse_target_token_index = None
max_encoder_seq_length = None
max_decoder_seq_length = None
num_encoder_tokens = None
num_decoder_tokens = None
models_loaded = False

def load_models():
    """Load all necessary models and parameters"""
    global encoder_model, decoder_model, input_token_index, reverse_target_token_index
    global max_encoder_seq_length, max_decoder_seq_length, num_encoder_tokens, num_decoder_tokens, models_loaded
    
    try:
        # Load the models
        encoder_model = load_model(fr"{path}/encoder_model.h5")
        decoder_model = load_model(fr"{path}/decoder_model.h5")
        
        # Load token indices
        with open(fr"{path}/input_token_index.pkl", "rb") as f:
            input_token_index = pickle.load(f)
        
        with open(fr"{path}/reverse_target_token_index.pkl", "rb") as f:
            reverse_target_token_index = pickle.load(f)
        
        # Load sequence parameters
        with open(fr"{path}/seq_params.pkl", "rb") as f:
            params = pickle.load(f)
            max_encoder_seq_length = params["max_encoder_seq_length"]
            max_decoder_seq_length = params["max_decoder_seq_length"]
            num_encoder_tokens = params["num_encoder_tokens"]
            num_decoder_tokens = params["num_decoder_tokens"]
        
        models_loaded = True
        print("All models loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def encode_input_text(input_text):
    """Encode input text into one-hot format"""
    encoder_input_data = np.zeros(
        (1, max_encoder_seq_length, num_encoder_tokens),
        dtype="float32"
    )
    
    for t, char in enumerate(input_text):
        if char in input_token_index:
            encoder_input_data[0, t, input_token_index[char]] = 1.0
    
    # Pad the rest with spaces
    if t + 1 < max_encoder_seq_length:
        encoder_input_data[0, t + 1:, input_token_index[" "]] = 1.0
    
    return encoder_input_data

def decode_sequence(input_seq):
    """Decode sequence using the trained models"""
    # Encode the input as state vectors
    states_value = encoder_model.predict(input_seq, verbose=0)
    
    # Generate empty target sequence of length 1
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    # Populate the first character of target sequence with the start character
    target_seq[0, 0, input_token_index['\t']] = 1.0
    
    # Sampling loop for a batch of sequences
    stop_condition = False
    decoded_sentence = ''
    
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value, verbose=0
        )
        
        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_token_index[sampled_token_index]
        decoded_sentence += sampled_char
        
        # Exit condition: either hit max length or find stop character
        if (sampled_char == '\n' or 
            len(decoded_sentence) > max_decoder_seq_length):
            stop_condition = True
        
        # Update the target sequence (of length 1)
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sampled_token_index] = 1.0
        
        # Update states
        states_value = [h, c]
    
    return decoded_sentence

def translate_text(input_text):
    """Main translation function"""
    global models_loaded
    
    if not models_loaded:
        if not load_models():
            return "Error: Models failed to load"
    
    if not input_text.strip():
        return "Please enter some text to translate"
    
    try:
        # Encode the input text
        input_seq = encode_input_text(input_text)
        
        # Decode the sequence
        translated_text = decode_sequence(input_seq)
        
        # Remove the start and end tokens
        translated_text = translated_text.replace('\t', '').replace('\n', '')
        
        return translated_text.strip()
    
    except Exception as e:
        return f"Translation error: {str(e)}"