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
    
    return render_template('timeline_html', message=query_db)

