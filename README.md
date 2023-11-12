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

## 开发约定

1. 这个项目中的代码和具体客户的需求无关, 客户的非通用需求需要单独创建项目
2. 通用需求分两类：1) 所有场景都需要的; 2) 某类场景都需要的
3. 第一类需求的解决方案是提供某种机制, 代码放在 muyu 这个 package 中
4. 第二类需求的解决方案是提供某种扩展实现, 代码放在 extentions 这个目录中
5. 建议尽可能把代码拆分成更细的粒度的函数或类
6. 能依赖数据结构的尽量不要依赖数据实例
7. 5、6条以可方便地单独 UT 为标准
8. 需要高频使用或调试的原子功能建议都做成小工具放到 examples 里