# todos


记录和管理待办事项，计划，项目。

## usage
### commands
``` bash
foo add "+work+code ladder plan"
foo append -m "ladder plan" -t "work"
foo show
foo show recent
foo finish index
foo drop index
```

### simbol
- %tag 描述tag
- @car @home @
- \# sss
- +foo 描述tag
- $ 
- 


### demos

- main tag
  - work 工作事务 
  - study 学习相关
  - self 个人相关
  - weekly 日常事务 monthly diary
  - misc 杂类 defalt 缺省
  - relax 休闲事务


- verb tag
  - creative
      - new 提出需求
      - ss 搜索
      - solve/debug 解决问题
      - test/benchmark 单元测试，跑分
      - code 代码编程
      - doc 文档
      - pdf/read 阅读
      - design 设计
      - log/diary 记录，日记
      - abs/summary 总结
      - law 规定，约定
      - install 安装软件，安装硬件（电脑，桌子）
      - tool 工具
      - discussion 讨论
  - non-creative activity
      - self
          - body
      - weekly
          - dinner 吃饭，大餐，聚餐
          - clean/wash 清洁 洗澡
          - fetch 获取快递
          - shop 网上购物
          - mall 商场购物
          - apply 网上申请，注册
          - office 办事处
          - driving/hitchhikers 顺风车
          - traffic/move 交通
          - party/meeting/greet 开会，聚会
          - homing/ move 回家
          - sport
              - run 跑步
          - call/summon 召唤
          - fix 修理
      - relax 
          - games 游戏
              - wzry 王者荣耀

#### 标题和描述
- about
- title


#### 时间
默认添加
-  created_at
-  updated_at



### table


- 用户列表
- 任务列表
- 工时管理



#### 用户
默认配置添加
- 用户
- usergroup
- 用户客户端: zlgmcu_vm, z203, redmi,xcxnth,
- ip addr
- gps

**Q**: 问题： 用户客户端，和todo是什么关系？

**A**: todo有new update，query，delete 四种操作，
每种操作有可能改变 用户客户端，如何处理这种不统一？
UA 应该和user绑定么？

- required machine
    - pc
    - mobile device
        - phone
        - pad


#### 进度
简化成：
- is_active 激活状态：打开（激活），挂起（失活，计划项）
    - depend_id 完成时 更改 is_active 状态
    - plan_at 到达
    - 更改 is_active 状态
- is_close 存档状态：待完成，完成。
- is_success 成功，不成功（失败） 。

#### task


- todo: tag
- project: is_project  par_id
- plan: finished_at plan_at is_active depend_id
- log: status
- workhour: plan_hour used_hour


- add_plan  finished_at plan_at
- add_todo
    - add depend todo
- add_project 
- add_log
- add_workhour


#### project

- depend_id 指定依赖任务，当前任务依赖depend id 任务。
    - 和 is_active 联动，需要依赖任务完成，依赖任务才会激活
    - 支持树形结构，多个任务可以依赖一个任务；不支持反树形结构，一个任务依赖多个任务，
    - 支持串行结构，上一个任务完成开始下一个任务
- par_id
- is_project 

##### 任务关联流程
(depend_id -> pro_delay) -> (prev_delay -> plan_at -> delay -> finished_at -> pro_delay)

#### privity
- 重要性importance 基于主标签（work/study）生成默认重要性
- 计划开始时间 planned_at：
- 计划完成时间 finished_at： +1day, +1week, +1month, +1year
- 截至时间 dead_date
- 紧迫性，基于当前时间和完成时间, 可用工时生成
- 优先级prior： 基于 重要性，紧迫性和难度生成。
- 预估完成工时 plan_hour
- 实际完成工时 used_hour
- 任务难度描述
    - 颗粒度，颗粒度越大，工时越长
    - 复杂度
    - 难度 预估难度，和预估完成工时相关
- 冷却时间 cooldown



#### 自动生成每周任务

taskGenerater: 
- period 周期


## 3


- 车辆保养
- 代码同步
- 疫情 接口
- 提前还款 计划


#### 场景
如何描述当前性，场景匹配性

- pc
- pad
- mobile
- wifi
- car
- bike
- walk

- location
  - work
      - zlg work +mobile +pc
  - home 
      - z203 +mobile +pad +pc +wifi +bed
      - xcxnth +mobile +pad +pc +wifi +bed
  - family
      - whxnlb +mobile +pad +pc +wifi +bed
      - vukgcp +mobile +pad +pc +wifi +bed
  - traffic 
      - car  +mobile
      - subway +mobile
      - walk +mobile
      - bike 
      - train +mobile
  - guest
      - +mobile
- datetime
    - workday
      - working time
      - life time
          - dinner time
          - washing time
      - study time
      - relax time
      - sleep time
    - weekend
      - 

代办事项，默认屏蔽项目，只显示合适项目


##### demnd

- 排列，sort
- 安排，Arrange
- put
- 放置 place
- 归类 categorize classify
- 归位，homing
- 处置 dispose
- 丢弃，discard
- 整理，整洁，整理衣服，清理，tidy

- 办事大厅，council
- 政务厅， Business lobby
- 办事处，office
- 顺风车，搭便车，hitchhiking

- 市场，Market
- 商场，shopping mall
- 逛街 ，shopping
- purchase, 
- 网购，online shopping,
- 电子商城 electronic mall
