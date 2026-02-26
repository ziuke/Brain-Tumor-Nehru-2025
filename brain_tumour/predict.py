"""
Prediction Module for Brain Tumor Classification
Handles prediction on single images or uploaded images
"""

import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image

CLASS_TYPES = ["glioma", "meningioma", "notumor", "pituitary"]

def load_model(model_path):
    return tf.keras.models.load_model(model_path)

def get_class_indices_from_directory(train_dir):
    return {class_name: idx for idx, class_name in enumerate(sorted(CLASS_TYPES))}


def preprocess_image(image_path, target_size=(150, 150)):
    """
    Preprocess a single image for prediction.
    
    Args:
        image_path (str): Path to the image file
        target_size (tuple): Target size for resizing (height, width)
        
    Returns:
        numpy.ndarray: Preprocessed image array ready for prediction
    """
    # Load and resize image
    img = Image.open(image_path)
    img = img.convert('RGB')  # Ensure RGB format
    img = img.resize(target_size)
    
    # Convert to array and normalize
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalize to [0, 1]
    
    # Expand dimensions to match model input shape (batch_size, height, width, channels)
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def load_class_indices(model_path, train_dir=None):
    """
    Load class indices from saved JSON file or directory.
    
    Args:
        model_path (str): Path to model file
        train_dir (str, optional): Path to training directory to get class indices
        
    Returns:
        dict: Class indices dictionary
    """
    # Try to load from JSON file (saved during training)
    class_indices_path = model_path.replace('.h5', '_class_indices.json')
    if os.path.exists(class_indices_path):
        with open(class_indices_path, 'r') as f:
            return json.load(f)
    
    # If not found, get from directory (alphabetical order like ImageDataGenerator)
    if train_dir and os.path.exists(train_dir):
        return get_class_indices_from_directory(train_dir)
    
    # Fallback to default alphabetical order
    return {class_name: idx for idx, class_name in enumerate(sorted(CLASS_TYPES))}


def predict_image(model, image_path, class_indices=None, target_size=(150, 150), return_probabilities=False):
    """
    Predict tumor class for a single image.
    
    Args:
        model: Trained Keras model
        image_path (str): Path to the image file
        class_indices (dict, optional): Dictionary mapping class names to indices
        target_size (tuple): Target size for image preprocessing
        return_probabilities (bool): Whether to return all class probabilities
        
    Returns:
        dict: Prediction results with class name, confidence, and optionally all probabilities
    """
    try:
        # Preprocess image
        img_array = preprocess_image(image_path, target_size)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        
        # Get predicted class index
        predicted_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_index])
        
        # Map index to class name
        if class_indices is None:
            # Default to alphabetical order (matches ImageDataGenerator)
            class_indices_list = sorted(CLASS_TYPES)
        else:
            # Create reverse mapping from indices to class names
            class_indices_list = [None] * len(class_indices)
            for class_name, idx in class_indices.items():
                class_indices_list[idx] = class_name
        
        predicted_class = class_indices_list[predicted_index]
        
        result = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'predicted_class_index': int(predicted_index)
        }
        
        if return_probabilities:
            # Return probabilities for all classes
            all_probs = {}
            for i, class_name in enumerate(class_indices_list):
                all_probs[class_name] = float(predictions[0][i])
            result['all_probabilities'] = all_probs
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'predicted_class': None,
            'confidence': 0.0
        }


def predict_batch(model, image_paths, class_indices=None, target_size=(150, 150)):
    """
    Predict tumor classes for multiple images.
    
    Args:
        model: Trained Keras model
        image_paths (list): List of paths to image files
        class_indices (dict, optional): Dictionary mapping class names to indices
        target_size (tuple): Target size for image preprocessing
        
    Returns:
        list: List of prediction results for each image
    """
    results = []
    for image_path in image_paths:
        result = predict_image(model, image_path, class_indices, target_size)
        result['image_path'] = image_path
        results.append(result)
    
    return results


def predict_from_upload(model_path, image_path, class_indices=None, train_dir=None):
    """
    Predict tumor class for an uploaded image file.
    
    Args:
        model_path (str): Path to saved model file
        image_path (str): Path to uploaded image file
        class_indices (dict, optional): Dictionary mapping class names to indices
        train_dir (str, optional): Path to training directory (used to get class indices if not saved)
        
    Returns:
        dict: Prediction results
    """
    # Load model
    try:
        model = load_model(model_path)
    except Exception as e:
        return {
            'error': f"Failed to load model: {str(e)}",
            'predicted_class': None,
            'confidence': 0.0
        }
    
    # Check if image exists
    if not os.path.exists(image_path):
        return {
            'error': f"Image file not found: {image_path}",
            'predicted_class': None,
            'confidence': 0.0
        }
    
    # Load class indices if not provided
    if class_indices is None:
        class_indices = load_class_indices(model_path, train_dir)
        print(f"Loaded class indices: {class_indices}")
    
    # Make prediction
    result = predict_image(model, image_path, class_indices, return_probabilities=True)
    
    return result


def format_prediction_result(result):
    """
    Format prediction result as a readable string.
    
    Args:
        result (dict): Prediction result dictionary
        
    Returns:
        str: Formatted string with prediction details
    """
    if 'error' in result:
        return f"Error: {result['error']}"
    
    output = f"Predicted Class: {result['predicted_class'].title()}\n"
    output += f"Confidence: {result['confidence']:.2%}\n"
    
    if 'all_probabilities' in result:
        output += "\nAll Class Probabilities:\n"
        for class_name, prob in result['all_probabilities'].items():
            output += f"  {class_name.title()}: {prob:.2%}\n"
    
    return output


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python predict.py <model_path> <image_path> [train_dir]")
        print("\nExample:")
        print("  python predict.py models/brain_tumor_model.h5 test_image.jpg")
        print("  python predict.py models/brain_tumor_model.h5 test_image.jpg D:/brain_tumour/archive/Training")
        sys.exit(1)
    
    model_path = sys.argv[1]
    image_path = sys.argv[2]
    train_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("="*60)
    print("BRAIN TUMOR CLASSIFICATION - PREDICTION")
    print("="*60)
    print(f"\nModel: {model_path}")
    print(f"Image: {image_path}\n")
    
    result = predict_from_upload(model_path, image_path, train_dir=train_dir)
    
    print(format_prediction_result(result))
    
    # Example: Predict multiple images
    # image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    # model = load_model(model_path)
    # results = predict_batch(model, image_paths)
    # for result in results:
    #     print(f"\n{result['image_path']}:")
    #     print(format_prediction_result(result))

