#! /usr/bin/python

from flask import Flask, jsonify, Response, json, flash, request, redirect, url_for, render_template, session, make_response
from flask_cors import CORS
import mysql.connector as mariadb
import os
from random import *
import string
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import sys

app = Flask(__name__)
CORS(app)

#conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', database='dafuckapi')
#cursor = conn.cursor()
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
SECRET_KEY = 'beetlebob'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

#@app.route('/')
#@app.route('/index')
#def index():
#    return render_template('welcome.html')

#####
# route to submit an image and a caption
#####

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload_image():
    conn = mariadb.connect(user='suckycompanies', password='bgesaw#4', 
            database='suckycompanies')
    cursor = conn.cursor()
    # check to see if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({'message' : 'No file included'})
    file = request.files['file']
    try:
        caption = request.form['caption']
    except NameError:
        pass
    else:
        caption = ''
    if file.filename == '':
        flash('No file selected')
        return jsonify({'message' : 'No file selected'})
    if file and allowed_file(file.filename):
        # shouldn't always have user_id=1
        if valid_user(request.form['user_id'], request.form['sessionvalue']):
            user_id = request.form['user_id']
        else:
            user_id=0
        cursor.execute("INSERT INTO imagemetadata VALUES (null, '', %s, %s, 0)", 
                       (caption, user_id))
        conn.commit()
        image_id = cursor.lastrowid
        filename = str(image_id) + '_' + secure_filename(file.filename)
        cursor.execute("UPDATE imagemetadata SET filename=%s WHERE \
                image_id=%s", (filename, image_id)) 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #this might be able to be done to stream
        image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], 
            filename))
        image.thumbnail((400, 400))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'],
            filename))
        conn.commit()
        conn.close()
        imagePath = "/static/images/" + file.filename
        return jsonify({'imagePath' : imagePath, 'image_id' : cursor.lastrowid})
    else:
        return jsonify({'message' : 'No file or filetype not allowed'})

###
# login
###

@app.route('/login', methods=['POST'])
def login():
    conn = mariadb.connect(user='suckycompanies', password='bgesaw#4', 
            database='suckycompanies')
    cursor = conn.cursor()
    response = jsonify()
    cursor.execute("SELECT password_hash, user_id FROM user WHERE username=%s", 
            (request.form['username'],))
    data = cursor.fetchone()
    if data is not None:
        if check_password_hash(data[0], request.form['password']):
            sessionvalue = ''.join([choice(string.ascii_letters +
                string.digits) for n in range(32)])
            response =  jsonify({'username' : request.form['username'], 
                'userId' : data[1], 'sessioncode' : sessionvalue })
            cursor.execute("UPDATE user SET sessionvalue=%s WHERE user_id=%s",
                    (sessionvalue, data[1]))
            conn.commit()
        else:
            response = jsonify({'userId' : 0 })
    else:
        response = jsonify({'userId' : 0 })
    conn.close()
    return response
    #return res

###
# register
###

@app.route('/register', methods=['POST'])
def register():
    conn = mariadb.connect(user='suckycompanies', password='bgesaw#4', 
            database='suckycompanies')
    cursor = conn.cursor()
    first_hash = generate_password_hash(request.form['password'])
    cursor.execute("INSERT INTO user (user_id, username, password_hash) \
            VALUES (null, %s, %s)", (request.form['username'], first_hash))
    conn.commit()
    conn.close()

    return jsonify({'userId' : cursor.lastrowid})

#####
# route to add a caption
#####

@app.route('/caption', methods=['GET', 'POST'])
def caption():
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    ret_obj = {'message' : request.form['caption'], 
            'image_id' : request.form['imageId']}
    cursor.execute("UPDATE imagemetadata SET caption=%s WHERE image_id=%s", 
            (request.form['caption'], request.form['imageId']))
    conn.commit()
    conn.close()
    return jsonify({'message' : ret_obj})

#####
# route to add an answer
#####

@app.route('/answer', methods=['POST'])
def answer():
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    if (request.form['answer'] == ''): 
        data = {'error' : 'No answer was received'}
        return jsonify(data)
    if valid_user(request.form['user_id'], request.form['sessionvalue']):
        sql = ("INSERT INTO answer VALUES (null, %s, %s, %s, 0, 0)")
        cursor.execute(sql, (request.form['imageId'], request.form['answer'], 
            request.form['user_id']))
    else:
        sql = ("INSERT INTO answer VALUES (NULL, %s, %s, 0, 0, 0)")
        cursor.execute(sql, (request.form['imageId'], request.form['answer'])) 
    sql = "UPDATE imagemetadata SET answer_count=answer_count+1 WHERE \
           image_id=%s"
    cursor.execute(sql, (request.form['imageId'],))
    conn.commit()
    conn.close()
    data = {'answer_id' : cursor.lastrowid}
    return jsonify(data)

#####
# route to get a company given an company_id
# if there is no company_id, just return the 
# most recent company - may change this
#####

# if selected_image is 'user' get just the users
@app.route('/get_company', methods=['GET'])
def get_image():
    conn = mariadb.connect(user='suckycompanies', password='bgesaw#4', 
            database='suckycompanies')
    cursor = conn.cursor()
    response = jsonify()
    response.headers.add('Access-Control-Allow-Headers',
            "Origin, X-Requested-With, Content-Type, Accept, x-auth")
    data = {}
    query = "SELECT name, company_id FROM company \
            ORDER BY company_id DESC LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    last_name = row[0]
    last_id = row[1]
    query = "SELECT name, company_id FROM company \
            ORDER BY company_id LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    first_name = row[0]
    first_id = row[1]
    if request.args['selected_company'] == 'latest':
        data['name'] = last_name
        data['company_id'] = last_id
        conn.close()
        return jsonify(data)
    elif request.args['selected_company'] == 'previous':
        query = "SELECT name, company_id FROM company \
                WHERE company_id < %s ORDER BY company_id DESC LIMIT 1"
        cursor.execute(query, (request.args['companyId'],))
    elif request.args['selected_company'] == 'user_previous':
        if valid_user(request.args['user_id'], request.args['sessionvalue']):
            query = "SELECT name, company_id FROM compaies \
                    WHERE company_id < %s AND user_id = %s ORDER BY company_id \
                    DESC LIMIT 1"
            cursor.execute(query, (request.args['companyId'], request.args['user_id']))
        else:
            data['error'] = 'No results'
            conn.close()
            return jsonify(data)
    elif request.args['selected_company'] == 'next':
        query = "SELECT name, company_id FROM company \
                WHERE company_id > %s LIMIT 1"
        cursor.execute(query, (request.args['companyId'],))
    elif request.args['selected_company'] == 'user_next':
        if valid_user(request.args['user_id'], request.args['sessionvalue']):
            query = "SELECT name, company_id FROM company \
                    WHERE company_id > %s AND user_id = %s ORDER BY company_id \
                    LIMIT 1"
            cursor.execute(query, (request.args['companyId'], request.args['user_id']))
        else:
            data['error'] = 'No results'
            conn.close()
            return jsonify(data)
    elif request.args['selected_company'] == 'most_answers':
        query = "SELECT name, company_id FROM company \
                ORDER BY answer_count DESC LIMIT 1"
        cursor.execute(query)
    elif request.args['selected_company'] == 'user':
        if valid_user(request.args['user_id'], request.args['sessionvalue']):
            query = "SELECT name, company_id FROM company \
                    WHERE user_id = %s ORDER BY company_id DESC LIMIT 1"
            cursor.execute(query, (request.args['user_id'],))
        else:
            data['error'] = 'No results'
            conn.close()
            return jsonify(data)
    else: 
        query = "SELECT name, company_id FROM company \
                WHERE company_id=%s"
        cursor.execute(query, (request.args['companyId'],))
    row = cursor.fetchone()
    if cursor.rowcount < 0:
        data['error'] = 'No results'
        conn.close()
        return jsonify(data)
    data['name'] = row[0] 
    data['company_id'] = row[1] 
    if row[1] == first_id:
        data['companyPosition'] = 'first'
    elif row[1] == last_id:
        data['companyPosition'] = 'last'
    else:
        data['companyPosition'] = 'middle'
    conn.close()
    return jsonify(data) 

@app.route('/get_most_net_upvoted', methods=['GET'])
def get_most_net_upvoted():
    data = []
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4',
            database='dafuckapi')
    cursor = conn.cursor()
    sql = "SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY up-down DESC, answer_id LIMIT 10"
    cursor.execute(sql, (request.args['imageId'],))
    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_most_net_downvoted', methods=['GET'])
def get_most_net_downvoted():
    data = []
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4',
            database='dafuckapi')
    cursor = conn.cursor()
    sql = "SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY down-up DESC LIMIT 10"
    cursor.execute(sql, (request.args['imageId'],))
    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_most_downvoted', methods=['GET'])
def get_most_downvoted():
    data = []
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4',
            database='dafuckapi')
    cursor = conn.cursor()
    sql = "SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY down DESC LIMIT 10"
    cursor.execute(sql, (request.args['imageId'],))
    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_most_upvoted', methods=['GET'])
def get_most_upvoted():
    data = []
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4',
            database='dafuckapi')
    cursor = conn.cursor()
    sql = "SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY up DESC LIMIT 10"
    cursor.execute(sql, (request.args['imageId'],))
    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_most_voted', methods=['GET'])
def get_most_voted():
    data = []
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4',
            database='dafuckapi')
    cursor = conn.cursor()
    sql = "SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY up+down DESC LIMIT 10"
    cursor.execute(sql, (request.args['imageId'],))
    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_answers', methods=['GET'])
def get_answers():
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    data = [] 
    response = jsonify()
    response.headers.add('Access-Control-Allow-Headers',
            "Origin, X-Requested-With, Content-Type, Accept, x-auth")
    sql = ('SELECT answer, answer_id, up, down FROM answer WHERE image_id=%s \
            ORDER BY answer_id DESC LIMIT 10')
    if request.args['answerId'] is '0':
        cursor.execute(sql, (request.args['imageId'],))
    else:
        sql = ('SELECT count(*) AS count FROM answer WHERE answer_id<%s AND \
                image_id=%s ORDER BY answer_id DESC LIMIT 10')
        cursor.execute(sql, (request.args['answerId'], 
            request.args['imageId']))
        if (cursor.fetchone())[0] < 10:
            sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                    image_id=%s ORDER BY answer_id ASC LIMIT 10')
            cursor.execute(sql, (request.args['imageId'],))
        else:
            sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                    answer_id<%s AND image_id=%s ORDER BY answer_id DESC LIMIT 10')
            cursor.execute(sql, (request.args['answerId'], 
                request.args['imageId']))

    for row in cursor.fetchall():
        data.append({ 'answer' : row[0], 'answerId' : row[1],
            'up' : row[2], 'down' : row[3] })
    conn.close()
    response = jsonify(data)
    return response

@app.route('/get_answer', methods=['GET'])
def get_answer():
    # after hitting most answers and then older it's returning the wrong one as the last 
    # entry
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    data = [] 
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    print("1 answerId is " + request.args['answerId'], file=sys.stderr)
    if request.args['answerId'] is '0':
        conn.close()
        return
    print("2 type is " + request.args['type'], file=sys.stderr)
    if request.args['type'] == 'netUp':
        # find the netUp for this answer (what am I going to do about ties?
        # ok, sort by answerId I reckon
        sql = ('SELECT up-down FROM ANSWER WHERE answer_id=%s')
        cursor.execute(sql, (request.args['answerId'],))
        row = cursor.fetchone()
        type_value = row[0]
        print("3 type value is ", file=sys.stderr)
        print(type_value, file=sys.stderr)
    print("4 direction is" + request.args['direction'], file=sys.stderr)
    if request.args['direction'] == 'older':
        # ok, first check if there are any other entries tied in up-down
        # but with answer_id higher than the original
        sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                up-down=%s AND answer_id>%s and image_id=%s ORDER BY \
                answer_id DESC LIMIT 1')
        cursor.execute(sql, (type_value, request.args['answerId'], request.args['imageId']))
        row = cursor.fetchone()
        print("8.1 sql is " + sql, file=sys.stderr)
        if cursor.rowcount > 0:
            data.append({ 'answer' : row[0], 'answerId' : row[1], 
                          'up' : row[2], 'down' : row[3]})
            conn.close()
            print("8.11 data is ", file=sys.stderr)
            print(data, file=sys.stderr)
            return jsonify(data)
        else:
            sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                    up-down<%s AND image_id=%s ORDER BY \
                    up-down DESC, answer_id DESC LIMIT 1')
            cursor.execute(sql, (type_value, request.args['imageId']))
            print("8.12 sql is " + sql, file=sys.stderr)
            row = cursor.fetchone()
            if cursor.rowcount > 0:
                data.append({ 'answer' : row[0], 'answerId' : row[1], 
                              'up' : row[2], 'down' : row[3]})
                conn.close()
                print("8.2 data is ", file=sys.stderr)
                print(data, file=sys.stderr)
                return jsonify(data)
            else:
                res = { 'response' : 'done' }
                conn.close()
                return jsonify(res)
    if request.args['direction'] == 'newer':
        #am I just assuming type is netUp here?  not working for other cases yet?

        # ok first check if there are any other entries tied in up-down
        # but with answer_id lower than the original
        sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                up-down=%s AND answer_id<%s and image_id=%s ORDER BY \
                answer_id DESC LIMIT 1')
        cursor.execute(sql, (type_value, request.args['answerId'], request.args['imageId']))
        row = cursor.fetchone()
        print("8.3 sql is " + sql, file=sys.stderr)
        if cursor.rowcount > 0:
            data.append({ 'answer' : row[0], 'answerId' : row[1], 
                          'up' : row[2], 'down' : row[3]})
            conn.close()
            return jsonify(data)
        else:
            sql = ('SELECT answer, answer_id, up, down FROM answer WHERE \
                    up-down>%s AND image_id=%s ORDER BY \
                    up-down ASC, answer_id DESC LIMIT 1')
            # don't think answer_id has to be less than here
            print("8.4 sql is " + sql, file=sys.stderr)
            cursor.execute(sql, (type_value, request.args['imageId']))
            row = cursor.fetchone()
            if cursor.rowcount > 0:
                data.append({ 'answer' : row[0], 'answerId' : row[1], 
                              'up' : row[2], 'down' : row[3]})
                conn.close()
                print("8.45 data is ", file=sys.stderr)
                print(data, file=sys.stderr)
                return jsonify(data)
            else:
                res = { 'response' : 'done' }
                conn.close()
                return jsonify(res)


        print("8.5 sql is " + sql, file=sys.stderr)
        #i need to find the answer here.  It's always going to include the answer_id that
        # we started with (I think), if that's all there is, then we're 'done'
        # if not, I need to take from the set of values with the up-down equal to 
        # the second one returned that has the highest answer_id
        # I think this might be faster to first for something with up-down equal to the 
        # type_value, but answer_id lower than the one requested limit 1
        # then if I don't find it, 
        
        #find the next value with up-down greater than the original
        # and answer_id lower, sorted by both limit one
        #not sure I should be saying answer)_id is greater than anything here or maybe not be here
        # I shouldn't - I should be getting 359, not 361
    cursor.execute(sql, (request.args['answerId'], request.args['imageId']))
    row = cursor.fetchone()
    if cursor.rowcount > 0:
        data.append({ 'answer' : row[0], 'answerId' : row[1], 
                     'up' : row[2], 'down' : row[3]})
    else:
        res = { 'response' : 'done' }
        return jsonify(res)
    print("9 data is ", file=sys.stderr)
    print(data, file=sys.stderr)
    conn.close()
    return jsonify(data)


@app.route('/get_previous_answer', methods=['GET'])
def get_previous_answer():
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    data = [] 
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    if request.args['answerId'] is '0':
        return
    else:
        sql = ('SELECT answer, answer_id, up, down FROM answer WHERE answer_id>%s \
                AND image_id=%s ORDER BY answer_id ASC LIMIT 1')
        cursor.execute(sql, (request.args['answerId'], request.args['imageId']))
        row = cursor.fetchone()
        if cursor.rowcount > 0:
            data.append({ 'answer' : row[0], 'answerId' : row[1], 
                'up' : row[2], 'down' : row[3] })
        else:
            res = { 'response' : 'newest' }
            return jsonify(res)

    conn.close()
    return jsonify(data)

#need to make sure you can't vote more than once
#get user_id from session
#need a new table of all the answers a user has voted on
@app.route('/vote', methods=['POST'])
def vote():
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    data = {}
    if valid_user(request.form['user_id'], request.form['sessionvalue']):
        sql = ("SELECT user_answer_id, vote FROM user_answer WHERE user_id=%s and \
                answer_id=%s")
        cursor.execute(sql, (request.form['user_id'], request.form['answer_id']))
        row = cursor.fetchone()
        if cursor.rowcount > 0:
            sql = ("UPDATE user_answer SET vote=%s WHERE user_answer_id=%s")
            cursor.execute(sql, (request.form['vote'], row[0]))
            conn.commit()
            if (request.form['vote'] == 'up' and row[1] == 'down'):
                sql = ("UPDATE answer SET up=up+1, down=down-1 WHERE answer_id=%s")
                cursor.execute(sql, (request.form['answer_id'],))
                conn.commit()
            if (request.form['vote'] == 'down' and row[1] == 'up'):
                sql = ("UPDATE answer SET up=up-1, down=down+1 WHERE answer_id=%s")
                cursor.execute(sql, (request.form['answer_id'],))
                conn.commit()
        else:
            sql = ("INSERT INTO user_answer VALUES (null, %s, %s, %s)")
            cursor.execute(sql, (request.form['user_id'], request.form['answer_id'],
                request.form['vote']))
            conn.commit()
            if (request.form['vote'] == 'up'):
                sql = ("UPDATE answer SET up=up+1 WHERE answer_id=%s")
                cursor.execute(sql, (request.form['answer_id'],))
                conn.commit()
            if (request.form['vote'] == 'down'):
                sql = ("UPDATE answer SET down=down+1 WHERE answer_id=%s")
                cursor.execute(sql, (request.form['answer_id'],))
                conn.commit()
        sql = ("SELECT up, down FROM answer WHERE answer_id=%s")
        cursor.execute(sql, (request.form['answer_id'],))
        row = cursor.fetchone()
        conn.close()
        data = {"answer_id" : request.form['answer_id'], "up" : row[0], "down" : row[1]}
        response = jsonify(data)
    else:
        response = jsonify()
        response = jsonify({"message" : "Not a valid user"})

    return response

def valid_user(user_id, sessionvalue):
    conn = mariadb.connect(user='dafuckapi', password='bgesaw#4', 
            database='dafuckapi')
    cursor = conn.cursor()
    sql = ("SELECT user_id FROM user WHERE user_id=%s AND sessionvalue=%s")
    cursor.execute(sql, (user_id, sessionvalue))
    row = cursor.fetchone()
    conn.close()
    if cursor.rowcount >0:
        return True
    else:
        return False




if (__name__ == "__main__"):
    #app.run(host='0.0.0.0')
    app.run(host='127.0.0.1')




#####
# route to add a response to an image
# if sent with a response_id it will edit
# that response
#####



