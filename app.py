import gzip
import json
import os
import traceback
from hashlib import sha1

import requests
import sqlite3

from time import time
from flask import Flask, request, Response, g, abort, render_template
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv('.env')
env_config = os.environ.get('CONFIGURATION_SETUP', 'config.ProdConfig')
app.config.from_object(env_config)


def create_tables(db):
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('temp.db')
        create_tables(db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def xstr(s):
    return '' if s is None else str(s)


def get_target():
    return xstr(os.environ.get('NSLITE_TARGET', app.config.get('NSLITE_TARGET', '')))


def get_api_secret():
    return xstr(os.environ.get('API_SECRET', app.config.get('API_SECRET', '')))


def minutes_from_now(minutes):
    return int(time() * 1000) + minutes * 60 * 1000


@app.route('/')
def index():
    return render_template('index.html', messages=get_messages())


@app.route('/nslite/api/sgv')
def sgv_data():
    with get_db() as db:
        x_tab = []
        y_tab = []
        for x, y in db.cursor().execute(
                'SELECT sgv_date, sgv_value FROM sgv WHERE sgv_date BETWEEN ? AND ? ORDER BY sgv_date',
                (minutes_from_now(-180), minutes_from_now(10))).fetchall():
            x_tab.append(int(x / 1000))
            y_tab.append(y)

        return json.dumps([x_tab, y_tab])


def get_messages():
    messages = []

    if len(get_target()) == 0:
        messages.append('NSLITE_TARGET is not set. Data is not forwarded to your Nightscout page.')

    if len(get_api_secret()) == 0:
        messages.append('API_SECRET is not set. Data is not being loaded into NS lite.')

    return messages


@app.route('/api/v1/entries', methods=['POST'])
def api():
    try:
        removed_old = False
        for sgv in extract_data(request):
            with get_db() as db:
                if not removed_old:
                    db.cursor().execute('DELETE FROM sgv WHERE sgv_date < ? or sgv_date IS NULL',
                                        (minutes_from_now(-180),))
                    removed_old = True
                db.cursor().execute('INSERT INTO sgv (sgv_date, sgv_value) VALUES (?, ?)', (sgv[1], sgv[0]))
                db.commit()
    except:
        # forwarding more important than local data
        print('[ERROR] ' + traceback.format_exc())

    return forward_request(request)


@app.route('/<path:any_path>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def default(any_path):
    return forward_request(request)


def extract_data(req):

    if req.data[:2] == b'\x1f\x8b':
        data = json.loads(gzip.decompress(req.data))
    else:
        data = json.loads(req.data)

    if not isinstance(data, list):
        data = [data]

    result = []
    api_secret_ok = False

    for single_req in data:
        if 'sgv' in single_req and 'date' in single_req:
            if api_secret_ok or sha1(get_api_secret().encode('utf-8')).hexdigest() == req.headers.get('api-secret'):
                api_secret_ok = True
                result.append((int(single_req['sgv']), int(single_req['date'])))

    return result


def forward_request(req):
    if len(get_target()) > 0:
        try:
            resp = requests.request(
                method=req.method,
                url=req.url.replace(req.host, get_target()),
                headers={key: value for (key, value) in req.headers if key not in ('Host', 'Transfer-Encoding')},
                data=req.data,
                cookies=req.cookies)
        except requests.exceptions.ConnectionError:
            abort(404)

        response = Response(resp.content, resp.status_code, resp.raw.headers.items())
        return response
    else:
        abort(404)


if __name__ == '__main__':
    app.run()
