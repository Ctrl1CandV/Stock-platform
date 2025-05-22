# 集成多维度股票分析的模拟证券交易平台

浙大城市学院计算机与计算科学学院软件工程2102班刘逸杰毕业设计，版本号：1.2.2

# 项目启动
在此之前需要保证已经安装了Docker和Docker-Compose

```shell
cd Stock-platform
docker-compose build
# 如果无法pull python,node和mysql,使用vpn和docker pull进行单独拉取 

# 在项目运行前确保.env的RUN_ENVIRONMENT = DOCKER且RUN_MODE = TEST
docker-compose up
# 后端运行时会报错，这是因为pandas_ta的文件错误
# 在docker中手动到usr/local/lib/python3.12/site-packages/pandas_ta/momentum/squeeze_pro.py
# 将第二行的NaN改为nan

# 进入到后端的exec界面进行数据迁移
python manage.py makemigrations
python manage.py migrate

# 更改RUN_MODE = NORMAL后，再次启动并访问
localhost:8080
```