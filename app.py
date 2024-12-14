from flask import Flask, render_template, url_for

app = Flask(__name__)

# 定义游戏数据
games = [
    {
        'id': 1,
        'name': 'Mario',
        'cover_url': 'mario.jpg',
        'price': 59.99,
        'description': 'Join Mario on an epic adventure through the Mushroom Kingdom. Jump, run, and defeat enemies to save Princess Peach from the evil Bowser. With stunning graphics and engaging gameplay, this classic platformer game is a must-play for all ages.'
    },
    {
        'id': 2,
        'name': 'Airplane Battle',
        'cover_url': 'plane.jpg',
        'price': 39.99,
        'description': 'Take to the skies in Airplane Battle, an exhilarating aerial combat game. Pilot your fighter jet through intense dogfights, complete challenging missions, and upgrade your aircraft with advanced weaponry. Experience the thrill of high-speed aerial warfare like never before.'
    },
    {
        'id': 3,
        'name': 'Snake',
        'cover_url': 'snake.jpg',
        'price': 19.99,
        'description': 'Relive the nostalgia with Snake, a fun and addictive game that will keep you hooked for hours. Guide your snake to eat food and grow longer, but be careful not to run into yourself or the walls. With simple controls and endless gameplay, Snake is perfect for players of all ages.'
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

@app.route('/logout')
def logout():
    # 在这里添加登出逻辑，例如清除会话等
    return "You have been logged out"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)