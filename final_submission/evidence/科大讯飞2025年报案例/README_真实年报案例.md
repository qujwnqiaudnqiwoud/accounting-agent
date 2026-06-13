# 科大讯飞 2025 年年度报告真实读取案例

本目录保存课程项目的真实年报读取和分析证据，用于证明系统能够从年度报告 PDF 抽取标准财务数据，再进入指标计算、风险识别和报告生成流程。

- 扫描页数：301 / 301 页
- 识别表格与文本：1073 个表格，17921 行表格记录，3804 行文本记录
- 标准化结果：抽取 15 个标准财务科目，覆盖年度 2024、2025
- 核心科目覆盖率：100%
- 数据校验：数据校验完成：通过 7 项，关注 0 项，异常 0 项。
- 分析输出：36 条指标记录，1 条风险提示，13 个 Agent trace 步骤

主要文件：

- `extracted_financial_data.csv` / `.xlsx`：由年报抽取出的标准财务数据。
- `extracted_financial_data_audit.json`：每个核心科目的页码、来源和候选行证据。
- `keda_ratio_results.xlsx`：基于抽取数据计算出的指标表。
- `keda_data_validation.xlsx`：数据完整性和勾稽关系校验表。
- `keda_agent_trace.json`：Agent 工具调用记录。
- `keda_financial_analysis_report.docx`：基于真实年报抽取数据生成的分析报告。