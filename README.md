# extract-evernote-tag

使用[bosonnlp](http://bosonnlp.com/)给印象笔记中来自外部收藏的笔记自动提取标签。

###现在标签来自与两部分
1. 通过[关键词提取](http://docs.bosonnlp.com/keywords.html) 提取出来的标签会跟自己印象笔记中的所有的标签取交集作为笔记的标签的一部分。
2. 通过[命名实体识别](http://docs.bosonnlp.com/ner.html) 将地点,人名,组织名,公司名,产品名,职位 直接作为标签。

使用前先申请[bosonnlp](http://bosonnlp.com/)跟 [印象笔记](https://dev.yinxiang.com/doc/) 的API KEY.

将API KEY 写入到config/token.json 文件`{"en_token":"","boson_nlp_token":""}`

`pip install evernote`

`pip install bosonnlp`

`$ python extractTag.py`

