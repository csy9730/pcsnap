# migration

``` sql
alter table Table_1 
add "Order" int null default 99

alter table 表名 
add 字段名 类型 null default 默认值
```


``` sql
alter table todos
add "used_hour" int null
add "plan_hour" int null
add "useragent" varchar(60) default "flanger"
add "finished_at" datetime null

```
### code
``` python

class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)

    name = Column(String(60))
    about = Column(String(660), nullable=True)
    useragent = Column(String(60)) # new

    is_close = Column(Boolean, default=False)
    is_success = Column(Boolean, default=False)
    is_active = Column(Boolean(), default=True)

    # progress = Column(Integer, default=0)
    tag = Column(Enum('weekly', 'work', 'study', 'relax', 'self', 'event'),
                    server_default='weekly',
                    nullable=False)

    created_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)
    updated_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)

    verb_tag = Column(Enum('code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'),
                    server_default='misc',
                    nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))

    is_project = Column(Boolean(), default=False)
    par_id = Column(Integer, ForeignKey('todos.id'), nullable=True)
    depend_id = Column(Integer, ForeignKey('todos.id'), nullable=True)
    
    plan_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True) # new

    stage = Column(Enum('new', 'ss', 'design', 'do', 'log'),
                server_default='new',
                nullable=False)
    progress = Column(Integer, default=0)

    plan_hour = Column(Integer, nullable=True) # new
    used_hour = Column(Integer, nullable=True) # new
```
