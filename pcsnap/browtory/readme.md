# readme


## chrome 

``` json
[{
        "filename": "history",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Bookmarks",
        "rootdir": input,
        "format": "json",
        "description": "json"
    }, {
        "filename": "Cookies",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Login Data",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Preferences",
        "rootdir": input,
        "format": "json",
        "description": "json"
    }, {
        "filename": "Favicons",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }
    ]
```
### history sqlite
#### download
#### keywords
#### visits
visits::
```
id
url 
visit_time
from_visit
transition
segment_id
visit_duration 
publicly_routable
incremented_omnibox_typed_score

```

#### urls
urls
```
id 
url string
title str
visit_count
typed_count
last_visit_time
hidden
```

## router

### base

/urls
/urls/<id>
/visits
/visits/<id>
/domains
/domains/<id>

### pager


### toper/order
/top/recent
/top/visit_count
/top/duration

### filter
/period/today
/period/week
/period/month
/period/year

## view

- table
- bar chart

## misc

引入 tag标注
统计 domain 

对 title 执行 nlp 分析

