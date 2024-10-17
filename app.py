
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import os
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from data_loader import load_data

print(os.getcwd())

# Path to the dataset
train_dir = r'C:\Users\Sahanna\energy_consumption_project\data'

# Load the data
train_generator, validation_generator = load_data(train_dir, target_size=(224, 224), batch_size=32)


app = Flask(__name__)
app.secret_key = 'your_secret_key'




# Load your trained MobileNet model
model = load_model('mobilenet_waste_classification.h5')

# Function to preprocess images for MobileNet
def preprocess_image(image):
    image = image.resize((224, 224))  # Resize image to 224x224
    image = np.array(image) / 255.0   # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Define class names (e.g., Plastic, Paper, Glass, etc.)
class_names = ['Cardboard', 'Glass', 'Metal', 'Paper', 'Plastic', 'Trash', 'Organic']

@app.route('/save_steps', methods=['POST'])
def save_steps():
    steps = request.json.get('steps')
    carbon_offset = request.json.get('carbon_offset')

    # Save the data in the user's profile (assume you have a user model)
    user_id = session['user_id']  # Example of retrieving the current user from the session
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET steps = ?, carbon_offset = ? WHERE id = ?', 
                   (steps, carbon_offset, user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/carbon_offset')
def carbon_offset():
    return render_template('carbon_offset.html')


@app.route('/classify_waste', methods=['GET', 'POST'])
def classify_waste():
    if request.method == 'POST':
        print("POST request received") 
        if 'file' not in request.files:
            print("No file uploaded")
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            print("No file selected")
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            img = Image.open(file.stream)
            img = img.resize((224, 224))  # Resize for MobileNet
            img_array = np.array(img) / 255.0  # Normalize the image

            # Expand dimensions since MobileNet expects 4D input (batch size, height, width, channels)
            img_array = np.expand_dims(img_array, axis=0)

            # Load model and predict
            print("Image processed, loading model...")
            model = load_model('mobilenet_waste_classification.h5')
            predictions = model.predict(img_array)

            # Map the predictions to the class labels (adjust based on your dataset)
            class_names = ['Plastic', 'Metal', 'Paper', 'Glass', 'Cardboard']  # Add your labels here
            predicted_class = class_names[np.argmax(predictions)]
            
            print(f"Prediction: {predicted_class}")

            # Render the result in the HTML template
            return render_template('classify_waste.html', result=predicted_class)
            
  
    return render_template('classify_waste.html')


    return jsonify({'classification': waste_category})

# Example static data for testing (You can replace this with actual API calls)
def get_electricity_data(country):
    return 0.45, 0.12  # Carbon intensity, electricity price (replace with real data)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index')
def index():
    return render_template('index.html')

# Energy estimation route
@app.route('/estimate', methods=['POST'])
def estimate():
    try:
        power = float(request.form['power'])
        hours = float(request.form['hours'])
        country = request.form['country']
        
        # Sample energy calculations
        energy_consumption = (power * hours) / 1000  # kWh/day
        carbon_intensity, electricity_price = get_electricity_data(country)
        carbon_footprint = energy_consumption * carbon_intensity
        cost = energy_consumption * electricity_price
        
        tips = "Consider reducing appliance usage or switching to energy-efficient devices."
        return render_template('index.html', energy=energy_consumption, carbon=carbon_footprint, cost=cost, tips=tips)
    except ValueError:
        return render_template('index.html', error="Invalid input. Please enter valid numbers.")

# Savings calculation route
@app.route('/savings', methods=['GET', 'POST'])
def savings():
    if request.method == 'POST':
        try:
            original_power = float(request.form['original_power'])
            original_hours = float(request.form['original_hours'])
            new_power = float(request.form['new_power'])
            new_hours = float(request.form['new_hours'])
            country = request.form['country']

            carbon_intensity, electricity_price = get_electricity_data(country)

            original_consumption = (original_power * original_hours) / 1000  # kWh/day
            new_consumption = (new_power * new_hours) / 1000  # kWh/day

            original_cost = original_consumption * electricity_price
            new_cost = new_consumption * electricity_price
            money_saved = original_cost - new_cost

            return render_template('savings.html', 
                                   original_cost=original_cost, 
                                   new_cost=new_cost, 
                                   money_saved=money_saved, 
                                   carbon_intensity=carbon_intensity)
        except ValueError:
            return render_template('savings.html', error="Invalid input.")
    return render_template('savings.html')

# Route for graphs page
@app.route('/graphs', methods=['GET', 'POST'])
def graphs():
    if request.method == 'POST':
        try:
            # Retrieve appliance data from the form
            ac_power = request.form.get('ac_power', 0, type=float)
            ac_hours = request.form.get('ac_hours', 0, type=float)
            fan_power = request.form.get('fan_power', 0, type=float)
            fan_hours = request.form.get('fan_hours', 0, type=float)
            lights_power = request.form.get('lights_power', 0, type=float)
            lights_hours = request.form.get('lights_hours', 0, type=float)
            tv_power = request.form.get('tv_power', 0, type=float)
            tv_hours = request.form.get('tv_hours', 0, type=float)
            washing_power = request.form.get('washing_power', 0, type=float)
            washing_hours = request.form.get('washing_hours', 0, type=float)
            country = request.form['country']

            # Get country-specific carbon intensity and electricity price
            carbon_intensity, electricity_price = get_electricity_data(country)

            # Calculate the energy consumption for each appliance (kWh/day)
            ac_energy = (ac_power * ac_hours) / 1000  # Convert watts to kWh
            fan_energy = (fan_power * fan_hours) / 1000
            lights_energy = (lights_power * lights_hours) / 1000
            tv_energy = (tv_power * tv_hours) / 1000
            washing_energy = (washing_power * washing_hours) / 1000

            # Calculate total energy consumption (kWh/day)
            total_energy_consumption = ac_energy + fan_energy + lights_energy + tv_energy + washing_energy

            # Calculate carbon intensity for the user based on total energy consumption
            user_carbon_intensity = total_energy_consumption * carbon_intensity

            # Calculate cost based on the total energy consumption and electricity price
            total_cost = total_energy_consumption * electricity_price

            # Example values for healthy and normal consumption, carbon intensity, and cost
            healthy_consumption = 100  # Sample healthy energy consumption in kWh/day
            normal_consumption = 200  # Sample normal energy consumption in kWh/day
            healthy_intensity = 150  # Healthy carbon intensity in gCO₂/kWh
            normal_intensity = 200  # Normal carbon intensity in gCO₂/kWh
            average_cost = 5  # Average daily cost in USD
            global_cost = 7  # Global average cost in USD

            return render_template('graphs.html',
                                   energy=total_energy_consumption,
                                   healthy=healthy_consumption,
                                   normal=normal_consumption,
                                   carbon=user_carbon_intensity,
                                   cost=total_cost,
                                   country=country)
        except ValueError:
            return render_template('graphs.html', error="Invalid input.")
    return render_template('graphs.html')

# Route for personalized tips page
@app.route('/tips', methods=['GET', 'POST'])
def tips():
    if request.method == 'POST':
        usage_pattern = request.form.get('usage_pattern')
        appliance_type = request.form.get('appliance_type')
        electricity_rate = request.form.get('electricity_rate')

        tips = []
        if usage_pattern == 'high':
            tips.append("Try reducing usage during peak hours.")
        if appliance_type == 'inefficient':
            tips.append("Consider upgrading to energy-efficient appliances.")
        if float(electricity_rate) > 0.15:
            tips.append("Look for renewable energy options or better tariffs.")

        return render_template('tips.html', tips=tips)
    
    return render_template('tips.html')

# Route for SDG page
@app.route('/sdg')
def sdg():
    return render_template('sdg.html')

# Route for rendering the challenges page
@app.route('/challenges', methods=['GET'])
def challenges():
    return render_template('challenges.html')

@app.route('/complete_challenge/<int:challenge_id>', methods=['POST'])
def complete_challenge(challenge_id):
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']
    conn = get_db_connection()

    # Mark the challenge as completed
    conn.execute('UPDATE user_challenges SET status = ? WHERE id = ? AND user_id = ?', ('completed', challenge_id, user_id))

    # Get the reward for the completed challenge
    reward = conn.execute('SELECT reward FROM user_challenges WHERE id = ?', (challenge_id,)).fetchone()

    # Update the user's points
    conn.execute('UPDATE users SET points = points + ? WHERE id = ?', (reward['reward'], user_id))

    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})  # Ensure the response is sent back properly




    


    # Mock-up: Track the completion in a simple list or file (could also be a database)
    completed_challenges = []

    # Mark the challenge as completed
    if challenge_id not in completed_challenges:
        completed_challenges.append(challenge_id)

    # For now, just print and send back a success message
    print(f"Challenge {challenge_id} completed")
    return jsonify({'message': f'Challenge {challenge_id} completed successfully!'}), 200

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            conn.commit()
            # Log the user in automatically after signup
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists!', 'danger')
        finally:
            conn.close()

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/accept_challenge/<int:challenge_id>', methods=['POST'])
def accept_challenge(challenge_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Get the challenge description and reward from the POST request
    challenge_data = request.get_json()
    description = challenge_data['description']
    reward = challenge_data['reward'].split()[0]  # Extract reward points from the string

    # Insert the accepted challenge for this user into the database
    conn.execute('INSERT INTO user_challenges (user_id, description, reward, status) VALUES (?, ?, ?, ?)',
                 (user_id, description, reward, 'accepted'))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Get the user's total points
    user = conn.execute('SELECT points FROM users WHERE id = ?', (user_id,)).fetchone()

    # Get accepted challenges
    challenges = conn.execute('SELECT * FROM user_challenges WHERE user_id = ? AND status = ?', (user_id, 'accepted')).fetchall()

    # Get completed challenges
    completed_challenges = conn.execute('SELECT * FROM user_challenges WHERE user_id = ? AND status = ?', (user_id, 'completed')).fetchall()

    conn.close()

    return render_template('dashboard.html', total_points=user['points'], challenges=challenges, completed_challenges=completed_challenges)


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out', 'info')
    return redirect(url_for('login'))








if __name__ == '__main__':
    app.run(debug=True)
