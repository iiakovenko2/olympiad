from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('instance/olympiad.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to serve the sign-up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        student_id = data.get('student_id')

        # Validate the data
        if not first_name or not last_name or not student_id:
            return jsonify({'success': False, 'error': 'All fields are required!'}), 400

        # Insert the student info into the database
        with sqlite3.connect('instance/olympiad.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz_results (student_id, first_name, last_name, score, answers)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, first_name, last_name, 0, ""))  # Initialize score and answers
            conn.commit()

        return jsonify({'success': True, 'redirect_url': url_for('quiz', student_id=student_id)})

# Route to fetch student information (name, last name) for the quiz page
@app.route('/quiz')
def quiz():
    student_id = request.args.get('student_id')
    
    # Fetch student info from the database
    with sqlite3.connect('instance/olympiad.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT first_name, last_name FROM quiz_results WHERE student_id = ?
        ''', (student_id,))
        student = cursor.fetchone()

    if student:
        first_name, last_name = student
        return render_template('testpage.html', student_id=student_id, first_name=first_name, last_name=last_name)
    else:
        return "Student not found!", 404

# Route to handle quiz submissions
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        # Log incoming request
        data = request.get_json()  # Use get_json() for clarity
        print("Received data:", data)  # Log the received data

        student_id = data.get('student_id')
        score = data.get('score')
        answers = data.get('answers')

        # Check if any required fields are missing
        if not student_id or score is None or answers is None:
            print("Missing data:", {"student_id": student_id, "score": score, "answers": answers})
            return jsonify({"error": "Missing required fields"}), 400

        # Log answers to ensure they're correctly formatted
        print("Answers:", answers)

        # Update quiz results in the database
        with sqlite3.connect('instance/olympiad.db') as conn:
            cursor = conn.cursor()
            print("Attempting to update database...")  # Log before the database query
            cursor.execute('''
                UPDATE quiz_results
                SET score = ?, answers = ?
                WHERE student_id = ?
            ''', (score, str(answers), student_id))  # Convert answers to string if it's a dictionary
            conn.commit()
            print("Database updated successfully!")  # Log after successful update

        return jsonify({"success": True})

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")  # Log database error
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"General error: {str(e)}")  # Log general error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
