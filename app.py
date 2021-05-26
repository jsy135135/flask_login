from flask import Flask, request, session, url_for, make_response, jsonify, render_template, redirect, escape
from jinja2.utils import contextfunction
from werkzeug import useragents
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'fkdjsafjdkfdlkjfadskjfadskljdsfklj'
app.config['JSON_AS_ASCII'] = False


def get_users_data():
    with open('./users_data.json', 'r', encoding='utf8') as file:
        return json.load(file)


def save_users_data(data):
    with open('./users_data.json', 'w', encoding='utf8') as file:
        return file.write(json.dumps(data))


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('data.html', username=username)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = get_users_data()
        for one in data['users_lists']:
            if username == one['username'] and check_password_hash(one['password'], password):
                session['username'] = request.form['username']
                break
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' in session and session['username'] == 'admin':
        if request.method == 'POST':
            return jsonify(get_users_data())
        else:
            return render_template('user.html')
    return redirect(url_for('login'))


@app.route('/user_add', methods=['POST'])
def user_add():
    username = request.json['username']
    password = generate_password_hash(request.json['password'])
    name = request.json['name'] if request.json['name'] else request.json['username']
    user_dict = {
        "username": username,
        "password": password,
        "name": name
    }
    data = get_users_data()
    data['users_lists'].append(user_dict)
    if(save_users_data(data)):
        res = {'code': 0, 'msg': '添加用户成功'}
    else:
        res = {'code': 1, 'msg': '添加用户失败'}
    return jsonify(res)


@app.route('/user_del', methods=['POST'])
def user_del():
    username = request.json['username']
    data = get_users_data()
    res = {'code': 0, 'msg': '删除用户成功'}
    for index, value in enumerate(data['users_lists']):
        # print(index,value)
        if value['username'] == username:
            try:
                del data['users_lists'][index]
                # print(data['users_lists'])
                save_users_data(data)
            except Exception as e:
                res = {'code': 1, 'msg': '删除用户失败'}
            break
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)
