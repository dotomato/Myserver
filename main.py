#!usr/bin/python
# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用。

# from flask import Flask, jsonify, make_response, abort, request
from flask import *
import MySQLdb as Ms
from uwsgidecorators import postfork
import uuid

app = Flask(__name__)

VERSION = 'v0.01'
APIURL = '/api/' + VERSION
cr = None
db = None


@app.route(APIURL + '/apitest', methods=['GET'])
def apitest():
    data = {'statue': 100}
    return make_response(jsonify(data), 200)


@app.route('/sayhello', methods=['GET'])
def sayhello():
    user = {'name': 'HLH'}
    return render_template('sayhello.html',
                           user=user)


def genpointid():
    return uuid.uuid1()


@app.route(APIURL + '/newpoint', methods=['POST'])
def newpoint():
    data = request.get_data()
    body = json.loads(data)
    pd = body['pointData']

    userID = pd['userID']
    userMessage = pd['userMessage']
    latitude = pd['latitude']
    longitude = pd['longitude']

    pointID = genpointid()

    pd['pointID'] = pointID

    query = "INSERT INTO usermessage set " \
            "pointID='%s'" \
            ",userID='%s'" \
            ",userMessage='%s'" \
            ",latitude=%f" \
            ",longitude=%f" \
            % (pointID, userID, userMessage, latitude, longitude)

    cr.execute(query)
    db.commit()

    result = {'statue': 100,
              'errorMessage': 'no error',
              'pointData': pd}
    print result
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
    data = request.get_data()
    body = json.loads(data)
    pointID = body['pointID']

    query = "SELECT pointID,userID,userMessage,latitude,longitude FROM usermessage " \
            "WHERE pointID='%s'" % pointID

    cr.execute(query)

    point = cr.fetchone()

    if point is None:
        result = {'statue': 101,
                  'errorMessage': 'no match pointID!'}
    else:
        pd = {'pointID': point[0], 'userID': point[1], 'userMessage': point[2], 'latitude': point[3],
              'longitude': point[4]}
        result = {'statue': 100,
                  'errorMessage': 'no error',
                  'pointData': pd}
    print result
    return make_response(jsonify(result), 200)


def selectallpoint():
    query = "SELECT latitude,longitude,pointID FROM usermessage"
    cr.execute(query)
    results = cr.fetchall()
    return results


def searchpoint(lt_la, lt_lo, rb_la, rb_lo):
    pointscache = selectallpoint()
    points = []
    if lt_la > rb_la:
        lt_la, rb_la = rb_la, lt_la
    for point in pointscache:
        if lt_la < point[0] < rb_la and lt_lo < point[1] < rb_lo:
            points.append({'latitude': point[0], 'longitude': point[1], 'pointID': point[2]})
    return points


@postfork
def connectmysql():
    mdb = Ms.connect('localhost', 'server-machine', 'server1234567890', 'maptestv0_01', charset="utf8")
    mcr = mdb.cursor()
    print '===================>connect mysql success'

    global db
    global cr
    db, cr = mdb, mcr


if __name__ == '__main__':
    connectmysql()
    app.run(debug=True, host='0.0.0.0', port=5001)
