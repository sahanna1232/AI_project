import sqlite3

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create the users table with points column
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            points INTEGER DEFAULT 0 -- Column to store user points
        )
    ''')

    # Create the challenges table
    c.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            reward INTEGER NOT NULL -- Reward for completing the challenge
        )
    ''')

    # Create the user_challenges table to link users with challenges they accepted/completed
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            challenge_id INTEGER,
            status TEXT DEFAULT 'accepted', -- Status can be 'accepted' or 'completed'
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(challenge_id) REFERENCES challenges(id)
        )
    ''')

    conn.commit()
    conn.close()



# Call the functions to ensure database is initialized correctly
init_db()

