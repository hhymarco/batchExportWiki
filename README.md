# batchExportWiki
批量导出wiki

## 特点
可遍历导出子目录中的页面

## 使用说明
1. 提前安装requests和pyquery，安装中可能遇到问题请自行搜索，网上有通用解决方案；
2. 找到cookie中的jsessionid填入cookieString，供导出请求使用；
3. wiki_page_url是树根节点页面的url，也就是要导出的根目录；
4. wiki_title是在本地生成的目录名；
5. dir指定导出到本地哪个目录；
6. export_wiki方法中的export_url目前是导出word的链接，可以改成导出pdf的%s/spaces/flyingpdf/pdfpageexport.action?pageId=%s；