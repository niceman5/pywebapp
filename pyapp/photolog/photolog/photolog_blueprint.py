# -*- coding: utf-8 -*-
import flask import Blueprint
from photolog.photolog_logger import log

photolog = Blueprint('photolog', __name__,
                    template_folder='../templates',
                    static_folder='../static')
log.info('static folder: %s' % photolog.static_folder)
log.info('template folder: %s' % photolog.template_folder)
                    