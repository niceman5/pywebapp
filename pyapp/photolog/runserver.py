# -*- coding: utf-8 -*-
"""
    runserver
    ~~~~~~~~~

    로컬 테스트를 위한 개발 서버 실행 모듈.    
"""
import sys

from photolog import create_app

# 한글 설정관련 세팅
reload(sys)
sys.setdefaultencoding('utf-8')

application = create_app()

if __name__ == '__main__':
    print('starting test server......')
    application.run(host='0.0.0.0', port=5000, debug=True)
