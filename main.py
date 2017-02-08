# from flask import Flask, jsonify, make_response, abort, request
from flask import *
import MySQLdb as Ms

app = Flask(__name__)

VERSION = 'v0.01'
APIURL = '/api/' + VERSION
cr = None
db = None


@app.route(APIURL + '/apitest', methods=['GET'])
def index():
    q = request.args.get('q')
    data = {'statue': q,
            'data': ['string 0', 'string 1']}
    return make_response(jsonify(data), 200)


@app.route('/sayhello', methods=['GET'])
def sayhello():
    user = {'name': 'HLH'}
    return render_template('sayhello.html',
                           user=user)


@app.route(APIURL + '/newpoint', methods=['POST'])
def newpoint():
    data = request.get_data()
    body = json.loads(data)
    userID = body['userID']
    userMessage = body['message']
    latitude = body['latitude']
    longitude = body['longitude']

    query = "INSERT INTO usermessage set " \
            "userID='%s'" \
            ",userMessage='%s'" \
            ",latitude=%f" \
            ",longitude=%f" \
            % (userID, userMessage, latitude, longitude)

    print query
    cr.execute(query)
    db.commit()

    result = {'statue': 100,
              'pointID': userID + 'PointID test'}
    print result
    return make_response(jsonify(result), 200)


def connectmysql():
    mdb = Ms.connect('localhost', 'server-machine', 'server1234567890', 'maptestv0_01')
    mcr = mdb.cursor()
    return mdb, mcr


db, cr = connectmysql()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
