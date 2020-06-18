# -*- coding: utf-8 -*-
"""
    photolog
    ~~~~~~~~

    photolog 패키지 초기화 모듈. 
    photolog에 대한 flask 어플리케이션을 생성함.
    config, blueprint, session, DB연결 등을 초기화함.

"""

import os
from flask import Flask, render_template, request, url_for
'''
# os 모듈의 getpid 를 getpid 라는 이름으로 import
>>> from os import getpid                         

# 현재 scope 에서는 os 라는 존재는 모르고
# os.getpid 를 가리키는 getpid 만 있으므로 에러
>>> os.getpid()
                                                        

Traceback (most recent call last):
  File “<stdin>”, line 1, in <module>
NameError: name ‘os’ is not defined


# getpid 밖에 모름
>>> getpid()                                          
2541

# os 의 getpid 만 import 했으므로 getpgid 는 모름.
>>> getpgid()       

# os 를 import 하니 getpgid 함수도 사용가능
>>> import os                                        
>>> os.getpgid(2541)

2541
'''

def print_setting(config):
    print('========================================================')
    print('SETTINGS for PHOTOLOG APPLICATION')
    print('========================================================')
    for key, value in config:
        print('%s=%s' % (key, value))
    print('========================================================')
    '''
    HTTP Error Code 404와 500은 errorhanlder에 application 레벨에서
    적용되므로 app 객체 생성시 등록해준다.
    '''

def not_found(error):
    return render_template('404.html'), 404

def server_error(error):
    err_msg = str(error)
    return render_template('500.html', err_msg=err_msg), 500

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page 
    return url_for(request.endpoint, **args)

def create_app(config_filepath='resource/config.cfg'):
    # 기본 설정은 PhotologConfig 객체에 정의되있고 운영 환경 또는 기본 설정을 변경을 하려면
    # 실행 환경변수인 PHOTOLOG_SETTINGS에 변경할 설정을 담고 있는 파일 경로를 설정 
    from photolog.photolog_config import PhotologConfig

    photolog_app = Flask(__name__)
    photolog_app.config.from_object(PhotologConfig)
    photolog_app.config.from_pyfile(config_filepath, slient=True)
    print_setting(photolog_app.config.items())

    # 로그 초기화
    from photolog.photolog_logger import Log

    log_filepath = os.path.join(photolog_app.root_path, 
                                photolog_app.config['LOG_FILE_PATH']))
    Log.init(log_filepath=log_filepath)

    # data base처리
    from photolog.database import DBManager
    db_filepath = os.path.join( photolog_app.root_path,
                                photolog_app.config['DB_FILE_PATH'])
    db_url = photolog_app.config['DB_URL'] + db_filepath
    DBManager.init(db_url, eval(photolog_app.config['DB_LOG_FILE']))
    DBManager.init_db()

    # 뷰 함수 모듈은 어플리케이션 객체 생성하고 블루프린트 등록전에 
    # 뷰 함수가 있는 모듈을 임포트해야 해당 뷰 함수들을 인식할 수 있음    
    from photolog.controller import login
    from photolog.controller import photo_show
    from photolog.controller import photo_upload
    from photolog.controller import register_user
    from photolog.controller import twitter

    from photolog.photolog_blueprint import photolog
    photolog_app.register_blueprint(photolog)

    # SessionInterface 설정.
    # Redis를 이용한 세션 구현은 cache_session.RedisCacheSessionInterface 임포트하고
    # app.session_interface에 RedisCacheSessionInterface를 할당    
    from photolog.cache_session import SimpleCacheSessionInserface
    photolog_app.session_interface = SimpleCacheSessionInserface()

    photolog_app.error_handler_spec[None][404] = not_found
    photolog_app.error_handler_spec[None][500] = server_error
    
    photolog_app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    
    return photolog_app







