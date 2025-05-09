import pickle
import cv2
import mediapipe as mp
import numpy as np
import atexit
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session

# Load trained model
model_dict = pickle.load(open('model.p', 'rb'))
model = model_dict['model']

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  


USER_CREDENTIALS = {
    "username": "admin",
    "password": "123"
}

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7, max_num_hands=1)

# Gesture labels
labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F',
    6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
    12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R',
    18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X',
    24: 'Y', 25: 'Z', 26: '0', 27: '1', 28: '2',
    29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9',
    36: 'I love You', 37: 'Yes', 38: 'No', 39: 'Hello', 40: 'Thanks',
    41: 'Sorry', 43: 'Space'
}

# Start video capture
cap = cv2.VideoCapture(0)
predicted_character = "Waiting for prediction..."  # Initialize variable to store last prediction

def process_frame():
    """ Captures video, detects hand gestures, and returns predictions. """
    global predicted_character

    while True:
        success, frame = cap.read()
        if not success or frame is None:
            continue

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        data_aux = []
        x_, y_ = [], []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                for lm in hand_landmarks.landmark:
                    x_.append(lm.x)
                    y_.append(lm.y)

                min_x, max_x = int(min(x_) * frame.shape[1]), int(max(x_) * frame.shape[1])
                min_y, max_y = int(min(y_) * frame.shape[0]), int(max(y_) * frame.shape[0])

                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)

                for lm in hand_landmarks.landmark:
                    data_aux.append(lm.x - min(x_))
                    data_aux.append(lm.y - min(y_))

                prediction = model.predict(np.array(data_aux).reshape(1, -1))
                predicted_character = labels_dict.get(int(prediction[0]), "Unknown")  # Store prediction globally

                cv2.putText(frame, predicted_character, (min_x, min_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# ------------------ FLASK ROUTES ------------------

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handles user login"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
        session['user'] = username  # Store session
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials!"})

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/signup')
def signup():
    """Signup page (placeholder)"""
    return render_template('signup.html')  # Ensure you create 'signup.html'

@app.route('/main')
def main():
    """Redirects to main page if logged in"""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(process_frame(), mimetype='multipart/x-mixed-replace; boundary=frame',
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.route('/predict', methods=['POST'])
def predict():
    """Returns latest predicted gesture"""
    global predicted_character
    return jsonify({"prediction": predicted_character})

# ------------------ APP CLEANUP ------------------

def cleanup():
    """Releases camera on exit"""
    cap.release()

atexit.register(cleanup)

# ------------------ RUN FLASK SERVER ------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
