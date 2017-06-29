#!usr/bin/python
# coding=utf-8

# from flask import Flask, jsonify, make_response, abort, request
from flask import *
import MySQLdb as Ms
# from uwsgidecorators import postfork
import uuid
import time
import random
import hashlib
import base64

app = Flask(__name__)

VERSION = 'v0.01'
APIURL = '/api/' + VERSION
APKSRC = 'http://icon-server.b0.upaiyun.com/web/MapTestV0_01.apk'

# global db



@app.route('/index', methods=['GET'])
def index():
    info = {'VERSION': VERSION, 'APKSRC': APKSRC}
    return render_template('index.html',
                           info=info)


@app.route(APIURL + '/apitest', methods=['GET'])
def apitest():
    data = {'statue': 100,
            'errorMessage': 'no error'}
    return make_response(jsonify(data), 200)


@app.route(APIURL + '/newpoint', methods=['POST'])
def newpoint():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    pd = body['pointData']
    userID2 = body['userID2']

    userID = pd['userID']
    userMessage = base64.b64encode(pd['userMessage'].encode('utf8'))
    latitude = pd['latitude']
    longitude = pd['longitude']

    pointID = genpointid()
    pointTime = int(time.time())
    pointLikeNum = 0

    pd['pointID'] = pointID
    pd['pointTime'] = pointTime

    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "INSERT INTO usermessage set " \
            "pointID='%s'" \
            ",userID='%s'" \
            ",userMessage='%s'" \
            ",latitude=%f" \
            ",longitude=%f" \
            ",pointTime=%d" \
            ",pointLikeNum=%d" \
            % (pointID, userID, userMessage, latitude, longitude, pointTime, pointLikeNum)

    cr.execute(query)
    db.commit()

    result = {'statue': 100,
              'errorMessage': 'no error',
              'pointData': pd}
    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/selectarea', methods=['POST'])
def selectarea():
    data = request.get_data()
    body = json.loads(data)
    print body
    lt_la = body['left_top_latitude']
    lt_lo = body['left_top_longitude']
    rb_la = body['right_bottom_latitude']
    rb_lo = body['right_bottom_longitude']

    points = searchpoint(lt_la, lt_lo, rb_la, rb_lo)
    pointsCount = len(points)

    result = {'statue': 100,
              'errorMessage': 'no error',
              'pointsCount': pointsCount,
              'points': points}
    print result
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/getpoint', methods=['POST'])
def getpoint():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    pointID = body['pointID']

    query = "SELECT pointID,userID,userMessage,latitude,longitude,pointTime,pointLikeNum FROM usermessage " \
            "WHERE pointID='%s'" % pointID

    cr.execute(query)

    point = cr.fetchone()

    if point is None:
        result = {'statue': 101,
                  'errorMessage': 'no match pointID!'}
    else:
        pd = {'pointID': point[0], 'userID': point[1], 'userMessage': point[2], 'latitude': point[3],
              'longitude': point[4], 'pointTime': point[5], 'pointLikeNum': point[6]}
        pd['userMessage'] = base64.b64decode(pd['userMessage'])

        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'pointData': pd}
    print result
    db.close()
    return make_response(jsonify(result), 200)


def searchpoint(lt_la, lt_lo, rb_la, rb_lo):
    # TODO pointscache缓存机制
    pointscache = selectallpoint()
    points = []
    if lt_la > rb_la:
        lt_la, rb_la = rb_la, lt_la
    for point in pointscache:
        if lt_la < point[0] < rb_la and lt_lo < point[1] < rb_lo:
            stt = base64.b64decode(point[4])
            msgjosn = json.loads(stt)
            msgtext = msgjosn['text']
            if len(msgtext) > 15:
                smallMsg = msgtext[:15]
            else:
                smallMsg = msgtext
            userName, userIcon = getNameAndIconByID(point[3])
            userName = base64.b64decode(userName)
            points.append({'latitude': point[0], 'longitude': point[1], 'pointID': point[2],
                           'userID': point[3], 'smallMsg': smallMsg, 'userName': userName, 'userIcon': userIcon})
    return points


def selectallpoint():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    query = "SELECT latitude,longitude,pointID,userID,userMessage FROM usermessage ORDER BY pointTime DESC limit 100"
    cr.execute(query)
    results = cr.fetchall()
    db.close()
    return results


@app.route(APIURL + '/newuser', methods=['POST'])
def newuser():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    userDes = body['userDes']
    if userDes == 'please give me a new ID!':
        pass
    userID = genuserid()
    userIcon = 'no_icon'
    userName = 'user-' + str(random.randint(100000, 999999))
    userDes = ''
    userID2 = hashlib.sha1(userID + str(random.randint(1000000000, 9999999999))).hexdigest()
    userLikeCommentIDList = json.dumps([])
    userLikePointIDList = json.dumps([])

    userNameB64 = base64.b64encode(userName.encode('utf8'))
    userDesB64 = base64.b64encode(userDes.encode('utf8'))

    query = "INSERT INTO userinfo set " \
            "userID='%s'" \
            ",userIcon='%s'" \
            ",userName='%s'" \
            ",userDes='%s'" \
            ",userID2='%s'" \
            ",userLikeCommentIDList='%s'" \
            ",userLikePointIDList='%s'" \
            % (userID, userIcon, userNameB64, userDesB64, userID2, userLikeCommentIDList, userLikePointIDList)

    cr.execute(query)
    db.commit()

    userinfo = {'userID': userID, 'userIcon': userIcon, 'userName': userName,
                'userDes': userDes}
    userinfo2 = {'userinfo': userinfo,
                 'userID2': userID2}
    result = {'statue': 100,
              'errorMessage': 'no error',
              'userinfo2': userinfo2,
              'userLikeCommentIDList': [],
              'userLikePointIDList': []}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/getuser', methods=['POST'])
def getuser():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    userID = body['userID']

    query = "SELECT userID,userIcon,userName,userDes FROM userinfo " \
            "WHERE userID='%s'" % userID

    cr.execute(query)
    duserinfo = cr.fetchone()
    if duserinfo is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
    else:
        userinfo = {'userID': duserinfo[0], 'userIcon': duserinfo[1],
                    'userName': duserinfo[2], 'userDes': duserinfo[3]}
        userinfo['userName'] = base64.b64decode(userinfo['userName'])
        userinfo['userDes'] = base64.b64decode(userinfo['userDes'])
        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'userinfo': userinfo}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/getuserlikecommentidlist', methods=['POST'])
def getuserlikecommentidlist():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    userID = body['userinfo']['userID']
    userID2 = body['userID2']

    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "SELECT userLikeCommentIDList FROM userinfo " \
            "WHERE userID='%s'" % userID

    cr.execute(query)
    duserinfo = cr.fetchone()
    if duserinfo is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
    else:
        ulci = json.loads(duserinfo[0])
        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'userLikeCommentIDList': ulci}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/getuserlikepointidlist', methods=['POST'])
def getuserlikepointidlist():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    userID = body['userinfo']['userID']
    userID2 = body['userID2']

    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "SELECT userLikePointIDList FROM userinfo " \
            "WHERE userID='%s'" % userID

    cr.execute(query)
    duserinfo = cr.fetchone()
    if duserinfo is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
    else:
        ulpi = json.loads(duserinfo[0])
        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'userLikePointIDList': ulpi}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/updateuser', methods=['POST'])
def updateuser():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    userinfo = body['userinfo']
    userID2 = body['userID2']
    userID = userinfo['userID']
    userIcon = userinfo['userIcon']
    userName = userinfo['userName']
    userDes = userinfo['userDes']

    userNameB64 = base64.b64encode(userName.encode('utf8'))
    userDesB64 = base64.b64encode(userDes.encode('utf8'))

    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "UPDATE userinfo SET" \
            " userIcon='%s'" \
            ",userName='%s'" \
            ",userDes='%s'" \
            " WHERE userID='%s'" \
            % (userIcon, userNameB64, userDesB64, userID)
    print query

    cr.execute(query)
    db.commit()

    userinfo = {'userID': userID, 'userIcon': userIcon, 'userName': userName, 'userDes': userDes}
    result = {'statue': 100,
              'errorMessage': 'no error',
              'userinfo': userinfo}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/newcomment', methods=['POST'])
def newcomment():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    userID2 = body['userID2']
    pointID = body['pointID']
    userID = body['userID']
    userComment = body['userComment']

    userCommentB64 = base64.b64encode(userComment.encode('utf8'))

    commentID = uuid.uuid1()
    commentTime = int(time.time())
    commentLikeNum = 0

    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "INSERT INTO usercomment set " \
            "commentID='%s'" \
            ",pointID='%s'" \
            ",userID='%s'" \
            ",userComment='%s'" \
            ",commentTime='%s'" \
            ",commentLikeNum='%s'" \
            % (commentID, pointID, userID, userCommentB64, commentTime, commentLikeNum)

    cr.execute(query)
    db.commit()

    result = {'statue': 100,
              'errorMessage': 'no error'}
    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/getpointcomment', methods=['POST'])
def getpointcomment():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    data = request.get_data()
    body = json.loads(data)
    print body
    pointID = body['pointID']

    query = "SELECT commentID, pointID, userID,userComment,commentTime,commentLikeNum FROM usercomment " \
            "WHERE pointID='%s' ORDER BY commentTime DESC" % pointID

    cr.execute(query)
    commentdata = cr.fetchall()
    if commentdata is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
    else:
        userCommentList = []
        for x in commentdata:
            xt = {'commentID': x[0], 'userID': x[2], 'userComment': x[3],
                  'commentTime': x[4], 'commentLikeNum': x[5]}
            xt['userComment'] = base64.b64decode(xt['userComment'])
            userName, userIcon = getNameAndIconByID(xt['userID'])
            if userName is None or userIcon is None:
                xt['userName'] = '_用户不存在_'
                xt['userIcon'] = 'no_icon'
            else:
                xt['userName'] = base64.b64decode(userName)
                xt['userIcon'] = userIcon

            userCommentList.append(xt)

        userCommentCount = len(userCommentList)
        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'userCommentCount': userCommentCount,
                  'userCommentList': userCommentList}

    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/userlikecomment', methods=['POST'])
def userlikecomment():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    # 解析数据
    data = request.get_data()
    body = json.loads(data)
    print body
    userID = body['userID']
    userID2 = body['userID2']
    commentID = body['commentID']
    isLike = body['isLike']

    # 检查用户密码
    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        db.close()
        return make_response(jsonify(result), 200)

    query = "SELECT userLikeCommentIDList FROM userinfo " \
            "WHERE userID='%s'" % userID

    # 获取用户喜爱列表
    cr.execute(query)
    userLikeCommentIDList = cr.fetchone()
    if userLikeCommentIDList is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
        db.close()
        return make_response(jsonify(result), 200)

    # 更新评论喜爱数
    ulcl = json.loads(userLikeCommentIDList[0])
    query2 = None
    if commentID in ulcl:
        if not isLike:
            ulcl.remove(commentID)
            query2 = "UPDATE usercomment SET commentLikeNum = commentLikeNum-1 " \
                     "WHERE commentID = '%s'" % commentID
            cr.execute(query2)
            db.commit()
    else:
        if isLike:
            ulcl.append(commentID)
            query2 = "UPDATE usercomment SET commentLikeNum = commentLikeNum+1 " \
                     "WHERE commentID = '%s'" % commentID
            cr.execute(query2)
            db.commit()

    # 更新用户喜爱列表
    if query2 is not None:
        ulclt = json.dumps(ulcl)
        query4 = "UPDATE userinfo SET userLikeCommentIDList = '%s' " \
                 "WHERE userID = '%s'" % (ulclt, userID)
        cr.execute(query4)
        db.commit()

    # 获取评论喜爱数
    query3 = "SELECT commentLikeNum FROM usercomment " \
             "WHERE commentID= '%s'" % commentID
    cr.execute(query3)
    commentLikeNum = cr.fetchone()[0]

    result = {'statue': 100,
              'errorMessage': 'no error',
              'isLike': isLike,
              'commentID': commentID,
              'commentLikeNum': commentLikeNum}
    print result
    db.close()
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/userlikepoint', methods=['POST'])
def userlikepoint():
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    # 解析数据
    data = request.get_data()
    body = json.loads(data)
    print body
    userID = body['userID']
    userID2 = body['userID2']
    pointID = body['pointID']
    isLike = body['isLike']

    # 检查用户密码
    if not check_user(userID, userID2):
        result = {'statue': 202,
                  'errorMessage': 'user check failed!'}
        return make_response(jsonify(result), 200)

    query = "SELECT userLikePointIDList FROM userinfo " \
            "WHERE userID='%s'" % userID

    # 获取用户喜爱列表
    cr.execute(query)
    userLikePointIDList = cr.fetchone()
    if userLikePointIDList is None:
        result = {'statue': 200,
                  'errorMessage': 'no match user'}
        db.close()
        return make_response(jsonify(result), 200)

    # 更新评论喜爱数
    ulpl = json.loads(userLikePointIDList[0])
    query2 = None
    if pointID in ulpl:
        if not isLike:
            ulpl.remove(pointID)
            query2 = "UPDATE usermessage SET pointLikeNum = pointLikeNum-1 " \
                     "WHERE pointID = '%s'" % pointID
            cr.execute(query2)
            db.commit()
    else:
        if isLike:
            ulpl.append(pointID)
            query2 = "UPDATE usermessage SET pointLikeNum = pointLikeNum+1 " \
                     "WHERE pointID = '%s'" % pointID
            cr.execute(query2)
            db.commit()

    # 更新用户喜爱列表
    if query2 is not None:
        ulplt = json.dumps(ulpl)
        query4 = "UPDATE userinfo SET userLikePointIDList = '%s' " \
                 "WHERE userID = '%s'" % (ulplt, userID)
        cr.execute(query4)
        db.commit()

    # 获取评论喜爱数
    query3 = "SELECT pointLikeNum FROM usermessage " \
             "WHERE pointID= '%s'" % pointID
    cr.execute(query3)
    pointLikeNum = cr.fetchone()[0]

    result = {'statue': 100,
              'errorMessage': 'no error',
              'isLike': isLike,
              'pointID': pointID,
              'pointLikeNum': pointLikeNum}
    print result
    db.close()
    return make_response(jsonify(result), 200)


def genpointid():
    return "point+" + str(uuid.uuid1())


def genuserid():
    return 'user' + str(uuid.uuid1())


def check_user(userID, userID2):
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    query = "SELECT userID FROM userinfo " \
            "WHERE userID='%s' and userID2='%s'" % (userID, userID2)
    cr.execute(query)
    duserinfo = cr.fetchone()
    db.close()
    if duserinfo is None:
        return False
    return True


def getNameAndIconByID(userID):
    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    cr = db.cursor()

    query = "SELECT userName, userIcon FROM userinfo " \
            "WHERE userID='%s'" % userID
    cr.execute(query)
    row = cr.fetchone()
    db.close()
    if row is None:
        return None, None
    else:
        return row[0], row[1]

# @postfork
def connectmysql():
    # global db

    db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
    print '===================>connect mysql success'


if __name__ == '__main__':
    connectmysql()
    app.run(debug=True, host='0.0.0.0', port=5001)
