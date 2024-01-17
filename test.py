from DB import DB as D
import config
import json

DB = D(config.mysql)

data = []
data.append('1.jpeg')
print(DB.update('Tasks', {'files': json.dumps(data)}, [['id', '=', '1']]))