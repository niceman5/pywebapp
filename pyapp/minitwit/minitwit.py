# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash

# configuration
DATABASE = 'minitwit.db'        #경로표시하면 위치 지정 가능
# DATABASE = 'C:\\00.Dev\\Study\\pywebapp\\pyapp\\minitwit\\minitwit2.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

#create application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def connect_db():
    # return new connection
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    # database생성처리
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    # 쿼리실행하고 결과 리스트나 사전으로 리턴
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def get_user_id(username):
    # 이름으로 id찾기
    rv = g.db.execute('select user_id from user where username = ?', [username]).fetchone()
    return rv[0] if rv else None

def format_datetime(timestamp):
    # timestamp 표시
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def gravatar_url(email, size=80):
    # return 
    return 'http://www.gravatar.com/avatar%s?d=identicon=%d'%(md5(email.strip().lower().encode('utf-8')).hexdigest(),size)

@app.before_request
def before_request():
    # 요청이있을 때마다 데이터베이스에 연결되어 있는지 확인하고 현재 사용자가 있는지 확인하십시오.
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id=?', [session['user_id']], one=True)

@app.teardown_request
def teardown_request(exception):
    #요청이 끝나면 데이터베이스를 다시 닫습니다.
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def timeline():
    # 사용자 타임 라인을 표시하거나 로그인 한 사용자가 없으면 공개 타임 라인으로 리디렉션됩니다. 이 타임 라인에는 사용자의 
    # 메시지와 팔로우 된 사용자의 모든 메시지가 표시됩니다.
    if not g.user:
        return redirect(url_for('public_timeline'))
    
    return render_template('timeline.html', message=query_db('''
        select
            message.*
        ,   user.* 
        from message, user
        where message.author_id = user.user_id
        and (
                user.user_id = ?
                or
                user.user_id in (select whom_id from follower where who_id=?)
            )
        order by message.pub_date desc limit ?
    ''', [session['user_id'], session['user_id'], PER_PAGE] ))

@app.route('/public')
def public_timeline():
    #모든 사용자의 최신 메시지를 표시합니다
    print('call public_timeline()')
    print(PER_PAGE)
    return render_template('timeline.html', message=query_db('''
        select 
            message.*
        ,   user.*
        from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?
    ''', [PER_PAGE]))

@app.route('/<username>')
def user_timeline(username):
    # 사용자의 트윗을 표시한다.
    profile_user = query_db('select * from user where username=?',[username], one=True)

    if profile_user is None:
        abort(404)
    
    followed = False
    if g.user:
        followed = query_db('''
            select 1 
            from follower 
            where follower.who_id = ? 
            and follower.whom_id = ?
        ''', [session['user_id'], profile_user['user_id']], one=True) is not None

    message=query_db('''
        select 
            message.*, user.*
        from message, user
        where message.author_id = user.user_id
        and user.user_id = ?
        order by message.pub_date desc limit ?
    ''', [profile_user['user_id'], PER_PAGE])
    
    print(type(message))
    print(message[0])
    print(type(profile_user))
    return render_template('timeline.html', message=query_db('''
        select 
            message.*, user.*
        from message, user
        where message.author_id = user.user_id
        and user.user_id = ?
        order by message.pub_date desc limit ?
    ''', [profile_user['user_id'], PER_PAGE]), followed=followed, profile_user=profile_user)

@app.route('/<username>/follow')
def follow_user(username):
    #현재 사용자를 지정된 사용자의 팔로워로 추가
    if not g.user:
        abort(404)
    
    whom_id = get_user_id(username)
    
    if whom_id is None:
        abort(404)
    
    g.db.execute('insert into follower (who_id, whom_id) values (?, ?)', [session['user_id'], whom_id])
    g.db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/<username>/unfollow')    
def unfollow_user(username):
    # 삭제...언팔
    if not g.user:
        abort(404)
    
    whom_id = get_user_id(username)
    
    if whom_id is None:
        abort(404)
    g.db.execute('delete from follewer who_id=? and whom_id = ?', [session['user_id'], whom_id])
    g.db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/add_message', methods=['POST'])
def add_message():
    # 사용자에게 메시지 등록
    if 'user_id' not in session:
        abort(404)    
    
    if request.form['text']:
        g.db.execute('''
            insert into message(author_id, text, pub_date)
            values(?,?,?) ''', (session['user_id'], request.form['text'], int(time.time())))
        g.db.commit()
        flash('your message was recorded')
    
    return redirect(url_for('timeline'))

@app.route('/login', methods=['GET','POST'])
def login():
    #login user
    if g.user:
        return redirect(url_for('timeline'))    
    error = None
    if request.method=='POST':
        user = query_db('''select * from user where username=?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('you were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
    # 사용자 등록
    if g.user:
        return redirect(url_for('timeline'))

    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            g.db.execute('''
                insert into user(username, email, pw_hash) values(?,?,?)
            ''', [request.form['username'], request.form['email'],generate_password_hash(request.form['password'])])
            g.db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    flash('you were logged out')
    session.pop('user_id', None)
    # print('log ', url_for('public_timeline'))
    return redirect(url_for('public_timeline'))

app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    