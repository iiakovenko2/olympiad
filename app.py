from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# PostgreSQL connection string
DATABASE_URL = "postgresql://olympiad_db_user:adxZZp7uKX6C1u35pTZLNmzMXWSJKFFh@dpg-cuatpki3esus73eosfbg-a/olympiad_db"

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Default route to redirect to signup
@app.route('/')
def main_route():
    return redirect(url_for('signup'))

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
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO quiz_results (student_id, first_name, last_name, score, answers)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (student_id, first_name, last_name, 0, ""))  # Initialize score and answers
                conn.commit()

        return jsonify({'success': True, 'redirect_url': url_for('quiz', student_id=student_id)})

# Route to fetch student information (name, last name) for the quiz page
@app.route('/quiz')
def quiz():
    student_id = request.args.get('student_id')
    
    # Fetch student info from the database
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT first_name, last_name FROM quiz_results WHERE student_id = %s
            ''', (student_id,))
            student = cursor.fetchone()

    if student:
        first_name = student['first_name']
        last_name = student['last_name']
        return render_template('testpage.html', student_id=student_id, first_name=first_name, last_name=last_name)
    else:
        return "Student not found!", 404

# Route to handle quiz submissions
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        data = request.get_json()  # Use get_json() for clarity
        student_id = data.get('student_id')
        score = data.get('score')
        answers = data.get('answers')

        if not student_id or score is None or answers is None:
            return jsonify({"error": "Missing required fields"}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE quiz_results
                    SET score = %s, answers = %s
                    WHERE student_id = %s
                ''', (score, str(answers), student_id))
                conn.commit()

        return jsonify({"success": True})

    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to download database (if needed for debugging)
@app.route('/download_db')
def download_db():
    return send_file('instance/olympiad.db', as_attachment=True)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
