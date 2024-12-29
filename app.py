import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, request, redirect
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# 定义游戏数据，包括评论
games = [
    {
        'id': 1,
        'name': 'Mario',
        'folder': 'mario',
        'cover_url': 'mario.png',
        'screenshots': ['mario1.png', 'mario2.png'],
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
        'screenshots': ['snake1.png', 'snake2.png'],
        'price': 19.99,
        'description': 'Relive the nostalgia with Snake...',
        'comments': []
    }
]

# 模拟用户数据
user = {
    'username': 'Player1',
    'email': 'player1@example.com'
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

@app.route('/play/<int:game_id>')
def play_game(game_id):
    game = next((g for g in games if g['id'] == game_id), None)
    if game:
        return render_template('play_game.html', game=game)
    else:
        return "Game not found", 404

@app.route('/logout')
def logout():
    # 在这里添加登出逻辑，例如清除会话等
    return "You have been logged out"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False)