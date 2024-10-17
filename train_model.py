from tensorflow.keras.applications import MobileNet
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from data_loader import load_data

# Step 1: Load Data
train_dir = r'C:\Users\Sahanna\energy_consumption_project\data'  # Path to your dataset
train_generator, validation_generator = load_data(train_dir, target_size=(224, 224), batch_size=32)

# Step 2: Load the Pre-trained MobileNet Model
base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Step 3: Add Custom Layers on Top of MobileNet
x = base_model.output
x = GlobalAveragePooling2D()(x)  # Global average pooling to reduce feature maps
x = Dense(1024, activation='relu')(x)  # Add a fully connected layer
predictions = Dense(6, activation='softmax')(x)  # 5 output classes (Plastic, Paper, Glass, Metal, Organic)

# Step 4: Define the Full Model
model = Model(inputs=base_model.input, outputs=predictions)

# Step 5: Freeze the Base Layers
for layer in base_model.layers:
    layer.trainable = False  # Keep the pre-trained layers frozen

# Step 6: Compile the Model
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Step 7: Train the Model
history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=6  # Adjust epochs based on how long you can train
)

# Step 8: Save the Model
model.save('mobilenet_waste_classification.h5')
