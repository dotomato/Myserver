import json
import MySQLdb as Ms
import base64


db = Ms.connect('localhost', 'cj', 'cj', 'cj', charset="utf8")
cr = db.cursor()
query = "SELECT userMessage, pointID FROM usermessage "
cr.execute(query)
points = cr.fetchall()
for point in points:
    stt = base64.b64decode(point[0])
    msgjosn = json.loads(stt)
    if 'title' not in msgjosn:
        msgjosn["title"] = "abcd"
        stt2 =base64.b64encode(json.dumps(msgjosn))
        query2 = "UPDATE usermessage SET" \
                " userMessage='%s'" \
                " WHERE pointID='%s'" \
                % (stt2, point[1])
        cr.execute(query2)
        db.commit()
        print 'change'
    else:
        print 'unchange'

db.close()
