# -*- coding: utf-8 -*-
from __future__ import with_statement
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash

# configuration
DATABASE = 'minitwit.db'
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
    
    return render_template('timeline_html', message=query_db('''
        select
             message.* user.* 
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
    return render_template('timeline.html', message=query_db('''
        select 
            message.*, user.*
        from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?
    ''', [PER_PAGE]))    

@app.route('/<username>')
def user_timeline(username):
    # 사용자의 트윗을 표시한다.
    profile_user = query_db('select * from user username=?',[username], one=True)

    if profile_user is None:
        abort(404)
    
    flolowed = False
    if g.user:
        flolowed = query_db('''
            select 1 
            from follower 
            where follower.who_id = ? 
            and follower.whom_id = ?
        ''', [session['user_id'], profile_user['user_id']], one=True) is not None
    return render_template('timeline,html', message=query_db('''
        select 
            message.*, user.*
        from message, user
        where message.author_id = user.user_id
        and user.user_id = ?
        order by message.pub_date desc limit ?
    ''', [profile_user['user_id'], PER_PAGE], flolowed=flolowed, profile_user=profile_user))

@app.route('<username>/follow')
def follow_user(username):
    #현재 사용자를 지정된 사용자의 팔로워로 추가
    if not g.user:
        abort(404)
    
    whom_id = get_user_id(username)
    
    if whom_id is None
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
    
    if whom_id is None
        abort(404)
    g.db.execute('delete from follewer who_id=? and whom_id = ?', [session['user_id'], whom_id])
    g.db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))
    