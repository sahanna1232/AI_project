from tensorflow.keras.preprocessing.image import ImageDataGenerator

def load_data(train_dir, target_size=(224, 224), batch_size=32, validation_split=0.2):
    """
    Loads and preprocesses the image dataset using ImageDataGenerator.

    Args:
        train_dir (str): Path to the training dataset directory.
        target_size (tuple): Image size for resizing (default is (224, 224)).
        batch_size (int): Number of samples per batch.
        validation_split (float): Fraction of data to reserve for validation.

    Returns:
        train_generator, validation_generator: Data generators for training and validation.
    """
    # Image data generators for training and validation with rescaling
    train_datagen = ImageDataGenerator(rescale=1./255, validation_split=validation_split)

    # Create training generator
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    # Create validation generator
    validation_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    return train_generator, validation_generator

