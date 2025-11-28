"""
Assertion Analysis Viewer - Visualize GPT-5 analysis results
"""

import streamlit as st
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Assertion Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fluent Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    .stApp { background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); }
    
    .pattern-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 4px solid;
    }
    
    .pattern-critical { border-left-color: #ef4444; }
    .pattern-expected { border-left-color: #f59e0b; }
    .pattern-aspirational { border-left-color: #3b82f6; }
    
    .pattern-id {
        font-size: 14px;
        font-weight: 700;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .id-critical { background: #ef4444; }
    .id-expected { background: #f59e0b; }
    .id-aspirational { background: #3b82f6; }
    
    .pattern-name {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 8px;
    }
    
    .pattern-desc {
        color: #475569;
        margin-bottom: 12px;
    }
    
    .pattern-template {
        background: #f1f5f9;
        padding: 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
        color: #334155;
        margin-bottom: 12px;
    }
    
    .criteria-item {
        padding: 8px 12px;
        background: #f8fafc;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 14px;
    }
    
    .grade-badge {
        font-size: 48px;
        font-weight: 700;
        padding: 20px 40px;
        border-radius: 16px;
        display: inline-block;
    }
    
    .grade-A { background: #dcfce7; color: #166534; }
    .grade-B { background: #dbeafe; color: #1e40af; }
    .grade-C { background: #fef3c7; color: #92400e; }
    .grade-D { background: #fee2e2; color: #991b1b; }
    .grade-F { background: #fecaca; color: #7f1d1d; }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #1e293b;
    }
    
    .stat-label {
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
    }
    
    .issue-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
    }
    
    .issue-specificity { background: #fee2e2; color: #dc2626; }
    .issue-applicability { background: #fef3c7; color: #d97706; }
    .issue-robustness { background: #dbeafe; color: #2563eb; }
    .issue-redundancy { background: #f3e8ff; color: #7c3aed; }
    .issue-ambiguity { background: #fce7f3; color: #db2777; }
    .issue-measurability { background: #d1fae5; color: #059669; }
    .issue-completeness { background: #e0e7ff; color: #4f46e5; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_analysis():
    analysis_path = Path("docs/ChinYew/assertion_analysis.json")
    if analysis_path.exists():
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@st.cache_data
def load_patterns():
    patterns_path = Path("docs/ChinYew/assertion_patterns.json")
    if patterns_path.exists():
        with open(patterns_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

analysis = load_analysis()
patterns = load_patterns()

# Header
st.title("📊 Assertion Quality Analysis")
st.markdown("GPT-5 JJ comprehensive analysis of workback plan assertions")

if not analysis:
    st.error("Analysis file not found. Run `python analyze_assertions_gpt5.py` first.")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔄 Patterns", "🔍 Critiques", "📋 Recommendations"])

# Tab 1: Overview
with tab1:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Grade
        oa = analysis.get('comprehensive_analysis', {}).get('overall_assessment', {})
        grade = oa.get('quality_grade', 'N/A')
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <div class="grade-badge grade-{grade}">{grade}</div>
            <p style="color: #64748b; margin-top: 8px;">Overall Quality Grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Stats
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{analysis.get('total_assertions', 0)}</div>
                <div class="stat-label">Total Assertions</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{analysis.get('sampled_assertions', 0)}</div>
                <div class="stat-label">Sampled</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            critiques = analysis.get('critiques', [])
            scores = [c.get('quality_score', 0) for c in critiques if c.get('quality_score')]
            avg = sum(scores)/len(scores) if scores else 0
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{avg:.1f}</div>
                <div class="stat-label">Avg Quality Score</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[3]:
            num_patterns = len(patterns.get('patterns', [])) if patterns else 0
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{num_patterns}</div>
                <div class="stat-label">Patterns Found</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Strengths & Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        for s in oa.get('strengths', []):
            st.success(s)
    
    with col2:
        st.markdown("### ⚠️ Weaknesses")
        for w in oa.get('weaknesses', []):
            st.warning(w)
    
    # Coverage & Balance
    st.markdown("---")
    st.markdown("### 📊 Assessment Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Balance Assessment:**")
        st.info(oa.get('balance_assessment', 'N/A'))
    with col2:
        st.markdown("**Coverage Assessment:**")
        st.info(oa.get('coverage_assessment', 'N/A'))
    
    # Issue Distribution
    if critiques:
        st.markdown("---")
        st.markdown("### 🔍 Issue Distribution")
        
        from collections import Counter
        issue_counts = Counter()
        for c in critiques:
            for issue in c.get('issues', []):
                issue_counts[issue.get('type', 'unknown')] += 1
        
        # Display as badges
        issue_html = ""
        for issue_type, count in issue_counts.most_common():
            issue_html += f'<span class="issue-badge issue-{issue_type}">{issue_type}: {count}</span> '
        st.markdown(issue_html, unsafe_allow_html=True)

# Tab 2: Patterns
with tab2:
    if patterns and patterns.get('patterns'):
        st.markdown("### 🔄 Identified Assertion Patterns")
        st.markdown("These patterns can be used by human judges to evaluate workback plans consistently.")
        
        for p in patterns['patterns']:
            level = p.get('level_recommendation', 'expected').lower()
            level_class = f"pattern-{level}"
            id_class = f"id-{level}"
            
            st.markdown(f"""
            <div class="pattern-card {level_class}">
                <span class="pattern-id {id_class}">{p.get('pattern_id', '?')}</span>
                <span style="margin-left: 8px; color: #64748b; font-size: 12px; text-transform: uppercase;">{level}</span>
                <div class="pattern-name">{p.get('pattern_name', 'Unknown')}</div>
                <div class="pattern-desc">{p.get('pattern_description', '')}</div>
                <div class="pattern-template">📝 {p.get('pattern_template', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View Evaluation Criteria & Details"):
                st.markdown("**Evaluation Criteria for Human Judges:**")
                for c in p.get('evaluation_criteria', []):
                    st.markdown(f"- {c}")
                
                if p.get('example_instances'):
                    st.markdown("**Example Assertions:**")
                    for ex in p.get('example_instances', []):
                        st.code(ex, language=None)
                
                if p.get('anti_patterns'):
                    st.markdown("**Anti-Patterns (what to avoid):**")
                    for ap in p.get('anti_patterns', []):
                        st.error(ap)
                
                if p.get('robustness_notes'):
                    st.markdown(f"**Robustness Notes:** {p.get('robustness_notes')}")
        
        # Dimension Consolidation
        st.markdown("---")
        st.markdown("### 🔀 Suggested Dimension Consolidation")
        
        dc = patterns.get('dimension_consolidation', {})
        for new_dim, old_dims in dc.items():
            st.markdown(f"**{new_dim}** ← {', '.join(old_dims)}")
        
        # Coverage Gaps
        if patterns.get('coverage_gaps'):
            st.markdown("---")
            st.markdown("### ⚠️ Coverage Gaps")
            for gap in patterns['coverage_gaps']:
                st.warning(gap)
        
        # Human Judge Guidelines
        if patterns.get('human_judge_guidelines'):
            st.markdown("---")
            st.markdown("### 👨‍⚖️ Human Judge Guidelines")
            
            hjg = patterns['human_judge_guidelines']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Priority Order:**")
                st.code(" → ".join(hjg.get('priority_order', [])))
            
            with col2:
                st.markdown("**Minimum Coverage (MUST check):**")
                for m in hjg.get('minimum_coverage', []):
                    st.markdown(f"✓ {m}")
            
            st.markdown("**Evaluation Workflow:**")
            st.info(hjg.get('evaluation_workflow', 'N/A'))
    else:
        st.warning("No patterns data available.")

# Tab 3: Critiques
with tab3:
    critiques = analysis.get('critiques', [])
    
    if critiques:
        st.markdown(f"### 🔍 Individual Assertion Critiques ({len(critiques)} analyzed)")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider("Minimum Quality Score", 1, 10, 1)
        with col2:
            max_score = st.slider("Maximum Quality Score", 1, 10, 10)
        
        filtered = [c for c in critiques if min_score <= c.get('quality_score', 5) <= max_score]
        
        st.markdown(f"Showing {len(filtered)} critiques")
        
        for i, c in enumerate(filtered[:50]):  # Limit display
            orig = c.get('original_assertion', {})
            score = c.get('quality_score', 0)
            
            # Color based on score
            if score >= 8:
                score_color = "#22c55e"
            elif score >= 6:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"
            
            with st.expander(f"[{score}/10] {orig.get('text', 'N/A')[:80]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Original Assertion:**")
                    st.markdown(f"> {orig.get('text', 'N/A')}")
                    
                    st.markdown(f"**Level:** {orig.get('level', 'N/A')} | **Dimension:** {orig.get('dim', 'N/A')}")
                
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 36px; font-weight: 700; color: {score_color};">{score}</div>
                        <div style="font-size: 12px; color: #64748b;">/10</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Issues
                if c.get('issues'):
                    st.markdown("**Issues:**")
                    for issue in c['issues']:
                        severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('severity', 'low'), "⚪")
                        st.markdown(f"{severity_color} **{issue.get('type', 'unknown')}**: {issue.get('description', '')}")
                
                # Strengths
                if c.get('strengths'):
                    st.markdown("**Strengths:**")
                    for s in c['strengths']:
                        st.markdown(f"✓ {s}")
                
                # Improvement Suggestions
                if c.get('improvement_suggestions'):
                    st.markdown("**Suggestions:**")
                    for s in c['improvement_suggestions']:
                        st.markdown(f"💡 {s}")
                
                # Rewritten
                if c.get('rewritten_assertion') and c['rewritten_assertion'] != 'N/A':
                    st.markdown("**Suggested Rewrite:**")
                    st.success(c['rewritten_assertion'])
                
                # Generalizability
                st.markdown(f"**Generalizability:** {c.get('generalizability', 'N/A')} - {c.get('generalizability_notes', '')}")
    else:
        st.warning("No critiques available.")

# Tab 4: Recommendations
with tab4:
    st.markdown("### 📋 Actionable Recommendations")
    
    ca = analysis.get('comprehensive_analysis', {})
    recs = ca.get('actionable_recommendations', [])
    
    if recs:
        for rec in sorted(recs, key=lambda x: x.get('priority', 99)):
            priority = rec.get('priority', '?')
            category = rec.get('category', 'General')
            
            with st.container():
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.markdown(f"""
                    <div style="background: #6366f1; color: white; font-size: 24px; font-weight: 700; 
                                width: 48px; height: 48px; border-radius: 24px; display: flex; 
                                align-items: center; justify-content: center;">
                        {priority}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{category}**")
                    st.markdown(rec.get('recommendation', ''))
                    st.caption(f"Impact: {rec.get('impact', 'N/A')}")
                st.markdown("---")
    
    # Level Analysis
    st.markdown("### 📊 Level-by-Level Analysis")
    
    la = ca.get('level_analysis', {})
    for level in ['critical', 'expected', 'aspirational']:
        level_data = la.get(level, {})
        if level_data:
            with st.expander(f"**{level.upper()}** Analysis"):
                st.markdown(f"**Appropriateness:** {level_data.get('appropriateness', 'N/A')}")
                
                if level_data.get('issues'):
                    st.markdown("**Issues:**")
                    for issue in level_data['issues']:
                        st.warning(issue)
                
                if level_data.get('recommendations'):
                    st.markdown("**Recommendations:**")
                    for rec in level_data['recommendations']:
                        st.info(rec)
    
    # Proposed Rubric
    rubric = ca.get('proposed_evaluation_rubric', {})
    if rubric:
        st.markdown("---")
        st.markdown("### ✅ Proposed Evaluation Rubric")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Must-Have Criteria:**")
            for c in rubric.get('must_have_criteria', []):
                st.success(c)
        
        with col2:
            st.markdown("**Should-Have Criteria:**")
            for c in rubric.get('should_have_criteria', []):
                st.warning(c)
        
        with col3:
            st.markdown("**Nice-to-Have Criteria:**")
            for c in rubric.get('nice_to_have_criteria', []):
                st.info(c)
        
        if rubric.get('scoring_guidance'):
            st.markdown("**Scoring Guidance:**")
            st.markdown(rubric['scoring_guidance'])

# Footer
st.markdown("---")
st.caption(f"Analysis generated: {analysis.get('timestamp', 'N/A')}")
