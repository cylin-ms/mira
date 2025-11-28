"""
Assertions Viewer - Fluent Design
Visualize utterances and their assertions in an easy-to-read card format.
"""

import streamlit as st
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Assertions Viewer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fluent Design CSS
st.markdown("""
<style>
    /* Fluent Design System */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
    }
    
    /* Utterance Card */
    .utterance-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .utterance-card:hover {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* Card Header */
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    .card-number {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-size: 14px;
        font-weight: 600;
        padding: 8px 14px;
        border-radius: 20px;
        min-width: 50px;
        text-align: center;
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a2e;
        flex: 1;
        line-height: 1.4;
    }
    
    /* Stats badges */
    .stats-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .stat-critical {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #dc2626;
        border: 1px solid #fca5a5;
    }
    
    .stat-expected {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #d97706;
        border: 1px solid #fcd34d;
    }
    
    .stat-aspirational {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #2563eb;
        border: 1px solid #93c5fd;
    }
    
    /* Response Section */
    .response-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    
    .response-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .response-text {
        font-size: 14px;
        color: #334155;
        line-height: 1.7;
        white-space: pre-wrap;
    }
    
    /* Assertions Grid */
    .assertions-header {
        font-size: 14px;
        font-weight: 600;
        color: #475569;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .assertion-item {
        background: white;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    
    .assertion-item:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .assertion-critical {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, #fef2f2 0%, white 20%);
    }
    
    .assertion-expected {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, #fffbeb 0%, white 20%);
    }
    
    .assertion-aspirational {
        border-left-color: #3b82f6;
        background: linear-gradient(90deg, #eff6ff 0%, white 20%);
    }
    
    .assertion-level {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .level-critical { color: #dc2626; }
    .level-expected { color: #d97706; }
    .level-aspirational { color: #2563eb; }
    
    .assertion-text {
        font-size: 14px;
        color: #1e293b;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    .assertion-meta {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #64748b;
    }
    
    .meta-dim {
        background: #f1f5f9;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 500;
    }
    
    .meta-source {
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 11px;
        color: #94a3b8;
    }
    
    /* Sidebar styles */
    .sidebar-header {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .sidebar-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 24px;
    }
    
    /* Summary stats */
    .summary-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .summary-title {
        font-size: 13px;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 4px;
    }
    
    .summary-value {
        font-size: 32px;
        font-weight: 700;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# Default file path
DEFAULT_FILE = "docs/Kening/Assertions_genv2_for_LOD1126part1.jsonl"

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">📋 Assertions Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Fluent Design Edition</div>', unsafe_allow_html=True)
    
    # File selection
    file_path = st.text_input("📁 Data File", value=DEFAULT_FILE)
    
    try:
        data = load_data(file_path)
        
        # Summary stats
        total_utterances = len(data)
        total_assertions = sum(len(item.get('assertions', [])) for item in data)
        
        # Count by level
        level_counts = {'critical': 0, 'expected': 0, 'aspirational': 0}
        for item in data:
            for a in item.get('assertions', []):
                level = a.get('level', 'unknown')
                if level in level_counts:
                    level_counts[level] += 1
        
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-title">Total Utterances</div>
            <div class="summary-value">{total_utterances}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Assertions", total_assertions)
        with col2:
            st.metric("📊 Avg/Utterance", f"{total_assertions/total_utterances:.1f}")
        
        st.divider()
        
        # Level breakdown
        st.markdown("**Assertion Levels**")
        st.markdown(f"""
        <div class="stats-row">
            <span class="stat-badge stat-critical">🔴 Critical: {level_counts['critical']}</span>
            <span class="stat-badge stat-expected">🟡 Expected: {level_counts['expected']}</span>
            <span class="stat-badge stat-aspirational">🔵 Aspirational: {level_counts['aspirational']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Filters
        st.markdown("**🔍 Filters**")
        
        # Level filter
        level_filter = st.multiselect(
            "Filter by Level",
            options=['critical', 'expected', 'aspirational'],
            default=['critical', 'expected', 'aspirational']
        )
        
        # Search
        search_query = st.text_input("🔎 Search utterances", placeholder="Type to search...")
        
        # Pagination
        st.divider()
        items_per_page = st.slider("Items per page", 5, 50, 10)
        
    except Exception as e:
        st.error(f"Error loading file: {e}")
        data = []

# Main content
if data:
    # Filter data
    filtered_data = []
    for i, item in enumerate(data):
        # Search filter
        if search_query:
            utterance = item.get('utterance', '').lower()
            response = item.get('response', '').lower()
            if search_query.lower() not in utterance and search_query.lower() not in response:
                continue
        
        # Level filter - keep items that have at least one assertion with selected level
        assertions = item.get('assertions', [])
        filtered_assertions = [a for a in assertions if a.get('level', 'unknown') in level_filter]
        
        if filtered_assertions or not assertions:  # Keep items with matching assertions or no assertions
            filtered_data.append((i, item, filtered_assertions))
    
    # Show filter results
    st.markdown(f"### Showing {len(filtered_data)} of {len(data)} utterances")
    
    # Pagination
    total_pages = max(1, (len(filtered_data) + items_per_page - 1) // items_per_page)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="page_selector")
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_data))
    
    st.markdown(f"<p style='text-align: center; color: #64748b;'>Page {page} of {total_pages}</p>", unsafe_allow_html=True)
    
    # Render utterance cards
    for idx, item, filtered_assertions in filtered_data[start_idx:end_idx]:
        utterance = item.get('utterance', 'No utterance')
        response = item.get('response', 'No response')
        assertions = filtered_assertions if level_filter != ['critical', 'expected', 'aspirational'] else item.get('assertions', [])
        
        # Count assertions by level
        counts = {'critical': 0, 'expected': 0, 'aspirational': 0}
        for a in assertions:
            level = a.get('level', 'unknown')
            if level in counts:
                counts[level] += 1
        
        # Build card header HTML
        card_header_html = f"""
        <div class="utterance-card">
            <div class="card-header">
                <span class="card-number">#{idx + 1}</span>
                <span class="card-title">{utterance}</span>
            </div>
        </div>
        """
        st.markdown(card_header_html, unsafe_allow_html=True)
        
        # Stats using Streamlit columns for proper rendering
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.markdown(f"🔴 **{counts['critical']}** Critical")
        with stat_cols[1]:
            st.markdown(f"🟡 **{counts['expected']}** Expected")
        with stat_cols[2]:
            st.markdown(f"🔵 **{counts['aspirational']}** Aspirational")
        
        # Response in expander
        with st.expander("📄 View Response", expanded=False):
            st.markdown(f"""
            <div class="response-section">
                <div class="response-label">LLM Response</div>
                <div class="response-text">{response}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Assertions in collapsible expander
        if assertions:
            with st.expander(f"📋 Assertions ({len(assertions)})", expanded=False):
                for a in assertions:
                    level = a.get('level', 'unknown')
                    text = a.get('text', '')
                    anchors = a.get('anchors', {})
                    dim = anchors.get('Dim', 'N/A')
                    source_id = anchors.get('sourceID', 'N/A')
                    
                    level_class = f"assertion-{level}" if level in ['critical', 'expected', 'aspirational'] else ""
                    level_label_class = f"level-{level}" if level in ['critical', 'expected', 'aspirational'] else ""
                    
                    st.markdown(f"""
                    <div class="assertion-item {level_class}">
                        <div class="assertion-level {level_label_class}">{level.upper()}</div>
                        <div class="assertion-text">{text}</div>
                        <div class="assertion-meta">
                            <span class="meta-item">
                                <span class="meta-dim">📂 {dim}</span>
                            </span>
                            <span class="meta-item meta-source">
                                🔗 {source_id[:20]}...
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Divider between cards
        st.markdown("---")

else:
    st.warning("No data loaded. Please check the file path.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px;">
    Assertions Viewer v1.0 | Fluent Design | Built with Streamlit
</div>
""", unsafe_allow_html=True)
