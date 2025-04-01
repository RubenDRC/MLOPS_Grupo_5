import tensorflow as tf
import tensorflow_transform as tft

def preprocessing_fn(inputs):
    """Función de preprocesamiento para normalizar características numéricas."""
    
    outputs = {}

    # Lista de características numéricas
    numeric_features = [
        'Elevation', 'Slope', 'Horizontal_Distance_To_Hydrology', 
        'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
        'Hillshade_9am', 'Hillshade_Noon', 'Horizontal_Distance_To_Fire_Points'
    ]

    # Normalizar características numéricas usando Min-Max Scaling
    for feature in numeric_features:
        outputs[feature + '_minmax'] = tft.scale_by_min_max(inputs[feature])

    # Convertir Cover_Type a tipo INT sin One-Hot Encoding
    outputs['Cover_Type'] = tf.cast(inputs['Cover_Type'], tf.int64)

    return outputs
