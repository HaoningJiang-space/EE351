import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit
import gymnasium as gym
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# 定义游戏数据
games = [
    {
        'id': 1,
        'name': 'Mario',
        'folder': 'mario',  # 添加游戏文件夹名称
        'cover_url': 'mario.jpg',
        'price': 59.99,
        'description': 'Join Mario on an epic adventure through the Mushroom Kingdom...'
    },
    {
        'id': 2,
        'name': 'Airplane Battle',
        'folder': 'airplane_battle',
        'cover_url': 'plane.jpg',
        'price': 39.99,
        'description': 'Take to the skies in Airplane Battle...'
    },
    {
        'id': 3,
        'name': 'Snake',
        'folder': 'snake',
        'cover_url': 'snake.jpg',
        'price': 19.99,
        'description': 'Relive the nostalgia with Snake...'
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

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = next((g for g in games if g['id'] == game_id), None)
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

@socketio.on('start_game')
def start_game(data):
    game_id = data['game_id']
    game = next((g for g in games if g['id'] == game_id), None)
    if game and game['name'] == 'Mario':
        env = gym.make('gym_super_mario_bros:SuperMarioBros-v0')  # 使用正确的环境名称
        state = env.reset()
        while True:
            action = env.action_space.sample()  # 随机动作，您可以根据需要修改
            state, reward, done, info = env.step(action)
            img = env.render(mode='rgb_array')
            img = Image.fromarray(img)
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            emit('game_frame', {'image': img_str})
            if done:
                break
        env.close()

@app.route('/logout')
def logout():
    # 在这里添加登出逻辑，例如清除会话等
    return "You have been logged out"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)