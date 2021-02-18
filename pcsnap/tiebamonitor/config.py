
DB_NAME = 'tiebawatcher'
DB_USER = 'root'
DB_PASSWD = '123456'
DB_HOST = '127.0.0.1'
DB_PORT = 3306

DB = 'sqlite:///tieba_watcher.db'
# DB = 'mysql+pymysql://root:pass@localhost/tieba_watcher'
DB = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB_NAME)
