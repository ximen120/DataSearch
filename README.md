# DataSearch
#项目目标
实现政务公开数据的采集和检索
#项目分阶段
##第一阶段
实现国家统计局结构化数据和数据解读数据的爬取。

采用Hanlp对文本进行解析形成知识库关联结构化和非结构化数据。

实现数据的检索，探索项目的主路线。

主要采用开源框架：Scrapy、ArangoDB、Vue、Hanlp、FastAPI、G2Plot、Scrapyd。

主要开发语言：Python、JavaScript

todo：

~~1、搭建开发环境~~

2、构建统计局数据爬取工程，数据存储到ArangoDB中。

3、通过Hanlp对爬取数据进行关键词、关键短语、命名实体识别，连通数据本身分类和关联关系，构建图谱。

4、通过Vue构建检索前端，从ArangoDB中检索和推荐数据。结构化数据采用G2Plot图表展示，非结构化数据
采用网页展示。
