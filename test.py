from DB import DB as D
import config

DB = D(config.mysql)

print(DB.select('Users', ['num_class'], [['id', '=', '1']], 1))