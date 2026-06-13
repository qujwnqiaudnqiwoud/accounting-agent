# 标准化财务报表分析报告模板

> 基于张新民、钱爱民《财务报表分析（第6版）》分析框架
> 版本：v1.0

---

# {{公司名称}} 财务报表分析报告

**报告期间**：{{start_year}}年度 — {{end_year}}年度
**报告日期**：{{report_date}}
**分析工具**：财务报表分析 Agent v1.0
**数据来源**：{{data_source_description}}

---

## 一、公司基本情况

### 1.1 公司概况

{{company_name}}（证券代码：{{stock_code}}）是一家主要从事{{main_business}}的上市公司，
属于{{industry_classification}}行业。截至{{latest_report_date}}，公司总资产{{total_assets}}亿元，
净资产{{net_assets}}亿元，全年实现营业收入{{revenue}}亿元。

### 1.2 行业背景

公司所属的{{industry_name}}行业目前处于{{lifecycle_stage}}阶段，行业集中度{{concentration}}。
主要竞争者包括{{competitors}}。近年来行业面临的主要挑战包括{{industry_challenges}}。

> **本节写作目标**：提供分析对象的基本背景
> **数据来源**：公司年报、Wind数据库、行业协会
> **标准分析思路**：行业生命周期判断 + 竞争格局描述 + 政策环境影响
> **应避免的错误**：避免过度展开与财务分析无关的行业细节

---

## 二、分析数据来源与方法说明

### 2.1 数据来源

| 数据类型 | 来源 | 期间 | 备注 |
|---|---|---|---|
| 财务报告 | {{company_name}}年度报告 | {{year_range}} | 经{{auditor}}审计，{{audit_opinion}} |
| 行业数据 | {{industry_data_source}} | {{year_range}} | — |

### 2.2 分析方法

本报告采用的分析方法包括：
1. **战略视角分析**：从资产结构透视经营战略，从资本结构透视融资战略（基于张新民"企业财务状况质量分析理论"）
2. **质量分析**：资产质量、资本结构质量、利润质量、现金流量质量四维分析
3. **比率分析**：偿债能力、营运能力、盈利能力、成长能力四大类指标体系
4. **趋势分析**：对近{{n_years}}年财务数据进行趋势分析
5. **杜邦分析**：运用杜邦分析体系分解净资产收益率驱动因素
6. **横向比较**：与同行业可比公司进行对比（{{peers}}）

### 2.3 分析框架

```
战略分析 → 会计质量判断 → 四表质量分析 → 专项能力分析 → 综合分析与评价 → 风险提示
```

> **本节写作目标**：建立分析的可靠性基础
> **应避免的错误**：不能省略审计意见类型的说明；行业数据来源必须真实可查

---

## 三、主要财务数据概览

### 3.1 关键财务数据一览

| 项目（亿元） | {{year_1}} | {{year_2}} | {{year_3}} | 三年复合增长率 |
|---|---|---|---|---|
| 总资产 | {{ta_1}} | {{ta_2}} | {{ta_3}} | {{ta_cagr}}% |
| 净资产 | {{na_1}} | {{na_2}} | {{na_3}} | {{na_cagr}}% |
| 营业收入 | {{rev_1}} | {{rev_2}} | {{rev_3}} | {{rev_cagr}}% |
| 净利润 | {{np_1}} | {{np_2}} | {{np_3}} | {{np_cagr}}% |
| 经营活动现金流净额 | {{ocf_1}} | {{ocf_2}} | {{ocf_3}} | — |

### 3.2 核心指标速览

| 指标 | {{year_1}} | {{year_2}} | {{year_3}} | 行业均值（{{latest_year}}） |
|---|---|---|---|---|
| ROE | {{roe_1}}% | {{roe_2}}% | {{roe_3}}% | {{roe_ind}}% |
| 资产负债率 | {{dar_1}}% | {{dar_2}}% | {{dar_3}}% | {{dar_ind}}% |
| 毛利率 | {{gm_1}}% | {{gm_2}}% | {{gm_3}}% | {{gm_ind}}% |
| 利润含金量 | {{pq_1}}% | {{pq_2}}% | {{pq_3}}% | — |

> **本节写作目标**：让读者在30秒内获得公司财务的核心印象
> **模板表达**："截至{{latest_date}}，公司总资产{{ta}}亿元，三年复合增长率{{cagr}}%。ROE近三年分别为{{values}}，呈{{trend}}趋势。"
> **应避免的错误**：只列数字不做任何概括性文字

---

## 四、资产负债表分析

### 4.1 资产结构分析

**总资产规模变化**：
公司总资产从{{ta_start}}亿元增长至{{ta_end}}亿元，增幅{{ta_change}}%，年均复合增长率{{ta_cagr}}%。

**资产结构特征**（张新民战略视角分类）：

| 资产类别 | 金额（亿元） | 占比 | 同比变动 |
|---|---|---|---|
| 经营性资产 | {{oa}} | {{oa_pct}}% | {{oa_delta}}% |
| 投资性资产 | {{ia}} | {{ia_pct}}% | {{ia_delta}}% |
| 流动资产 | {{ca}} | {{ca_pct}}% | {{ca_delta}}% |
| 非流动资产 | {{nca}} | {{nca_pct}}% | {{nca_delta}}% |

**战略解读**：{{strategy_interpretation}}

### 4.2 资产质量分析

**流动资产质量**：

1. **货币资金质量**：{{cash_quality_assessment}}
2. **应收账款质量**：应收账款{{ar}}亿元，周转天数{{ar_days}}天。{{ar_quality_assessment}}
3. **存货质量**：存货{{inv}}亿元，周转天数{{inv_days}}天。{{inv_quality_assessment}}

**非流动资产质量**：

1. **固定资产**：成新率{{fa_new_rate}}%。{{fa_assessment}}
2. **在建工程**：{{cip}}亿元，占总资产{{cip_pct}}%。{{cip_assessment}}
3. **商誉**：{{gw}}亿元，占净资产{{gw_pct}}%。{{gw_assessment}}
4. **无形资产**：{{ia_assets}}亿元。{{ia_assessment}}

**资产质量综合评价**：{{asset_quality_summary}}

### 4.3 资本结构分析

**负债结构**：

| 负债类型 | 金额（亿元） | 占比 |
|---|---|---|
| 金融性负债（有息） | {{fin_liab}} | {{fin_liab_pct}}% |
| 经营性负债（无息） | {{op_liab}} | {{op_liab_pct}}% |
| 流动负债 | {{cl}} | {{cl_pct}}% |
| 非流动负债 | {{ncl}} | {{ncl_pct}}% |

**所有者权益结构**：

| 权益来源 | 金额（亿元） | 占比 |
|---|---|---|
| 外部输血（股本+资本公积） | {{external}} | {{ext_pct}}% |
| 内部造血（盈余公积+未分配利润） | {{internal}} | {{int_pct}}% |

造血输血比：{{ratio}}%。{{ratio_interpretation}}

> **本节写作目标**：从战略视角揭示资产负债表背后的经营逻辑
> **标准分析思路**：整体规模 → 结构特征 → 各项目质量 → 综合判断
> **模板表达**："从资产结构来看，公司经营性资产占比{{oa_pct}}%，属于{{asset_strategy_type}}企业。从资本结构来看，公司造血输血比为{{ratio}}%，{{interpretation}}。"

---

## 五、利润表分析

### 5.1 收入质量分析

公司近三年营业收入分别为{{rev_values}}亿元，同比增长{{rev_growth_values}}%。

收入现金比率：{{cash_ratio_values}}%。{{cash_ratio_assessment}}

收入构成（分产品/行业/地区）：{{revenue_breakdown}}

前五大客户集中度：{{top5}}%。{{top5_assessment}}

关联销售占比：{{related_sales}}%。{{related_assessment}}

### 5.2 利润结构分析

| 利润层次 | 金额（亿元） | 占收入比 |
|---|---|---|
| 毛利 | {{gp}} | {{gp_pct}}% |
| 核心利润 | {{cp}} | {{cp_pct}}% |
| 营业利润 | {{op}} | {{op_pct}}% |
| 利润总额 | {{tp}} | {{tp_pct}}% |
| 净利润 | {{np}} | {{np_pct}}% |

毛利率趋势：{{gm_trend_assessment}}

核心利润率趋势：{{cpm_trend_assessment}}

非经常性损益分析：非经常性损益{{nonrec}}亿元，占净利润{{nonrec_pct}}%。{{nonrec_assessment}}

投资收益分析：投资收益{{inv_income}}亿元，占营业利润{{inv_pct}}%。{{inv_assessment}}

### 5.3 费用质量分析

| 费用项目 | 金额（亿元） | 费用率 | 同比变动 | 行业均值 |
|---|---|---|---|---|
| 销售费用 | {{se}} | {{se_pct}}% | {{se_delta}} | {{se_ind}}% |
| 管理费用 | {{me}} | {{me_pct}}% | {{me_delta}} | {{me_ind}}% |
| 研发费用 | {{rd}} | {{rd_pct}}% | {{rd_delta}} | {{rd_ind}}% |
| 财务费用 | {{fe}} | {{fe_pct}}% | {{fe_delta}} | {{fe_ind}}% |

研发费用资本化率：{{rd_cap_rate}}%。{{rd_cap_assessment}}

> **本节写作目标**：穿透利润表表面数字，揭示真实的盈利能力和质量
> **应调用的指标**：毛利率、核心利润率、各项费用率、非经常性损益占比、利润含金量
> **模板表达**："公司核心利润率为{{cp_pct}}%，较上年{{change}}{{delta}}个百分点，{{change_reason}}。"

---

## 六、现金流量表分析

### 6.1 现金流结构分析

| 现金流类别 | {{year_1}}（亿元） | {{year_2}}（亿元） | {{year_3}}（亿元） | 趋势 |
|---|---|---|---|---|
| 经营活动现金流净额 | {{ocf_1}} | {{ocf_2}} | {{ocf_3}} | {{ocf_trend}} |
| 投资活动现金流净额 | {{icf_1}} | {{icf_2}} | {{icf_3}} | {{icf_trend}} |
| 筹资活动现金流净额 | {{fcf_1}} | {{fcf_2}} | {{fcf_3}} | {{fcf_trend}} |
| 现金净增加额 | {{nc_1}} | {{nc_2}} | {{nc_3}} | {{nc_trend}} |

现金流模式识别：{{cashflow_pattern}}

### 6.2 经营活动现金流质量

利润含金量：{{profit_quality_values}}%。{{pq_assessment}}

经营现金流/营业收入：{{ocf_rev_values}}%。{{ocf_rev_assessment}}

### 6.3 投资活动现金流分析

资本支出：{{capex_values}}亿元。{{capex_assessment}}

投资效率（资本支出/营业收入）：{{capex_rev_values}}%。

### 6.4 筹资活动现金流分析

借款净增加：{{loan_change}}亿元。
分红金额：{{dividend}}亿元，股利支付率{{payout}}%。
股权融资：{{equity_finance}}亿元。

### 6.5 自由现金流与造血能力

自由现金流：{{fcf_values}}亿元。{{fcf_assessment}}

造血能力综合评估：{{self_sufficiency_assessment}}

> **本节写作目标**：还原企业真实的资金运动轨迹
> **模板表达**："公司近三年经营活动现金流净额分别为{{ocf_values}}元，呈{{trend}}趋势。利润含金量为{{pq}}%，表明每1元净利润有{{pq}}元现金保障。自由现金流{{fcf}}元，{{fcf_assessment}}。"

---

## 七、偿债能力分析

### 7.1 短期偿债能力

| 指标 | {{year_1}} | {{year_2}} | {{year_3}} | 行业均值 |
|---|---|---|---|---|
| 流动比率 | | | | |
| 速动比率 | | | | |
| 现金比率 | | | | |
| 现金流量比率 | | | | |

{{short_term_solvency_assessment}}

### 7.2 长期偿债能力

| 指标 | {{year_1}} | {{year_2}} | {{year_3}} | 行业均值 |
|---|---|---|---|---|
| 资产负债率 | | | | |
| 权益乘数 | | | | |
| 利息保障倍数 | | | | |
| 现金流量利息保障倍数 | | | | |
| 有息负债/EBITDA | | | | |

{{long_term_solvency_assessment}}

### 7.3 偿债能力综合评价

{{solvency_summary}}

---

## 八、营运能力分析

| 指标 | {{year_1}} | {{year_2}} | {{year_3}} | 行业均值 |
|---|---|---|---|---|
| 应收账款周转天数 | | | | |
| 存货周转天数 | | | | |
| 总资产周转率 | | | | |
| 固定资产周转率 | | | | |
| 营业周期（天） | | | | |
| 现金转化周期（天） | | | | |

{{operating_capacity_assessment}}

---

## 九、盈利能力分析

### 9.1 盈利水平

| 指标 | {{year_1}} | {{year_2}} | {{year_3}} | 行业均值 |
|---|---|---|---|---|
| ROE | | | | |
| ROA | | | | |
| ROIC | | | | |
| 毛利率 | | | | |
| 核心利润率 | | | | |
| 净利率 | | | | |

### 9.2 杜邦分解

ROE = 净利率 × 总资产周转率 × 权益乘数

| 因素 | {{year_1}} | {{year_2}} | {{year_3}} | 变动方向 |
|---|---|---|---|---|
| ROE | | | | |
| 净利率 | | | | |
| 总资产周转率 | | | | |
| 权益乘数 | | | | |

{{dupont_interpretation}}

### 9.3 盈利质量

利润含金量 vs ROE：{{quality_comparison}}

{{profitability_summary}}

---

## 十、成长能力分析

| 指标 | {{year_2}}同比 | {{year_3}}同比 | 三年复合 |
|---|---|---|---|
| 营业收入增长率 | | | |
| 净利润增长率 | | | |
| 核心利润增长率 | | | |
| 总资产增长率 | | | |
| 净资产增长率 | | | |

可持续增长率 vs 实际增长率：{{sgr_comparison}}

{{growth_assessment}}

---

## 十一、杜邦综合分析

### 11.1 杜邦分解结果

{{dupont_tree}}

### 11.2 因素变动分析（连环替代法）

{{factor_analysis}}

### 11.3 ROE驱动因素诊断

{{roe_diagnosis}}

### 11.4 与对标公司杜邦对比

{{peer_dupont_comparison}}

---

## 十二、现金流质量与盈余质量分析

### 12.1 现金流质量评估

现金流质量等级：{{cf_quality_grade}}
{{cf_quality_detail}}

### 12.2 盈余质量评估

盈余质量等级：{{earnings_quality_grade}}
{{earnings_quality_detail}}

### 12.3 会计信息可靠性评价

审计意见：{{audit_opinion}}
关键审计事项：{{kam}}
会计政策/估计变更：{{accounting_changes}}
会计信息可靠性评级：{{reliability_grade}}

---

## 十三、异常信号与风险提示

### 13.1 高风险信号

{{#each high_risks}}
- **[{{rule_id}}] {{rule_name}}**：{{explanation}}。{{agent_response}}
{{/each}}

{{#if no_high_risks}}
未触发高风险规则。
{{/if}}

### 13.2 中等风险信号

{{#each medium_risks}}
- **[{{rule_id}}] {{rule_name}}**：{{explanation}}。{{agent_response}}
{{/each}}

### 13.3 需关注事项

{{attention_items}}

### 13.4 风险总结

风险等级综合评定：{{overall_risk_grade}}

---

## 十四、综合评价与改进建议

### 14.1 总体财务健康度评级

**综合评价等级**：{{overall_grade}}（优秀/良好/一般/关注/风险）

| 评价维度 | 评分 | 说明 |
|---|---|---|
| 资产质量 | {{aq_score}} | {{aq_note}} |
| 资本结构 | {{cs_score}} | {{cs_note}} |
| 利润质量 | {{pq_score}} | {{pq_note}} |
| 现金流质量 | {{cf_score}} | {{cf_note}} |
| 偿债能力 | {{sol_score}} | {{sol_note}} |
| 营运能力 | {{op_score}} | {{op_note}} |
| 盈利能力 | {{pr_score}} | {{pr_note}} |
| 成长能力 | {{gr_score}} | {{gr_note}} |

### 14.2 核心优势

{{strengths}}

### 14.3 主要问题

{{weaknesses}}

### 14.4 改进建议

{{recommendations}}

### 14.5 免责声明

> 本报告由财务报表分析 Agent 自动生成，分析结果基于公开财务数据和教材分析框架，
> 仅供研究参考，不构成任何投资建议。报告中涉及的所有判断均基于特定分析框架和假设，
> 可能存在局限。投资者在使用本报告时，应结合自身的专业判断和市场实际情况，
> 独立做出投资决策。

---

**报告生成时间**：{{generation_timestamp}}
**所使用教材框架**：张新民、钱爱民《财务报表分析（第6版）》"企业财务状况质量分析理论"
**数据完整性**：{{data_completeness}}
**分析局限性**：{{limitations}}
