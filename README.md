# PcrWebAssigner 公主连结出刀统计/排刀优化的Web App

Python/Django开发，目前已完成Yobot的主要功能，作为独立于qq的Web App。参与开发请联系q: 951806257。


#### 项目进度
目前已完成：
 - Boss状态，公会成员战斗状态
 - 报刀，伤害统计 (web based)
 
进行中：
 - 尾刀/合刀优化，作为优化整体排刀基础

计划进行：
 - 从QQ-based Bot的数据库进行同步和迁移
 - 排刀算法（动态规划）
 
#### 安装及环境配置（需要Linux系统以及Python3环境，建议Anaconda配置环境）
 
```
git clone https://github.com/ycremar/PcrWebAssigner.git
cd PcrWebAssigner
pip3 install -r requirements.txt
```

#### 数据库迁移以及运行Web Server
```
 python manage.py migrate --run-syncdb
 python manage.py runserver 8080
```
