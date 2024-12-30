import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, request, redirect, session, flash ,send_from_directory
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, async_mode='eventlet')

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    member_since = db.Column(db.String(50), nullable=False, default='January 2023')
    membership_level = db.Column(db.String(50), nullable=False, default='Gold')
    address = db.Column(db.String(200), nullable=False, default='1234 Game St, Gamer City, 56789')
    phone = db.Column(db.String(20), nullable=False, default='123-456-7890')
    profile_picture = db.Column(db.String(100), default='player1.png')
    favorite_games = db.Column(db.String(300), nullable=False, default='')
    purchase_history = db.relationship('Purchase', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 定义游戏数据，包括评论

games = [
    {
        'id': 1,
        'name': 'Mario',
        'folder': 'mario',
        'cover_url': 'mario.png',
        'screenshots': ['mario1.png', 'mario2.jpg'],
        'price': 59.99,
        'description': 'Join Mario on an epic adventure through the Mushroom Kingdom...',
        'comments': []  # 初始化评论列表
    },
    {
        'id': 2,
        'name': 'Airplane Battle',
        'folder': 'airplane_battle',
        'cover_url': 'plane.png',
        'screenshots': ['plane1.png', 'plane2.png'],
        'price': 39.99,
        'description': 'Take to the skies in Airplane Battle...',
        'comments': []
    },
    {
        'id': 3,
        'name': 'Snake',
        'folder': 'snake',
        'cover_url': 'snake.png',
        'screenshots': ['snake1.jpeg', 'snake2.png'],
        'price': 19.99,
        'description': 'Relive the nostalgia with Snake...',
        'comments': []
    },
    {
        'id': 4,
        'name': 'Star Wars',
        'folder': 'silence',
        'cover_url': 'silence.jpg',
        'screenshots': ['conquer_planet.png', 'planet.png'],
        'price': 49.99,
        'description': '飞向无垠的星河，在寂静宇宙中展开星球大战……',
        'comments': []
    },
    {
        'id': 5,
        'name': 'Life in Digua',
        'folder': 'life-in-digua-main',
        'cover_url': 'brest.jpg',
        'screenshots': ['digua.jpg', 'guoba.jpg'],
        'price': 99.99,
        'description': 'Welcome to Life in Digua! A mysterious thriller awaits...',
        'comments': []
    }
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html', popular_games=games)

@app.route('/store')
def store():
    return render_template('store.html', games=games)

@app.route('/game/<int:game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    game = next((g for g in games if g['id'] == game_id), None)
    if not game:
        return "Game not found", 404

    if request.method == 'POST':
        comment = request.form.get('comment')
        if comment:
            game['comments'].append(comment)
        return redirect(url_for('game_detail', game_id=game_id))

    return render_template('game_detail.html', game=game)

@app.route('/user')
@login_required
def user_profile():
    current_user = User.query.filter_by(username=session['user']).first()
    return render_template('user.html', user=current_user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    current_user = User.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        # 获取表单数据并更新用户信息
        current_user.username = request.form.get('username').strip()
        current_user.email = request.form.get('email').strip().lower()
        current_user.address = request.form.get('address').strip()
        current_user.phone = request.form.get('phone').strip()
        current_user.membership_level = request.form.get('membership_level').strip()
        # 处理头像上传（需实现文件上传逻辑）
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            profile_picture.save(f'static/profile_pictures/{profile_picture.filename}')
            current_user.profile_picture = profile_picture.filename
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))
    return render_template('edit_profile.html', user=current_user)

@app.route('/play/<int:game_id>', methods=['GET', 'POST'])
def play_game(game_id):
    game = next((g for g in games if g['id'] == game_id), None)
    if not game:
        return "Game not found", 404

    if request.method == 'POST':
        comment = request.form.get('comment')
        if comment:
            game['comments'].append(comment)
        return redirect(url_for('play_game', game_id=game_id))

    # 如果是“星球大战”，则使用silence.html模板
    if game['name'] == 'Star Wars':
        return render_template('silence.html', game=game)
    elif game['name'] == 'Life in Digua':
        # 不移动 index.html，直接从其所在目录提供文件
        # return send_from_directory('/Users/haoning/project/EE351/life-in-digua-main', 'index.html')
        return render_template('index.html', game=game)
    else:
        return render_template('play_game.html', game=game)

@app.route('/logout')
def logout():
    session.clear()
    flash('You logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        # 检查用户是否已存在
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))

        # 创建新用户
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
            # favorite_games 会自动使用默认值 ''
        )
        db.session.add(new_user)
        db.session.commit()
        session['user'] = new_user.username
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user_obj = User.query.filter_by(email=email).first()
        if user_obj and check_password_hash(user_obj.password, password):
            session['user'] = user_obj.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False)