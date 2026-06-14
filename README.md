# 财报智析 Agent

“财报智析 Agent：基于 smolagents 的上市公司财务报表智能分析系统”是《生成式AI会计前沿》课程期末项目。系统把财务报表分析教材框架转化为可调用的 Agent 工具链，支持从年度报告 PDF/Word 抽取财务数据并生成标准 CSV，也支持直接读取标准 Excel/CSV，随后完成指标计算、趋势分析、杜邦分析、现金流量质量分析、风险识别、图表展示和标准化报告生成。

在线演示地址：[https://accounting-agent-yspsw2afdlis9itfyheqde.streamlit.app/](https://accounting-agent-yspsw2afdlis9itfyheqde.streamlit.app/)

GitHub 仓库：[https://github.com/qujwnqiaudnqiwoud/accounting-agent](https://github.com/qujwnqiaudnqiwoud/accounting-agent)

公网部署说明：项目已完成从本地开发、Agent 架构搭建、API 接入、前端交互到 Streamlit Cloud 在线演示的初步应用闭环。API Key 不写入代码或仓库，可在网页侧边栏临时填写，或在 Streamlit Cloud Secrets 中配置。

## 功能概览

- Streamlit 财务分析工作台：先上传年报 PDF/Word 或标准 Excel/CSV，生成并预览标准 CSV，再点击分析，展示 Agent 工作流、核心指标、图表、风险卡片和报告。
- 教材知识库驱动：`knowledge/` 中的分析框架、指标定义、风险规则、报告模板和提示词会被系统读取。
- 财务数据读取：支持从可复制表格型 PDF/docx 年报抽取财务数据，也支持宽表/长表 Excel、CSV，并自动映射常见中文财务科目。
- 年报抽取增强：PDF 默认全文扫描，综合使用表格抽取、文本行兜底、跨页表头继承、合并报表优先、报告年度识别和核心科目覆盖率校验。
- 数据质量校验：自动检查核心科目完整性、资产负债表勾稽关系和利润现金流匹配性，生成可下载的数据校验表。
- 确定性指标计算：偿债能力、营运能力、盈利能力、成长能力和现金流量质量指标均由 Python 计算。
- 大模型 API 接入：默认支持 DeepSeek OpenAI-compatible API，也可切换通义、智谱、Kimi、OpenAI-compatible 本地服务；安装 smolagents 且配置 API Key 后，主控 Agent 会使用 ToolCallingAgent 规划工具链。
- fallback 演示：未配置 API Key 时仍可完成指标、风险、图表和模板报告生成。

## 技术路线

- 前端：Streamlit
- Agent：smolagents + fallback Python pipeline
- 数据处理：pandas、openpyxl
- PDF/Word：pdfplumber / PyMuPDF / python-docx
- 图表：plotly
- 报告：Markdown + python-docx
- API：OpenAI-compatible 接口，默认 DeepSeek

## 文件结构

```text
accounting-agent/
├── app.py
├── README.md
├── requirements.txt
├── config/
│   ├── settings.py
│   └── model_config.example.yaml
├── knowledge/
├── agents/
├── tools/
├── schemas/
├── data/
├── outputs/
├── notebooks/
└── tests/
```

## 安装与运行

```bash
cd accounting-agent
pip install -r requirements.txt
streamlit run app.py
```

打开网页后，可在左侧侧边栏顶部的“模型 API 配置”区域填写 API Base URL、模型名称和 API Key。如果暂时没有 API Key，可以留空，系统会使用 fallback pipeline 完成课堂演示。

如需用 Jupyter Lab 查看或重新运行课程 Notebook：

```bash
cd accounting-agent
pip install -r requirements.txt
jupyter lab final_submission/财报智析Agent_项目说明_Notebook.ipynb
```

> 注意：`smolagents` 新版本需要 Python 3.10+。如果当前环境是 Python 3.9，`pip install -r requirements.txt` 会跳过 `smolagents`，页面会提示“smolagents 未安装”。这不影响标准数据读取、指标计算、风险识别和报告主流程；API Key 配置后，大模型仍会通过 OpenAI-compatible 接口参与计划生成和报告润色。若需要完整启用 smolagents 主控 Agent，请使用 Python 3.10+ 重建虚拟环境。

## API 配置

默认配置见 `config/model_config.example.yaml`：

```yaml
provider: openai_compatible
api_base: https://api.deepseek.com
model_id: deepseek-v4-flash
api_key_env: DEEPSEEK_API_KEY
temperature: 0.25
max_tokens: 4096
timeout: 120
reasoning_effort: medium
enable_llm: true
```

优先推荐在网页侧边栏直接配置，本次会话输入的 API Key 不会写入本地文件。也可以用环境变量配置：

```bash
export DEEPSEEK_API_KEY="你的真实key"
streamlit run app.py
```

如需长期修改默认模型，复制为 `config/model_config.yaml` 后调整 `api_base`、`model_id` 和 `api_key_env`。不要把真实 API Key 写入配置文件。

## 使用流程

1. 在侧边栏上传年度报告 PDF/docx，或上传已经整理好的标准 Excel/CSV。
2. 点击“读取数据并生成标准 CSV”。
3. 在主页面检查“数据读取结果”，确认科目、年度和数值是否正确，可下载标准 CSV/Excel。
4. 确认无误后点击“开始分析”，Agent 才会进入指标计算、风险识别、图表和报告生成环节。

如果同时上传标准 Excel/CSV 和年报 PDF，系统优先使用 Excel/CSV 作为结构化财务数据，PDF 仅作为报告文本增强材料。

## 标准 CSV/Excel 输入格式

宽表格式：

```text
项目,2022,2023,2024
营业收入,100000,120000,135000
营业成本,60000,76000,89000
净利润,12000,15000,16000
经营活动现金流量净额,13000,11000,18000
总资产,300000,350000,390000
总负债,120000,160000,190000
所有者权益,180000,190000,200000
```

长表格式：

```text
年份,项目,金额
2022,营业收入,100000
2023,营业收入,120000
```

如果只上传 PDF/docx 年报，系统会尝试从报表表格中抽取为上述标准格式。扫描版 PDF 或图片型年报需要先 OCR，否则可能无法识别表格。

## 年报上传与解析

- Streamlit 单个上传文件上限已配置为 1GB，配置文件为 `.streamlit/config.toml`。
- PDF/docx 年报可用于自动抽取标准财务数据；分析前会先生成标准 CSV 供用户核对。
- PDF 年报还可用于文本增强分析，例如补充公司名称、管理层讨论、风险提示和会计政策等背景。
- 系统默认全文扫描 PDF，尽量避免漏掉三大报表。若课堂演示或超大 PDF 需要限制页数，可在启动前设置：

```bash
export FIN_AGENT_REPORT_MAX_PAGES=300
./run_app.sh
```

年报特别大或表格结构复杂时，建议先使用自动抽取结果检查数据；如关键科目缺失，可下载标准 CSV 后手工补充，再上传 CSV 重新分析。
页面会展示扫描页数、识别表格数、核心科目覆盖率、缺失核心科目，并提供 `extracted_financial_data_audit.json` 作为读取证据。扫描版或图片型 PDF 仍需要先 OCR。

## 输出结果

- `outputs/tables/ratio_results.xlsx`：财务指标计算结果。
- `outputs/charts/*.html`：趋势图和风险分布图。
- `outputs/reports/financial_analysis_report.md`：Markdown 报告。
- `outputs/reports/financial_analysis_report.docx`：Word 报告。
- `outputs/agent_trace.json`：Agent 工具调用记录。

## Agent 工作流

1. `llm_model`：加载模型 API 配置。
2. `main_agent`：smolagents ToolCallingAgent 规划工具链；失败时降级为 LLM 计划或受控 Python 管线。
3. `file_loader`：读取标准财务数据 CSV/Excel。
4. `pdf_parser`：解析 PDF，可跳过。
5. `data_cleaner`：标准化财务科目。
6. `data_validator`：校验核心科目完整性、资产负债表勾稽关系和利润现金流匹配性。
7. `ratio_calculator`：计算财务指标。
8. `trend_analyzer`：分析趋势。
9. `dupont_analyzer`：执行杜邦分析。
10. `cashflow_analyzer`：评价现金流量质量。
11. `risk_detector`：识别异常风险。
12. `chart_generator`：生成图表。
13. `report_generator`：生成报告。

## 课程提交建议

最终提交时建议只打包课程所需文件，不要把虚拟环境、缓存、大型临时上传文件一起提交。推荐保留：

- `app.py`、`agents/`、`tools/`、`schemas/`、`config/`、`knowledge/`
- `data/sample_financial_data.xlsx`
- `notebooks/demo.ipynb`
- `tests/`
- `README.md`、`requirements.txt`、`run_app.sh`
- `final_submission/` 中的课程报告、题目说明、提交清单和附录材料

建议排除：`.venv/`、`__pycache__/`、`.pytest_cache/`、`.DS_Store`、`outputs/uploads/`、运行中生成的大体积临时文件。

## 常见问题

- **在哪里配置 API Key？** 在 Streamlit 左侧侧边栏顶部的“模型 API 配置”区域直接粘贴 API Key 即可，也可以使用环境变量。
- **没有 API Key 能不能演示？** 可以。系统会显示 API 未配置，并使用规则管线生成报告。
- **为什么输入 API Key 后仍提示 smolagents 未安装？** API Key 是远程模型服务凭证，`smolagents` 是本地 Python 包。当前 Python 版本低于 3.10 时依赖会被跳过，此时系统仍可用 API 生成计划/报告，但工具调度会使用 fallback pipeline。
- **为什么不让模型直接算指标？** 财务数字必须可追溯，指标由 Python 确定性计算，模型只做调度说明和语言组织。
- **可以替换教材框架吗？** 可以。替换 `knowledge/` 下对应文件即可。

## 课堂演示建议

1. 打开 Streamlit 页面，介绍“教材框架驱动”和“Agent 工具调用流程”。
2. 上传 `data/sample_financial_data.xlsx`，或上传可复制表格型 PDF/docx 年报。
3. 点击“读取数据并生成标准 CSV”，检查数据读取结果。
4. 点击“开始分析”，展示 Agent trace。
5. 展示核心指标卡片、趋势图和风险识别卡片。
6. 打开报告 Tab，并下载 Markdown/Word 报告。

## Word 报告渲染检查

项目内置了不依赖 LibreOffice 的 DOCX 预览渲染器。它使用 `python-docx` 读取 Word 内容，并通过 PyMuPDF 生成审阅用 PDF 和每页 PNG，避免 LibreOffice 动态库缺失导致渲染失败。

```bash
cd accounting-agent
.venv/bin/python scripts_render_docx.py final_submission/财报智析Agent_课程报告.docx --output-dir outputs/rendered_docs/course_report
.venv/bin/python scripts_render_docx.py final_submission/财报智析Agent_作业题目说明.docx --output-dir outputs/rendered_docs/topic_doc
```

输出目录会包含 `.html`、`.pdf` 和 `page-001.png` 等页面预览。该渲染结果用于提交前检查空白页、乱码和明显排版问题，不依赖系统 LibreOffice。

## 免责声明

本系统输出仅作为课程研究与财务分析参考，不构成投资建议或审计意见。
