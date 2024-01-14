from DB import DB as D
import config

DB = D(config.mysql)

print(DB.select('Teams', 'people', [['id', '=', '1']], 1))