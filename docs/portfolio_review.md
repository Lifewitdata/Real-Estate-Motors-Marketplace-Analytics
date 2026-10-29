# Portfolio review and remaining limits

The original delivery contained Python scripts, SQL and a Streamlit UI but lacked an executed notebook presenting the analytical work. The notebook now exposes data inspection, source verification, exploratory tables, charts, quality rules, reconciliation and conclusions. Code cells execute independently of Streamlit; shared functions keep the notebook and pipeline consistent.

Project 1 demonstrates market analysis and comparable-selection sensitivity. Project 2 demonstrates database evidence reconciliation and controlled before/after recovery. Both use the same official Brooklyn extract; they should be described as complementary workflows, not independent datasets or independent external validations.

A notebook is not a prerequisite for using Python, and a running dashboard alone does not prove analytical completeness. Local software tests, notebook execution and CI establish reproducibility; they do not prove valuation accuracy or business impact.

Still outside scope: independent deed/transaction verification, property inspections, income evidence, certified appraiser review, proprietary Newmark systems and production authorization. Recovery metrics in project 2 are deliberately simulated. No MySQL, PostgreSQL, Tableau or Power BI implementation is claimed for the active workflows. The local SQLite/DuckDB choices are disclosed; the historic MySQL exercise is separate.
