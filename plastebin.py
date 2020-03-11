from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from mrhlab.forms.pastebin import GenerateForm
from mrhlab.extensions import db
from mrhlab.models import Pastebin

import datetime

bp = Blueprint('pastebin', __name__)


def generate_base62(s):
    BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    def base_encode(num, base=62):
        digits = []
        while num > 0:
            remainder = num%base
            digits.append(BASE62[remainder])
            num = num//base
        return ''.join(digits[::-1])
        
    import hashlib
    md5Val = int(hashlib.md5(s.encode('utf-8')).hexdigest(),base=16)
    hashVal = base_encode(md5Val)
    return hashVal
    

@bp.route('/', methods=('GET', 'POST'))
def index():
    form = GenerateForm()
    if request.method == 'POST' and form.validate():
        datetime_ = datetime.datetime.utcnow()
        seed = request.remote_addr + str(datetime_)
        base62val = generate_base62(seed)
        pastebin_= Pastebin(shortlink=base62val, original=form.original.data)
        inserted = False
        while not inserted:
            try:
                db.session.add(pastebin_)
                db.session.commit()
            except:
                datetime_ = datetime.datetime.utcnow()
                seed = request.remote_addr + str(datetime_)
                base62val = generate_base62(seed)
                pastebin_= Pastebin(shortlink=base62val, original=form.original.data)
            else:
                inserted = True
        return form.original.data +' '+base62val
    return render_template('pastebin/index.html', form=form)

@bp.route('/<shorturl>')
def getpaste(shorturl):
    return Pastebin.query.get(shorturl).original
