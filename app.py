from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    return render_template('game_detail.html', game_id=game_id)

@app.route('/user')
def user_profile():
    return render_template('user.html')

@app.route('/logout')
def logout():
    # 在这里添加登出逻辑，例如清除会话等
    return "You have been logged out"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)