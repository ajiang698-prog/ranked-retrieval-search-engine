# 排序检索搜索引擎（Ranked Retrieval Search Engine）

## 项目简介（Overview）

本项目使用 Python 实现了一个基于位置倒排索引的搜索引擎。系统支持文档索引构建，并结合查询词覆盖率、词间距离及词序一致性对检索结果进行排序。

## 功能特点（Features）

- 基于位置的倒排索引（Positional Inverted Index）
- 不区分大小写的搜索
- 词形归一化（lemmatization）
- 支持单复数与动词时态处理
- 基本的标点与数字处理
- 基于一下因素的排序检测：
    - 查询词覆盖率
    - 词项之间的距离
    - 查询词顺序一致性
- 支持显示匹配文本行（`> query` 模式）

## 项目结构（Project Structure）

```
.
├── index.py    # 索引构建
├── search.py   # 查询与排序
├── sample_docs/    # 示例文档
├── requirements.txt    # 依赖文件
└── README.md
```

## 环境配置（Setup）

创建虚拟环境（可选但推荐）
```bash
python -m venv venv
source venv/bin/activate
```

安装依赖:
```bash
pip install -r requirements.txt
```

下载所需的NLTK数据:
```bash
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('punkt_tab')"
python -c "import nltk; nltk.download('wordnet')"
python -c "import nltk; nltk.download('omw-1.4')"
```

## 使用方法（Usage）

### 1. 构建索引
```bash
python index.py sample_docs sample_index
```

### 2. 执行搜索
```bash
python search.py sample_index
```
然后在终端输入查询词进行搜索。

## 示例（Example queries & Output）
查询：

```
garlic bread
> garlic bread
apple
u.s. company
breach
```

输出：

```
> garlic bread
> 1
Garlic bread is very popular in restaurants. 
> 2
Bread garlic combinations appears in some recipes.
> 3
Garlic is used in many traditional dishes.
Bread is often served at the end of the meal.
> 4
Garlic is widely used in cooking.
apple
5
u.s. company
6
9
breach
9
```

## 排序策略（Ranking Strategy）

文档的排序依据如下：

- **覆盖率（Coverage）**：查询词在文档中被匹配到的比例
- **词项距离（Proximity）**：匹配词之间的距离
- **词序一致性（Order）**： 文档中词序顺序是否与查询一致

匹配词越多、词项之间距离越近、且顺序越符合查询的文档，将被赋予更高的排名。

## 说明（Notes）

- 系统同时保留词形还原后的词项（lemmatized tokens）和原始词项，以提升召回率并支持更灵活的匹配方式。
- 本项目最初作为课程项目开发，后续进行了整理和优化，用于展示信息检索系统的实现思路和工程能力。