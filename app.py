from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'e31641d3c807dae1b760ce979abdb8253261941faf0996bd2db02edaa2de3eae'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    personality = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_session = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'personality': self.personality,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create database tables
with app.app_context():
    db.create_all()

# AI Personalities
AI_PERSONALITIES = {
    'shakespeare': "Write in Shakespearean English with poetic flair and dramatic expression",
    'hemingway': "Write in short, crisp sentences. Simple words. Direct style.",
    'tolkien': "Write with rich descriptions, fantasy elements, and epic storytelling",
    'comedy': "Write with humor, wit, and comedic timing. Make it funny!",
    'thriller': "Write with suspense, tension, and unexpected twists",
    'scifi': "Write with futuristic concepts, technology, and scientific imagination",
    'rajkumar_hirani': "Write with warmth, humor, and social commentary, in the style of Rajkumar Hirani (think 3 Idiots, Munna Bhai).",
    'ss_rajamouli': "Write with epic scale, grand visuals, and heroic drama, in the style of S. S. Rajamouli (think Baahubali, RRR).",
    'zoya_akhtar': "Write with urban realism, layered characters, and contemporary themes, in the style of Zoya Akhtar (think Zindagi Na Milegi Dobara, Gully Boy).",
    'anurag_kashyap': "Write with gritty realism, dark humor, and bold storytelling, in the style of Anurag Kashyap (think Gangs of Wasseypur, Black Friday).",
    'kjo': "Write with melodrama, romance, and family emotions, in the style of Karan Johar (think Kabhi Khushi Kabhie Gham, Kuch Kuch Hota Hai)."
}

def generate_ai_response(user_text, personality):
    """Generate AI response using OpenAI API or fallback mock response"""
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": AI_PERSONALITIES.get(personality, '')},
                {"role": "user", "content": f"Continue this story: {user_text}"}
            ],
            max_tokens=300,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenRouter API Error: {e}")
        return generate_mock_response(user_text, personality)

def generate_mock_response(user_text, personality):
    """Generate mock AI response when API is not available"""
    
    mock_responses = {
        'shakespeare': "Hark! What tale dost thou weave? Methinks the story doth unfold most wondrously. The protagonist, brave and true, ventures forth into realms unknown, where dragons slumber and magic whispers through ancient stones. Verily, this narrative shall echo through the ages!",
        
        'hemingway': "The story continued. It was good. The sun set. The character walked on. There was no time for doubt. Only action. The end would come. But not today. Today there was still hope.",
        
        'tolkien': "And so the journey continued through lands forgotten by time itself. Ancient trees whispered secrets of ages past, their gnarled branches reaching toward skies painted with the colors of legend. In the distance, mountains stood as silent guardians, their peaks crowned with eternal snow.",
        
        'comedy': "And then something absolutely ridiculous happened! A penguin wearing a tuxedo (yes, a tuxedo on a penguin!) waddled in and declared himself the new CEO. Everyone just went with it. Quarterly profits increased by 300%. Nobody questioned the fish-based bonus structure.",
        
        'thriller': "The footsteps grew closer. Each echo in the hallway sent shivers down the spine. There was no escape now. The door handle slowly turned. Time seemed to freeze. Then, suddenly, everything changed. The hunter had become the hunted.",
        
        'scifi': "The quantum stabilizers hummed to life as the ship breached the dimensional barrier. Reality flickered, reformed, and presented possibilities never before imagined. In this new universe, the laws of physics were merely suggestions, and consciousness itself could be uploaded, downloaded, and shared."
    }
    
    return mock_responses.get(personality, "The story continued in unexpected ways. New characters emerged, plot twists unfolded, and the narrative took on a life of its own. What happened next would surprise everyone.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            error = 'Username and password are required.'
        elif User.query.filter_by(username=username).first():
            error = 'Username already exists.'
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('register.html', error=error)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        print(f"Login attempt: username={username}, password={password}")
        print(f"User found: {user}")
        if user:
            print(f"Password hash in DB: {user.password_hash}")
            print(f"Password check: {user.check_password(password)}")
        if user and user.check_password(password):
            login_user(user)
            print("Login successful!")
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
            print("Login failed.")
    return render_template('login.html', error=error)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Home page"""
    return render_template('index.html', personalities=AI_PERSONALITIES.keys())

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate AI continuation"""
    data = request.json
    user_text = data.get('user_text', '')
    personality = data.get('personality', 'shakespeare')
    
    if not user_text:
        return jsonify({'error': 'Please provide some text'}), 400
    
    ai_response = generate_ai_response(user_text, personality)
    
    return jsonify({
        'ai_response': ai_response,
        'personality': personality
    })

@app.route('/save', methods=['POST'])
@login_required
def save_story():
    """Save story to database"""
    data = request.json
    
    title = data.get('title', 'Untitled Story')
    user_input = data.get('user_text', '')
    ai_response = data.get('ai_response', '')
    personality = data.get('personality', 'shakespeare')
    
    if not user_input or not ai_response:
        return jsonify({'error': 'Story content is missing'}), 400
    
    story = Story(
        title=title,
        user_input=user_input,
        ai_response=ai_response,
        personality=personality,
        user_session=current_user.username
    )
    
    db.session.add(story)
    db.session.commit()
    
    return jsonify({'success': True, 'story_id': story.id})

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with all stories"""
    stories = Story.query.filter_by(user_session=current_user.username).order_by(Story.created_at.desc()).all()
    return render_template('dashboard.html', stories=stories)

@app.route('/story/<int:story_id>')
@login_required
def view_story(story_id):
    """View individual story"""
    story = Story.query.get_or_404(story_id)
    if story.user_session != current_user.username:
        return redirect(url_for('dashboard'))
    return render_template('story.html', story=story)

@app.route('/delete/<int:story_id>', methods=['POST'])
@login_required
def delete_story(story_id):
    """Delete a story"""
    story = Story.query.get_or_404(story_id)
    if story.user_session != current_user.username:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(story)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/download/<int:story_id>')
@login_required
def download_story(story_id):
    """Download story as text file"""
    story = Story.query.get_or_404(story_id)
    if story.user_session != current_user.username:
        return redirect(url_for('dashboard'))
    content = f"""Title: {story.title}\nDate: {story.created_at.strftime('%Y-%m-%d %H:%M')}\nAI Personality: {story.personality.title()}\n\n=== Your Part ===\n{story.user_input}\n\n=== AI's Continuation ===\n{story.ai_response}\n"""
    response = app.response_class(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename="{story.title}.txt"'}
    )
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)