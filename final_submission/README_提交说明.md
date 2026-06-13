# 财报智析 Agent 期末提交说明

## 提交前可选补充

- 如老师要求，可补充系统运行截图或课堂演示截图。
- 课程报告已补充投资者互动平台案例、经管期刊文献、智能财经平台应用对比和本项目解决路径。
- `final_submission/evidence/科大讯飞2025年报案例/` 已保存真实年报读取证据，包括标准 CSV、抽取审计 JSON、指标表、数据校验表、Agent trace 和真实案例 Word 报告。
- `final_submission/evidence/运行输出样例/` 已保存指标表、校验表、图表 HTML、分析报告和 Agent trace。
- `final_submission/evidence/文档渲染预览/` 保存 Word 文档渲染后的 PDF、HTML 和页面总览 PNG。

## 推荐运行方式

```bash
cd accounting-agent
pip install -r requirements.txt
streamlit run app.py
```

如需查看或重新执行课程 Notebook：

```bash
cd accounting-agent
pip install -r requirements.txt
jupyter lab final_submission/财报智析Agent_项目说明_Notebook.ipynb
```

如需使用大模型 API，可在网页侧边栏顶部填写 API Key，或在终端设置：

```bash
export DEEPSEEK_API_KEY="你的真实key"
streamlit run app.py
```

## 推荐打包方式

最终压缩包建议命名为：

`选题二_财报智析Agent_徐北辰.zip`

打包时不要包含 `.venv/`、`__pycache__/`、`.pytest_cache/`、`.DS_Store`、大体积临时上传文件。

## Word 渲染检查

本项目已改用不依赖 LibreOffice 的渲染脚本，提交前可以运行：

```bash
.venv/bin/python scripts_render_docx.py final_submission/财报智析Agent_课程报告.docx --output-dir outputs/rendered_docs/course_report
.venv/bin/python scripts_render_docx.py final_submission/财报智析Agent_作业题目说明.docx --output-dir outputs/rendered_docs/topic_doc
```

输出目录中的 PDF 和 PNG 用于检查是否有空白页、乱码或明显排版问题。
