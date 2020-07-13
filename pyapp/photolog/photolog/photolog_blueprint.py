# -*- coding: utf-8 -*-
import flask import Blueprint
from photolog.photolog_logger import Log

photolog = Blueprint('photolog', __name__,
                    template_folder='../templates',
                    static_folder='../static')
Log.info('static folder: %s' % photolog.static_folder)
Log.info('template folder: %s' % photolog.template_folder)
                    