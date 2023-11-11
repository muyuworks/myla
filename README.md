# Muyu Assistants

## 开发环境设置

### 安装依赖
```
pip install requirements.txt
pip install requirements_dev.txt
```

### 设置环境变量和配置


```
set PYTHONPATH=.

cp env-example.txt .env
```

### 启动

```
./scripts/muyu --reload --extentions ./extentions --vectorstore ./vectorstore --debug
```

## 打包

```
python ./setup.py sdist
```