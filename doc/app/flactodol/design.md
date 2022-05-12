# todos

### commands
``` bash
foo add "+work+code ladder plan"
foo append -m "ladder plan" -t "work"
foo show
foo show recent
foo finish index
foo drop index
```

## record

### simbol
- %tag
- @car @home @
- \# sss
- +foo
- $
- 


### demos

- main tag
  - work
  - study
  - self
  - weekly misc defalt relax
- verb tag
  - creative
      - new
      - ss
      - debug
      - solve
      - code
      - doc
      - design
      - log/summary/diary
      - law 
  - non-creative activity
      - run/sport
      - dinner
      - clean
      - shop
      - move
      - apply
      - party
      - games
#### 标题和描述
- about
- title
#### 时间
默认添加
-  created_at
-  updated_at


#### 用户
默认配置添加
- 用户
- usergroup
- 用户客户端: zlgmcu_vm, z203, redmi,xcxnth,
- ip addr
- gps

#### 进度
简化成：
- is_active 激活状态：打开（激活），挂起（失活，计划项）
- is_close 存档状态：待完成，完成。
- is_success 成功，不成功（失败） 。


#### project

- depend_id
- par_id
- is_project 

#### privity
- 重要性 基于主标签（work/study）生成默认重要性
- 计划开始时间 planned_at：
- 计划完成时间 finished_at： +1day, +1week, +1month, +1year
- 紧迫性，基于当前时间和完成时间, 可用工时生成
- 优先级： 基于 重要性，紧迫性和难度生成。
- 预估完成工时 plan_hour
- 实际完成工时 used_hour
- 任务难度描述
    - 颗粒度，颗粒度越大，工时越长
    - 复杂度
    - 难度 预估难度，和预估完成工时相关




