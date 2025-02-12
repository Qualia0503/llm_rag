# LLM-RAG 项目



## 安装依赖软件
docker-compose -f milvus-standalone-docker-compose.yml up -d
docker-compose up -d

## 数据库迁移
flask db init
flask db migrate
flask db upgrade

## Milvus初始化
flask dataset_init_milvus

## 启动 celery 队列监听
Linux:
celery -A app.celery worker -c 2 --loglevel INFO -Q dataset --logfile storage/logs/celery_worker.log
Win:
celery -A app.celery worker --loglevel=INFO -Q dataset --logfile=storage/logs/celery_worker.log --pool=solo


## 启动flask服务
flask run --debug




