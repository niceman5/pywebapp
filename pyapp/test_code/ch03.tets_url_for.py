from flask import Flask, url_for
app = Flask(__name__)

@app.route('/hello/')
def hello():
    return 'Hello Flask!!'

@app.route('/profile/<username>')
def get_profile(username):
    return 'profile : ' + username


if __name__ == '__main__':
    with app.test_request_context():                        # http요청을 테스트 하는 함수
        print(url_for('hello'))                             # http://127.0.0.1:5000/hello/
        print(url_for('get_profile', username='flask'))     # http://127.0.0.1:5000/profile/flask
        # print(url_for('profile', username='flask2222'))
    app.run(debug=True)        