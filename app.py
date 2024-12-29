import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, request, redirect ,session, flash
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet')

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
    }
]

# 模拟用户数据
user = {
    'username': 'Player1',
    'email': 'player1@example.com',
    'member_since': 'January 2023',
    'membership_level': 'Gold',
    'address': '1234 Game St, Gamer City, 56789',
    'phone': '123-456-7890',
    'profile_picture': 'player1.png',  # 确保在 static/profile_pictures/ 下有此图片
    'favorite_games': ['Mario', 'Airplane Battle', 'Snake'],
    'purchase_history': [
        {'game_name': 'Mario', 'date': '2023-01-15', 'amount': 59.99, 'payment_method': 'Credit Card'},
        {'game_name': 'Airplane Battle', 'date': '2023-02-20', 'amount': 39.99, 'payment_method': 'PayPal'},
        {'game_name': 'Snake', 'date': '2023-03-10', 'amount': 19.99, 'payment_method': 'Credit Card'},
    ],
    'comments': [
        {'game_name': 'Mario', 'date': '2023-01-20', 'content': 'Great game! Had a lot of fun.'},
        {'game_name': 'Airplane Battle', 'date': '2023-02-25', 'content': 'Exciting and challenging.'}
    ]
}

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
def user_profile():
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # 获取表单数据并更新用户信息
        user['username'] = request.form.get('username')
        user['email'] = request.form.get('email')
        user['address'] = request.form.get('address')
        user['phone'] = request.form.get('phone')
        user['membership_level'] = request.form.get('membership_level')
        # 处理头像上传（需实现文件上传逻辑）
        # 这里只做简单示范，实际应用中需处理文件保存和安全性
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            profile_picture.save(f'static/profile_pictures/{profile_picture.filename}')
            user['profile_picture'] = profile_picture.filename
        return redirect(url_for('user_profile'))
    return render_template('edit_profile.html', user=user)

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

    return render_template('play_game.html', game=game)

@app.route('/logout')
def logout():
    session.clear()
    flash('You logged out successfully', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False)