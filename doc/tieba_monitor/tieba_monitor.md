# tieba_monitor

## model

- [ ] add tiezi
- [ ] add tiezi.log
- [ ] add mariadb
- [ ] add user


## crawler

- [x] code: parse request.html
- [x] add: rstrip 
- [x] add: reverse 

## flask viewer

- [x] add: href
- [x] add: pagination


### flask

### html

- [x] add: boostrap html


## misc


* mysql 用utf8 保存 emoji，出现乱码，无法处理

**A**: 
1. utf8mb4
2. 过滤脏字符 （failed）
3. base64 转码



**Q**: sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1049, "Unknown database abc

**A**:  手动在mysql 中创建database abc 。