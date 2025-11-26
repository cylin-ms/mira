import streamlit as st
import json
import os
import re
import time
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Output Visualizer",
    page_icon="📋",
    layout="wide"
)

# Paths to the files
# Updated to use new format (11_25_output.jsonl) which uses 'justification' instead of 'reasoning'
OUTPUT_FILE_PATH = os.path.join("docs", "11_25_output.jsonl")  # New format with justification/sourceID
INPUT_FILE_PATH = os.path.join("docs", "LOD_1121.WithUserUrl.jsonl")  # New context file with user URLs for Test Tenant
ANNOTATION_SAVE_PATH = os.path.join("docs", "annotations_temp.json")
ANNOTATION_EXPORT_PATH = os.path.join("docs", "annotated_output.jsonl")

# ====== ANNOTATION SYSTEM ======
def init_annotation_state():
    """Initialize annotation-related session state variables."""
    if "annotations" not in st.session_state:
        st.session_state.annotations = {}  # {utterance: {assertion_idx: {is_good: bool, revision: str, original: str}}}
    if "new_assertions" not in st.session_state:
        st.session_state.new_assertions = {}  # {utterance: [{text, level, justification}]}
    if "last_save_time" not in st.session_state:
        st.session_state.last_save_time = time.time()
    if "annotation_modified" not in st.session_state:
        st.session_state.annotation_modified = False
    if "judge_name" not in st.session_state:
        st.session_state.judge_name = os.environ.get('USERNAME', os.environ.get('USER', ''))
    if "expanded_assertions" not in st.session_state:
        st.session_state.expanded_assertions = set()  # Track which assertion expanders are open
    
    # Try to load existing annotations from temp file
    if os.path.exists(ANNOTATION_SAVE_PATH):
        try:
            with open(ANNOTATION_SAVE_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if "annotations" in saved:
                    st.session_state.annotations = saved["annotations"]
                if "new_assertions" in saved:
                    st.session_state.new_assertions = saved["new_assertions"]
                if "judge_name" in saved:
                    st.session_state.judge_name = saved["judge_name"]
        except:
            pass


def auto_save_annotations():
    """Auto-save annotations every minute if modified."""
    current_time = time.time()
    if st.session_state.annotation_modified and (current_time - st.session_state.last_save_time > 60):
        save_annotations()
        st.session_state.last_save_time = current_time
        st.session_state.annotation_modified = False
        return True
    return False


def save_annotations():
    """Save current annotations to temporary file."""
    save_data = {
        "annotations": st.session_state.annotations,
        "new_assertions": st.session_state.new_assertions,
        "judge_name": st.session_state.judge_name,
        "last_saved": datetime.now().isoformat()
    }
    with open(ANNOTATION_SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)


def get_annotation(utterance, assertion_idx):
    """Get annotation for a specific assertion."""
    if utterance in st.session_state.annotations:
        return st.session_state.annotations[utterance].get(str(assertion_idx), {})
    return {}


def set_annotation(utterance, assertion_idx, is_good=None, revision=None, original=None, note=None, is_confident=None, is_judged=None):
    """Set annotation for a specific assertion."""
    if utterance not in st.session_state.annotations:
        st.session_state.annotations[utterance] = {}
    
    key = str(assertion_idx)
    if key not in st.session_state.annotations[utterance]:
        st.session_state.annotations[utterance][key] = {"is_good": True, "revision": "", "original": "", "note": "", "is_confident": True, "is_judged": False}
    
    if is_good is not None:
        st.session_state.annotations[utterance][key]["is_good"] = is_good
    if revision is not None:
        st.session_state.annotations[utterance][key]["revision"] = revision
    if original is not None:
        st.session_state.annotations[utterance][key]["original"] = original
    if note is not None:
        st.session_state.annotations[utterance][key]["note"] = note
    if is_confident is not None:
        st.session_state.annotations[utterance][key]["is_confident"] = is_confident
    if is_judged is not None:
        st.session_state.annotations[utterance][key]["is_judged"] = is_judged
    
    st.session_state.annotation_modified = True


def add_new_assertion(utterance, assertion_data):
    """Add a new user-created assertion."""
    if utterance not in st.session_state.new_assertions:
        st.session_state.new_assertions[utterance] = []
    st.session_state.new_assertions[utterance].append(assertion_data)
    st.session_state.annotation_modified = True


def get_new_assertions(utterance):
    """Get user-added assertions for an utterance."""
    return st.session_state.new_assertions.get(utterance, [])


def export_annotated_data(output_data):
    """Export annotated data in Kening's format with annotations field."""
    exported = []
    
    for item in output_data:
        utterance = item.get('utterance', '')
        new_item = item.copy()
        
        # Add annotations field
        annotations_for_item = []
        original_assertions = item.get('assertions', [])
        
        for i, assertion in enumerate(original_assertions):
            ann = get_annotation(utterance, i)
            annotation_entry = {
                "assertion_index": i,
                "original_text": assertion.get('text', ''),
                "is_good": ann.get('is_good', True),  # Default is good
                "is_confident": ann.get('is_confident', True),  # Default is confident
                "is_judged": ann.get('is_judged', False),  # Default is not judged
            }
            
            # Add revision if exists
            if ann.get('revision'):
                annotation_entry["revised_text"] = ann.get('revision')
            
            # Add note if exists
            if ann.get('note'):
                annotation_entry["note"] = ann.get('note')
            
            annotations_for_item.append(annotation_entry)
        
        # Add new assertions created by user
        new_asserts = get_new_assertions(utterance)
        for new_assert in new_asserts:
            annotations_for_item.append({
                "is_new": True,
                "text": new_assert.get('text', ''),
                "level": new_assert.get('level', 'expected'),
                "justification": new_assert.get('justification', {}),
                "is_good": True,
                "is_confident": True,
                "is_judged": True  # New assertions are considered judged
            })
        
        new_item['annotations'] = annotations_for_item
        
        # Add judge information
        new_item['judge'] = st.session_state.judge_name
        
        # Calculate statistics
        good_count = sum(1 for a in annotations_for_item if a.get('is_good', True))
        confident_count = sum(1 for a in annotations_for_item if a.get('is_confident', True))
        judged_count = sum(1 for a in annotations_for_item if a.get('is_judged', False))
        total_count = len(annotations_for_item)
        new_item['annotation_stats'] = {
            "total": total_count,
            "good": good_count,
            "not_good": total_count - good_count,
            "confident": confident_count,
            "not_confident": total_count - confident_count,
            "judged": judged_count,
            "not_judged": total_count - judged_count,
            "revised": sum(1 for a in annotations_for_item if a.get('revised_text')),
            "new_added": len(new_asserts)
        }
        
        exported.append(new_item)
    
    return exported


# Initialize annotation state
init_annotation_state()


def get_assertion_reasoning(assertion):
    """Get reasoning from assertion, handling both old and new formats.
    
    Old format: {'reasoning': {'reason': '...', 'source': '...'}}
    New format: {'justification': {'reason': '...', 'sourceID': '...'}}
    """
    if 'justification' in assertion:
        return assertion['justification']
    elif 'reasoning' in assertion:
        return assertion['reasoning']
    return {}


def get_assertion_source(assertion):
    """Get source reference from assertion, handling both old and new formats.
    
    Old format uses 'source' field with descriptive text.
    New format uses 'sourceID' field with entity IDs.
    """
    reasoning = get_assertion_reasoning(assertion)
    if 'sourceID' in reasoning:
        return reasoning['sourceID']
    elif 'source' in reasoning:
        return reasoning['source']
    return ''


def is_source_id_format(assertion):
    """Check if assertion uses new sourceID format (entity IDs)."""
    reasoning = get_assertion_reasoning(assertion)
    return 'sourceID' in reasoning


def build_entity_index(input_item):
    """Build a lookup index for entities by various ID fields.
    
    Returns a dict mapping potential IDs to (entity_type, entity_index, entity_data).
    sourceID can reference: FileId, EventId, ChatId, ChatMessageId, OnlineMeetingId, etc.
    """
    index = {}
    
    # Index the User
    user_data = input_item.get('USER', {})
    if user_data:
        user_id = user_data.get('id', '')
        if user_id:
            index[user_id] = ('User', 0, user_data)
        # Also index by common ID patterns
        for key in ['id', 'userId', 'userPrincipalName']:
            if key in user_data and user_data[key]:
                index[user_data[key]] = ('User', 0, user_data)
    
    # Index all entities
    entities = input_item.get('ENTITIES_TO_USE', [])
    for i, entity in enumerate(entities):
        etype = entity.get('type', 'Other')
        
        # Index by various ID fields that might be referenced
        id_fields = [
            'FileId', 'ChatId', 'EventId', 'ChannelMessageId', 'ChannelId',
            'ChannelMessageReplyId', 'OnlineMeetingId', 'EmailId', 'MessageId',
            'id', 'Id', 'ID', 'entityId', 'EntityId'
        ]
        for field in id_fields:
            if field in entity and entity[field]:
                index[entity[field]] = (etype, i, entity)
        
        # Index ChatMessageIds from nested ChatMessages in Chat entities
        if etype == 'Chat' and 'ChatMessages' in entity:
            for msg in entity['ChatMessages']:
                if 'ChatMessageId' in msg:
                    index[msg['ChatMessageId']] = ('ChatMessage', i, entity)
        
        # Also try to match by name/subject for partial matches
        name_fields = ['Subject', 'FileName', 'DisplayName', 'Name', 'Title']
        for field in name_fields:
            if field in entity and entity[field]:
                index[entity[field]] = (etype, i, entity)
    
    return index


def find_entity_by_source_id(source_id, entity_index):
    """Find an entity matching the given sourceID.
    
    Returns (entity_type, entity_index, entity_data) or None if not found.
    """
    if not source_id:
        return None
    
    # Direct match
    if source_id in entity_index:
        return entity_index[source_id]
    
    # Try partial match (sourceID might be a substring or vice versa)
    for key, value in entity_index.items():
        if source_id in str(key) or str(key) in source_id:
            return value
    
    return None

# Entity Styling Configuration
ENTITY_STYLES = {
    "User": {"color": "#3498db", "icon": "👤"},
    "Event": {"color": "#9b59b6", "icon": "📅"},
    "OnlineMeeting": {"color": "#8e44ad", "icon": "📹"},
    "File": {"color": "#e67e22", "icon": "📄"},
    "Chat": {"color": "#2ecc71", "icon": "💬"},
    "ChannelMessage": {"color": "#27ae60", "icon": "📢"},
    "Email": {"color": "#e74c3c", "icon": "✉️"},
    "Other": {"color": "#95a5a6", "icon": "📦"}
}

def get_entity_card_header(etype, title):
    style = ENTITY_STYLES.get(etype, ENTITY_STYLES["Other"])
    color = style["color"]
    icon = style["icon"]
    return f"""
    <div style="
        background-color: {color}; 
        padding: 8px 12px; 
        border-radius: 5px; 
        color: white; 
        margin-bottom: 10px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span style="font-size: 1.2em;">{icon}</span>
        <span>{title}</span>
    </div>
    """

def render_user_card(item):
    """Render a professional card for a User entity."""
    display_name = item.get('DisplayName', 'Unknown')
    job_title = item.get('JobTitle', '')
    department = item.get('Department', '')
    email = item.get('MailNickName', '')
    phone = item.get('PhoneNumber', '')
    location = item.get('OfficeLocation', '')
    manager = item.get('Manager', '')
    
    # Address
    address = item.get('Address', {})
    full_address = f"{address.get('Street', '')}, {address.get('City', '')}, {address.get('State', '')} {address.get('PostalCode', '')}" if address else ""

    html = f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; color: #333;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h3 style="margin: 0; color: #2c3e50;">{display_name}</h3>
                <p style="margin: 2px 0; color: #7f8c8d; font-style: italic;">{job_title} {f"| {department}" if department else ""}</p>
            </div>
            <div style="text-align: right; font-size: 0.9em; color: #7f8c8d;">
                <div>{location}</div>
            </div>
        </div>
        <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
            <div>
                <strong>📧 Email:</strong> {email}<br>
                <strong>📞 Phone:</strong> {phone}<br>
                <strong>👔 Manager:</strong> {manager}
            </div>
            <div>
                <strong>📍 Address:</strong><br>
                {full_address}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_generic_card(item):
    """Render a generic card for other entities."""
    # Filter out complex objects for the summary view
    simple_fields = {k: v for k, v in item.items() if isinstance(v, (str, int, float, bool)) and k not in ['type', 'Content']}
    
    # Create a markdown table
    md = "| Field | Value |\n|---|---|\n"
    for k, v in simple_fields.items():
        md += f"| **{k}** | {v} |\n"
    
    st.markdown(md)

def render_file_card(item, key_suffix=""):
    """Render a card for File entities with content side-by-side."""
    content = item.get('Content', 'No content available.')
    
    # Filter simple fields for metadata
    simple_fields = {k: v for k, v in item.items() if isinstance(v, (str, int, float, bool)) and k not in ['type', 'Content']}
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📄 Metadata")
        # Create a markdown table
        md = "| Field | Value |\n|---|---|\n"
        for k, v in simple_fields.items():
            md += f"| **{k}** | {v} |\n"
        st.markdown(md)
        
    with col2:
        st.markdown("#### 📝 Content")
        # Use tabs to allow switching between rendered markdown and raw text
        tab1, tab2 = st.tabs(["📄 Preview", "ℹ️ Raw Source"])
        
        with tab1:
            # Render markdown in a bordered container to simulate a document page
            with st.container(border=True):
                if content and content.strip():
                    st.markdown(content)
                else:
                    st.caption("No content to preview.")
        
        with tab2:
            st.text_area("File Content", content, height=400, disabled=True, label_visibility="collapsed", key=f"file_content_{key_suffix}")

@st.cache_data
def load_data(path):
    """Load JSONL data from the given path."""
    data = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return data

def get_meeting_subject(item):
    """Extract meeting subject from utterance or entities."""
    utterance = item.get('UTTERANCE', {}).get('text', '')
    
    # 1. Try to extract text inside single quotes
    match = re.search(r"'([^']*)'", utterance)
    if match:
        return match.group(1)
        
    # 2. Try to find Event entity Subject
    entities = item.get('ENTITIES_TO_USE', [])
    for entity in entities:
        if entity.get('type') == 'Event' and 'Subject' in entity:
            return entity['Subject']
            
    # 3. Fallback to truncated utterance
    return utterance[:50] + "..." if len(utterance) > 50 else utterance

def main():
    st.title("📋 Output Data Visualizer")
    
    # Judge name input in header
    col_title, col_judge = st.columns([3, 1])
    with col_judge:
        judge_name = st.text_input(
            "👤 Judge Name",
            value=st.session_state.judge_name,
            key="judge_name_input",
            placeholder="Enter your name"
        )
        if judge_name != st.session_state.judge_name:
            st.session_state.judge_name = judge_name
            save_annotations()
    
    st.markdown(f"### 👤 Judge: **{st.session_state.judge_name or '(Please enter your name)'}**")
    st.markdown(f"Visualizing contents of: `{OUTPUT_FILE_PATH}` matched with `{INPUT_FILE_PATH}`")

    # Load Data early so we can show progress
    output_data = load_data(OUTPUT_FILE_PATH)
    input_data = load_data(INPUT_FILE_PATH)

    if not input_data:
        st.error(f"Could not find or load data from {INPUT_FILE_PATH}. Please ensure the file exists.")
        return

    # === SYNC CHECKBOX STATES TO ANNOTATIONS ===
    # This ensures progress calculation reflects current checkbox states
    # (Streamlit checkboxes update session_state immediately, but our annotations
    # need to be synced before we calculate progress)
    for idx, item in enumerate(output_data):
        utterance = item.get('utterance', '')
        assertions = item.get('assertions', [])
        for i in range(len(assertions)):
            checkbox_key = f"judged_{idx}_{i}"
            if checkbox_key in st.session_state:
                # Get current annotation value
                ann = get_annotation(utterance, i)
                stored_judged = ann.get('is_judged', False)
                checkbox_judged = st.session_state[checkbox_key]
                # Sync if different
                if checkbox_judged != stored_judged:
                    set_annotation(utterance, i, is_judged=checkbox_judged)

    # === PROGRESS REPORT ===
    # Calculate how many meetings have been fully judged (all assertions have is_judged=True)
    total_meetings = len(output_data)
    fully_judged_meetings = 0
    partially_judged_meetings = 0
    total_assertions_judged = 0
    total_assertions = 0
    confident_judgments = 0
    not_confident_judgments = 0
    
    # Build a map of meeting judgment status for sidebar use
    meeting_judgment_status = {}  # utterance -> 'complete' | 'partial' | 'none'
    
    for item in output_data:
        utterance = item.get('utterance', '')
        assertions = item.get('assertions', [])
        num_assertions = len(assertions)
        total_assertions += num_assertions
        
        # Count judged assertions for this meeting
        judged_count = 0
        if utterance in st.session_state.annotations:
            meeting_annotations = st.session_state.annotations[utterance]
            for ann in meeting_annotations.values():
                if ann.get('is_judged', False):
                    judged_count += 1
                    total_assertions_judged += 1
                    # Count confidence only for judged assertions
                    if ann.get('is_confident', True):
                        confident_judgments += 1
                    else:
                        not_confident_judgments += 1
        
        # Determine meeting status
        if num_assertions > 0 and judged_count == num_assertions:
            meeting_judgment_status[utterance] = 'complete'
            fully_judged_meetings += 1
        elif judged_count > 0:
            meeting_judgment_status[utterance] = 'partial'
            partially_judged_meetings += 1
        else:
            meeting_judgment_status[utterance] = 'none'
    
    # Display progress report
    progress_pct = (fully_judged_meetings / total_meetings * 100) if total_meetings > 0 else 0
    
    st.markdown("### 📊 Annotation Progress Report")
    
    # Progress bar
    st.progress(fully_judged_meetings / total_meetings if total_meetings > 0 else 0)
    
    # Legend for status indicators
    st.caption("📗 = Fully judged | 📙 = Partially judged | 📕 = Not started")
    
    # Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Meetings Completed", f"{fully_judged_meetings} / {total_meetings}", f"{progress_pct:.1f}%")
    with col2:
        st.metric("Assertions Judged", f"{total_assertions_judged}", f"of {total_assertions} total")
    with col3:
        st.metric("Confident", f"{confident_judgments}", "✓ sure")
    with col4:
        st.metric("Uncertain", f"{not_confident_judgments}", "? unsure")
    
    # Show partial progress
    if partially_judged_meetings > 0:
        st.info(f"📙 {partially_judged_meetings} meeting(s) partially judged")
    
    st.markdown("---")

    # Display Prompt File
    PROMPT_FILE_PATH = os.path.join("docs", "step1_v2.md")
    if os.path.exists(PROMPT_FILE_PATH):
        with st.expander("📄 View Generation Prompt (step1_v2.md)"):
            with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
                st.markdown(f"```markdown\n{f.read()}\n```")

    # Create a map for output data: utterance -> output_item
    output_map = {item.get('utterance'): item for item in output_data}

    # Sidebar Navigation
    st.sidebar.header("Select an Entry (from Input Data)")
    
    # Filter by annotation status
    filter_options = ["📋 All Meetings", "📗 Fully Judged", "📙 Partially Judged", "📕 Not Started"]
    selected_filter = st.sidebar.selectbox(
        "Filter by status:",
        filter_options,
        index=0,
        help="Filter meetings by their annotation status"
    )
    
    # Create a list of options for the sidebar based on INPUT data
    # Input data structure: {"UTTERANCE": {"text": "..."}}
    options = []
    filtered_indices = []  # Track original indices for filtered items
    
    for i, item in enumerate(input_data):
        subject = get_meeting_subject(item)
        utterance_text = item.get('UTTERANCE', {}).get('text', 'No Utterance')
        
        # Determine status indicator
        if utterance_text not in output_map:
            status = "⬜"  # No output data
            judgment_status = 'none'
        else:
            judgment_status = meeting_judgment_status.get(utterance_text, 'none')
            if judgment_status == 'complete':
                status = "📗"  # Fully judged (green book)
            elif judgment_status == 'partial':
                status = "📙"  # Partially judged (orange book)
            else:
                status = "📕"  # Not started (red book)
        
        # Apply filter
        include_item = False
        if selected_filter == "📋 All Meetings":
            include_item = True
        elif selected_filter == "📗 Fully Judged" and judgment_status == 'complete':
            include_item = True
        elif selected_filter == "📙 Partially Judged" and judgment_status == 'partial':
            include_item = True
        elif selected_filter == "📕 Not Started" and judgment_status == 'none':
            include_item = True
        
        if include_item:
            options.append(f"{i+1}. {status} {subject}")
            filtered_indices.append(i)
    
    # Show count of filtered results
    st.sidebar.caption(f"Showing {len(options)} of {len(input_data)} meetings")
    
    # Handle case where filter returns no results
    if not options:
        st.sidebar.warning("No meetings match the selected filter.")
        st.info("No meetings match the selected filter. Please change the filter to see meetings.")
        return
    
    # Use radio buttons for selection
    selected_option = st.sidebar.radio(
        "Choose a meeting context:",
        options,
        index=0
    )
    
    # Extract index from the selected option string "1. ✅ Subject..."
    selected_index = int(selected_option.split('.')[0]) - 1

    # === OVERALL SAVE & EXPORT BUTTONS IN SIDEBAR ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Save & Export All")
    
    sidebar_col1, sidebar_col2 = st.sidebar.columns(2)
    with sidebar_col1:
        if st.sidebar.button("💾 Save All", help="Save all annotations to temp file", key="sidebar_save_all"):
            save_annotations()
            st.sidebar.success("✅ Saved!")
    with sidebar_col2:
        if st.sidebar.button("📤 Export All", help="Export all annotated data", key="sidebar_export_all"):
            exported = export_annotated_data(output_data)
            with open(ANNOTATION_EXPORT_PATH, 'w', encoding='utf-8') as f:
                for item in exported:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            st.sidebar.success(f"✅ Exported!")
    
    # Reset All with confirmation
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚠️ Reset Options")
    
    reset_col1, reset_col2 = st.sidebar.columns(2)
    with reset_col1:
        # Reset current meeting only
        if st.sidebar.button("🔄 Reset Current", help="Reset annotations for current meeting only", key="reset_current"):
            st.session_state.show_reset_current_confirm = True
    with reset_col2:
        # Reset all annotations
        if st.sidebar.button("🗑️ Reset All", help="Reset ALL annotations (requires confirmation)", key="reset_all"):
            st.session_state.show_reset_all_confirm = True
    
    # Confirmation dialogs
    if st.session_state.get('show_reset_current_confirm', False):
        st.sidebar.warning("⚠️ Reset annotations for current meeting?")
        conf_col1, conf_col2 = st.sidebar.columns(2)
        with conf_col1:
            if st.sidebar.button("✅ Yes, Reset", key="confirm_reset_current"):
                # Get current utterance and reset its annotations
                current_utterance = input_data[selected_index].get('UTTERANCE', {}).get('text', '')
                if current_utterance in st.session_state.annotations:
                    del st.session_state.annotations[current_utterance]
                if current_utterance in st.session_state.new_assertions:
                    del st.session_state.new_assertions[current_utterance]
                # Clear expanded state for this meeting
                keys_to_remove = [k for k in st.session_state.expanded_assertions if k.startswith(f"{selected_index}_")]
                for k in keys_to_remove:
                    st.session_state.expanded_assertions.discard(k)
                save_annotations()
                st.session_state.show_reset_current_confirm = False
                st.rerun()
        with conf_col2:
            if st.sidebar.button("❌ Cancel", key="cancel_reset_current"):
                st.session_state.show_reset_current_confirm = False
                st.rerun()
    
    if st.session_state.get('show_reset_all_confirm', False):
        st.sidebar.error("⚠️ This will DELETE ALL annotations!")
        conf_col1, conf_col2 = st.sidebar.columns(2)
        with conf_col1:
            if st.sidebar.button("✅ Yes, Reset ALL", key="confirm_reset_all", type="primary"):
                st.session_state.annotations = {}
                st.session_state.new_assertions = {}
                st.session_state.expanded_assertions = set()
                save_annotations()
                st.session_state.show_reset_all_confirm = False
                st.rerun()
        with conf_col2:
            if st.sidebar.button("❌ Cancel", key="cancel_reset_all"):
                st.session_state.show_reset_all_confirm = False
                st.rerun()
    
    # Show annotation summary in sidebar
    total_annotated = len(st.session_state.annotations)
    total_new = sum(len(v) for v in st.session_state.new_assertions.values())
    st.sidebar.caption(f"📊 {total_annotated} items annotated | {total_new} new assertions")
    
    last_save = datetime.fromtimestamp(st.session_state.last_save_time).strftime("%H:%M:%S")
    st.sidebar.caption(f"🕐 Last save: {last_save}")
    st.sidebar.markdown("---")

    # Get selected input item
    input_item = input_data[selected_index]
    utterance_text = input_item.get('UTTERANCE', {}).get('text', '')
    
    # Try to find matching output
    output_item = output_map.get(utterance_text)

    # Display Content
    st.markdown("---")
    
    # Utterance Section
    st.subheader("🗣️ Utterance")
    st.info(f"**{utterance_text}**")

    # Check if we should auto-expand the Input Context section (from entity link click)
    expand_input = st.session_state.get("expand_input_context", False)
    linked_entity_id = st.session_state.get("linked_entity_id")
    linked_entity_type = st.session_state.get("linked_entity_type")
    linked_entity_data = st.session_state.get("linked_entity_data")
    
    # Clear the expand flag after using it
    if expand_input:
        st.session_state["expand_input_context"] = False

    # Input Data Toggle
    with st.expander("📥 View Input Context (LOD Data)", expanded=expand_input):
        # Show linked entity notification if applicable
        if linked_entity_id:
            st.success(f"🔗 Linked to **{linked_entity_type}** entity with ID: `{linked_entity_id}`")
            if st.button("❌ Clear Link", key="clear_entity_link"):
                st.session_state["linked_entity_id"] = None
                st.session_state["linked_entity_type"] = None
                st.session_state["linked_entity_data"] = None
                st.rerun()
        
        # View Mode Toggle
        view_mode = st.radio("View Mode", ["Card View", "JSON View"], horizontal=True, label_visibility="collapsed")
        
        if view_mode == "JSON View":
            st.json(input_item)
        else:
            # Card View Implementation
            
            # 1. User Info
            st.markdown("#### 👤 User")
            user_data = input_item.get('USER', {})
            if user_data:
                # Check if this user is the linked entity
                is_linked_user = linked_entity_type == "User" and linked_entity_data == user_data
                border_style = "border: 3px solid #28a745;" if is_linked_user else ""
                
                with st.container(border=True):
                    if is_linked_user:
                        st.markdown("🔗 **LINKED ENTITY**", help="This is the entity referenced by the assertion's sourceID")
                    st.markdown(f"**{user_data.get('displayName', 'Unknown')}**")
                    st.caption(f"ID: {user_data.get('id', 'N/A')}")
                    st.json(user_data, expanded=False)
            
            # 2. Entities
            st.markdown("#### 📦 Entities")
            entities = input_item.get('ENTITIES_TO_USE', [])
            
            if entities:
                # Group entities by type
                groups = {}
                for e in entities:
                    etype = e.get('type', 'Other')
                    if etype not in groups:
                        groups[etype] = []
                    groups[etype].append(e)
                
                # View Mode Toggle
                view_mode = st.radio("Display Mode", ["Card View", "JSON View"], horizontal=True, key="entity_view_mode")

                # Controls for Expand/Collapse
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("➕ Groups", help="Expand all entity groups"):
                    st.session_state["groups_expanded"] = True
                if c2.button("➖ Groups", help="Collapse all entity groups"):
                    st.session_state["groups_expanded"] = False
                if c3.button("➕ Details", help="Expand all JSON details"):
                    st.session_state["json_expanded"] = True
                if c4.button("➖ Details", help="Collapse all JSON details"):
                    st.session_state["json_expanded"] = False
                
                groups_expanded = st.session_state.get("groups_expanded", False)
                json_expanded = st.session_state.get("json_expanded", True)

                # Display groups
                for etype, group_items in groups.items():
                    # Check if this group contains the linked entity
                    contains_linked = linked_entity_type == etype if linked_entity_type else False
                    group_should_expand = groups_expanded or contains_linked
                    
                    # Show statistics in the expander label (add marker if contains linked entity)
                    label = f"**{etype}** ({len(group_items)} items)"
                    if contains_linked:
                        label = f"🔗 **{etype}** ({len(group_items)} items) - Contains linked entity"
                    
                    with st.expander(label, expanded=group_should_expand):
                        for i, item in enumerate(group_items):
                            # Check if this specific item is the linked entity
                            is_linked = False
                            if linked_entity_data:
                                # Match by multiple ID fields
                                for id_field in ['EventId', 'FileId', 'ChatId', 'MessageId', 'id', 'Id']:
                                    if id_field in item and id_field in linked_entity_data:
                                        if item[id_field] == linked_entity_data[id_field]:
                                            is_linked = True
                                            break
                            
                            # Individual Card
                            with st.container(border=True):
                                # Show linked indicator
                                if is_linked:
                                    st.markdown(
                                        "<div style='background-color: #d4edda; padding: 8px; border-radius: 5px; border-left: 5px solid #28a745; margin-bottom: 10px;'>🔗 <strong>LINKED ENTITY</strong> - This entity is referenced by the assertion's sourceID</div>",
                                        unsafe_allow_html=True
                                    )
                                
                                # Determine a title for the card
                                title = item.get('Subject') or item.get('FileName') or item.get('DisplayName') or item.get('EventId') or "Item"
                                header = get_entity_card_header(etype, title)
                                st.markdown(header, unsafe_allow_html=True)
                                
                                if view_mode == "Card View":
                                    # Render user card or generic card based on entity type
                                    if etype == "User":
                                        render_user_card(item)
                                    elif etype == "File":
                                        render_file_card(item, key_suffix=f"{etype}_{i}")
                                    else:
                                        render_generic_card(item)
                                        with st.expander("Raw JSON"):
                                            st.json(item)
                                else:
                                    st.json(item, expanded=json_expanded)
            else:
                st.info("No entities found in this context.")

    if output_item:
        # Two-column layout for Response and Assertions
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🤖 Generated Response")
            response_content = output_item.get('response', '*No response content*')
            
            # Apply highlighting
            highlight_matches = st.session_state.get("highlight_matches")
            highlight_term = st.session_state.get("highlight_term")
            
            if highlight_matches:
                # Colors for ranked matches: Strong -> Medium -> Weak
                # Using RGBA for fading effect
                colors = [
                    "rgba(255, 193, 7, 1.0)",  # Rank 1: Strong Yellow
                    "rgba(255, 193, 7, 0.6)",  # Rank 2: Medium Yellow
                    "rgba(255, 193, 7, 0.3)"   # Rank 3: Light Yellow
                ]
                
                for i, match_text in enumerate(highlight_matches):
                    if i < len(colors):
                        color = colors[i]
                        pattern = re.compile(re.escape(match_text), re.IGNORECASE)
                        response_content = pattern.sub(
                            lambda m: f"<mark style='background-color: {color}; color: black; border-radius: 3px;' title='Match Rank: {i+1}'>{m.group(0)}</mark>", 
                            response_content
                        )
            elif highlight_term:
                # Case-insensitive replacement with yellow background
                pattern = re.compile(re.escape(highlight_term), re.IGNORECASE)
                # We use a lambda to preserve the case of the matched text
                response_content = pattern.sub(lambda m: f"<mark style='background-color: #fff3cd; color: black;'>{m.group(0)}</mark>", response_content)
                
            st.markdown(response_content, unsafe_allow_html=True)

        with col2:
            st.subheader("✅ Assertions")
            
            # Annotation controls
            ann_col1, ann_col2, ann_col3 = st.columns([2, 2, 2])
            with ann_col1:
                if st.button("💾 Save Annotations", help="Save current annotations to temp file"):
                    save_annotations()
                    st.success("✅ Saved!")
            with ann_col2:
                if st.button("📤 Export Data", help="Export annotated data in Kening's format"):
                    exported = export_annotated_data(output_data)
                    with open(ANNOTATION_EXPORT_PATH, 'w', encoding='utf-8') as f:
                        for item in exported:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    st.success(f"✅ Exported to {ANNOTATION_EXPORT_PATH}")
            with ann_col3:
                # Auto-save indicator
                if auto_save_annotations():
                    st.toast("💾 Auto-saved annotations")
                last_save = datetime.fromtimestamp(st.session_state.last_save_time).strftime("%H:%M:%S")
                st.caption(f"🕐 Last save: {last_save}")
            
            assertions = output_item.get('assertions', [])
            
            # Calculate annotation statistics
            total_assertions = len(assertions) + len(get_new_assertions(utterance_text))
            good_count = sum(1 for i in range(len(assertions)) 
                           if get_annotation(utterance_text, i).get('is_good', True))
            new_count = len(get_new_assertions(utterance_text))
            
            st.markdown(f"**Stats:** {good_count}/{len(assertions)} marked good | {new_count} new added")
            
            # Expand/Collapse all buttons
            exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 2])
            with exp_col1:
                if st.button("📂 Expand All", key=f"expand_all_{selected_index}", help="Expand all assertion cards"):
                    for i in range(len(assertions)):
                        st.session_state.expanded_assertions.add(f"{selected_index}_{i}")
                    st.rerun()
            with exp_col2:
                if st.button("📁 Collapse All", key=f"collapse_all_{selected_index}", help="Collapse all assertion cards"):
                    for i in range(len(assertions)):
                        st.session_state.expanded_assertions.discard(f"{selected_index}_{i}")
                    st.rerun()
            with exp_col3:
                expanded_count = sum(1 for i in range(len(assertions)) if f"{selected_index}_{i}" in st.session_state.expanded_assertions)
                st.caption(f"📊 {expanded_count}/{len(assertions)} expanded")
            
            if not assertions:
                st.warning("No assertions found for this entry.")
            else:
                # Build entity index once for all assertions
                entity_index = build_entity_index(input_item) if input_item else {}
                
                for i, assertion in enumerate(assertions):
                    level = assertion.get('level', 'unknown').lower()
                    
                    # Color coding based on level
                    color_map = {
                        "critical": "red",
                        "expected": "green",
                        "aspirational": "orange"
                    }
                    color = color_map.get(level, "blue")
                    
                    # Check if sourceID has a matching reference
                    source = get_assertion_source(assertion)
                    has_reference = False
                    if source and is_source_id_format(assertion):
                        entity_info = find_entity_by_source_id(source, entity_index)
                        has_reference = entity_info is not None
                    
                    # Add evidence icon: 🟢 for matched, 🔴 for unmatched/missing
                    if source and is_source_id_format(assertion):
                        evidence_icon = "🟢" if has_reference else "🔴"
                    else:
                        evidence_icon = ""  # No icon for old format (text sources)
                    
                    # Get current annotation state
                    ann = get_annotation(utterance_text, i)
                    is_good = ann.get('is_good', True)
                    revision = ann.get('revision', '')
                    note = ann.get('note', '')
                    is_judged = ann.get('is_judged', False)
                    
                    # Revision/note indicator in header
                    has_feedback = revision or note
                    feedback_icon = "📝" if has_feedback else ""
                    
                    # Judgment status indicator
                    judged_icon = "✅" if is_judged else "⬜"
                    
                    # Track expander state with unique key
                    expander_key = f"{selected_index}_{i}"
                    is_expanded = expander_key in st.session_state.expanded_assertions
                    
                    # Card-like expander for each assertion
                    with st.expander(f"{judged_icon} {evidence_icon} {feedback_icon} :{color}[**{level.upper()}**] - {assertion.get('text', '')[:50]}...", expanded=is_expanded):
                        # Track that this expander is now open
                        st.session_state.expanded_assertions.add(expander_key)
                        
                        # === ANNOTATION CONTROLS ===
                        st.markdown("##### 📋 Annotation")
                        
                        # Full assertion text in a highlighted box
                        st.markdown(
                            f"""<div style='background-color: #e8f4fd; padding: 15px; border-radius: 8px; 
                                border-left: 4px solid #1976d2; margin-bottom: 15px;'>
                                <strong style='color: #1565c0;'>Full Assertion:</strong><br>
                                <span style='color: #333; font-size: 1em;'>{assertion.get('text', '')}</span>
                            </div>""",
                            unsafe_allow_html=True
                        )
                        
                        st.caption("Check this assertion if it is correct; uncheck it if it is incorrect. Optionally, provide an explanation in the note below about why the assertion is incorrect.")
                        
                        # Get current confidence value
                        is_confident = ann.get('is_confident', True)
                        
                        # Three columns: correctness, confidence, and mark as judged button
                        col_correct, col_confident, col_judged = st.columns([1, 1, 1])
                        
                        with col_correct:
                            # Checkbox for correct/incorrect - green when checked (correct)
                            # Use selected_index in key to prevent collisions between different entries
                            is_good_new = st.checkbox(
                                "✅ This assertion is correct", 
                                value=is_good, 
                                key=f"good_{selected_index}_{i}"
                            )
                            if is_good_new != is_good:
                                # Auto-mark as judged when user makes a judgment
                                set_annotation(utterance_text, i, is_good=is_good_new, is_judged=True, original=assertion.get('text', ''))
                                save_annotations()
                        
                        with col_confident:
                            # Checkbox for confidence in judgment
                            is_confident_new = st.checkbox(
                                "🎯 Confident in judgment",
                                value=is_confident,
                                key=f"confident_{selected_index}_{i}"
                            )
                            if is_confident_new != is_confident:
                                # Auto-mark as judged when user indicates confidence level
                                set_annotation(utterance_text, i, is_confident=is_confident_new, is_judged=True)
                                save_annotations()
                        
                        with col_judged:
                            # Checkbox to mark assertion as judged (local update, no page jump)
                            is_judged_new = st.checkbox(
                                "📋 Judged",
                                value=is_judged,
                                key=f"judged_{selected_index}_{i}",
                                help="Check this when you've finished reviewing this assertion"
                            )
                            if is_judged_new != is_judged:
                                set_annotation(utterance_text, i, is_judged=is_judged_new)
                                save_annotations()
                        
                        # Local status indicator that updates with checkbox state
                        # Use the checkbox value directly for immediate feedback
                        current_judged = st.session_state.get(f"judged_{selected_index}_{i}", is_judged)
                        if current_judged:
                            st.success("✅ **Judged** - This assertion has been reviewed")
                        else:
                            st.info("⬜ **Not yet judged** - Check the 'Judged' box when done reviewing")
                        
                        # Note field - always visible for comments
                        st.markdown("**Note:** (Optional comments or explanation)")
                        new_note = st.text_area(
                            "Add your notes here",
                            value=note,
                            key=f"note_{selected_index}_{i}",
                            height=80,
                            placeholder="Enter any comments about this assertion...",
                            label_visibility="collapsed"
                        )
                        if new_note != note:
                            set_annotation(utterance_text, i, note=new_note)
                        
                        # Revision text area - always visible for consistency
                        st.markdown("**Revision:** (Optional - suggest an improved assertion text)")
                        new_revision = st.text_area(
                            "Revised assertion text",
                            value=revision if revision else "",
                            key=f"revision_{selected_index}_{i}",
                            height=100,
                            placeholder="Enter a revised version of this assertion if needed...",
                            label_visibility="collapsed"
                        )
                        if new_revision != revision:
                            set_annotation(utterance_text, i, revision=new_revision, original=assertion.get('text', ''))
                        
                        # Collapse button to close this expander when done
                        if st.button("🔼 Done - Collapse", key=f"collapse_{selected_index}_{i}", help="Close this assertion card"):
                            st.session_state.expanded_assertions.discard(expander_key)
                            st.rerun()
                        
                        st.markdown("---")
                        
                        # === JUSTIFICATION/REASONING CONTENT ===
                        # Handle both old format (reasoning) and new format (justification)
                        reasoning = get_assertion_reasoning(assertion)
                        if reasoning:
                            # Label based on format: new format uses 'justification', old uses 'reasoning'
                            label = "**Justification:**" if 'justification' in assertion else "**Reasoning:**"
                            st.markdown(label)
                            st.info(reasoning.get('reason', 'No justification provided.'))
                            
                            # Handle both old (source) and new (sourceID) formats
                            source = get_assertion_source(assertion)
                            if source:
                                # Check if using new sourceID format
                                if is_source_id_format(assertion):
                                    st.markdown("**Source ID:**")
                                    
                                    # Use the pre-built entity index (already built above)
                                    entity_info = find_entity_by_source_id(source, entity_index)
                                    
                                    if entity_info:
                                        entity_type, entity_idx, entity_data = entity_info
                                        
                                        # Get entity display info
                                        entity_name = (entity_data.get('FileName') or 
                                                      entity_data.get('Subject') or 
                                                      entity_data.get('ChatName') or 
                                                      entity_data.get('DisplayName') or 
                                                      entity_data.get('displayName') or
                                                      'Unknown')
                                        icon = ENTITY_STYLES.get(entity_type, {}).get('icon', '📦')
                                        style_color = ENTITY_STYLES.get(entity_type, {}).get('color', '#6c757d')
                                        
                                        # Render beautifully formatted inline entity card (matching LOD card style)
                                        with st.container(border=True):
                                            # Header with icon and entity type
                                            st.markdown(
                                                f"""<div style='background: linear-gradient(135deg, {style_color}22, {style_color}11); 
                                                    padding: 10px 15px; margin: -1rem -1rem 1rem -1rem; 
                                                    border-bottom: 2px solid {style_color}; border-radius: 8px 8px 0 0;'>
                                                    <span style='font-size: 1.5em;'>{icon}</span>
                                                    <strong style='font-size: 1.2em; color: {style_color}; margin-left: 8px;'>{entity_type}</strong>
                                                    <span style='float: right; background: #d4edda; color: #155724; padding: 2px 8px; 
                                                        border-radius: 12px; font-size: 0.75em;'>✓ Matched</span>
                                                </div>""",
                                                unsafe_allow_html=True
                                            )
                                            
                                            # Entity name as title
                                            st.markdown(f"### {entity_name}")
                                            st.caption(f"🔗 `{source}`")
                                            
                                            # Render card content based on entity type (like LOD cards)
                                            if entity_type == 'User':
                                                render_user_card(entity_data)
                                            elif entity_type == 'File':
                                                render_file_card(entity_data, key_suffix=f"inline_{i}")
                                            else:
                                                # For other entity types, render a generic styled card
                                                render_generic_card(entity_data)
                                            
                                            # Always show raw JSON in expander
                                            with st.expander("📋 Raw JSON"):
                                                st.json(entity_data)
                                        
                                        # Optional: Button to jump to full entity in Input Context
                                        if st.button(f"🔗 View in Input Context", key=f"link_entity_{selected_index}_{i}", help=f"Jump to {entity_type} in Input Context"):
                                            st.session_state["linked_entity_id"] = source
                                            st.session_state["linked_entity_type"] = entity_type
                                            st.session_state["linked_entity_data"] = entity_data
                                            st.session_state["expand_input_context"] = True
                                            st.rerun()
                                    else:
                                        # Unmatched - show in light red with proper styling
                                        with st.container(border=True):
                                            st.markdown(
                                                f"""<div style='background: linear-gradient(135deg, #dc354522, #dc354511); 
                                                    padding: 10px 15px; margin: -1rem -1rem 1rem -1rem; 
                                                    border-bottom: 2px solid #dc3545; border-radius: 8px 8px 0 0;'>
                                                    <span style='font-size: 1.5em;'>⚠️</span>
                                                    <strong style='font-size: 1.2em; color: #dc3545; margin-left: 8px;'>Unmatched Source ID</strong>
                                                    <span style='float: right; background: #f8d7da; color: #721c24; padding: 2px 8px; 
                                                        border-radius: 12px; font-size: 0.75em;'>✗ Not Found</span>
                                                </div>""",
                                                unsafe_allow_html=True
                                            )
                                            st.code(source, language=None)
                                            st.warning("This ID was not found in the LOD input data. It may be a synthetic/generated reference.")
                                else:
                                    st.markdown("**Source:**")
                                    # Highlight the source text in yellow as requested
                                    st.markdown(
                                        f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 5px solid #ffc107; color: #856404;'>{source}</div>", 
                                        unsafe_allow_html=True
                                    )
                                
                                # Button to locate in response
                                # Check if pre-computed matches exist
                                matched_segments = assertion.get('matched_segments', [])
                                
                                if matched_segments:
                                    # Use pre-computed matches
                                    if st.button(f"🔍 Show Evidence", key=f"locate_{selected_index}_{i}"):
                                        st.session_state["highlight_matches"] = matched_segments
                                        st.session_state["active_assertion_index"] = i
                                        st.rerun()
                                else:
                                    st.caption("⚠️ No pre-computed matches found. Run compute_assertion_matches.py first.")
                                
                                # Match display and clear (only for the active assertion)
                                if st.session_state.get("active_assertion_index") == i and st.session_state.get("highlight_matches"):
                                    matches = st.session_state["highlight_matches"]
                                    
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.caption(f"✅ Showing {len(matches)} evidence passages (Strongest to Weakest)")
                                    with col2:
                                        if st.button("❌", key=f"clear_{selected_index}_{i}", help="Clear Highlight"):
                                            st.session_state["highlight_matches"] = None
                                            st.session_state["highlight_term"] = None
                                            st.session_state["active_assertion_index"] = None
                                            st.rerun()
                        else:
                            st.markdown("*No reasoning provided.*")
            
            # === DISPLAY USER-ADDED ASSERTIONS ===
            new_assertions = get_new_assertions(utterance_text)
            if new_assertions:
                st.markdown("---")
                st.markdown("### ➕ User-Added Assertions")
                for j, new_assert in enumerate(new_assertions):
                    level = new_assert.get('level', 'expected')
                    color = {"critical": "red", "expected": "green", "aspirational": "orange"}.get(level, "blue")
                    with st.expander(f"🆕 :{color}[**{level.upper()}**] - {new_assert.get('text', '')[:50]}..."):
                        st.markdown(f"**Assertion:** {new_assert.get('text', '')}")
                        st.markdown(f"**Level:** {level}")
                        if new_assert.get('justification', {}).get('reason'):
                            st.markdown(f"**Justification:** {new_assert['justification']['reason']}")
                        if new_assert.get('justification', {}).get('sourceID'):
                            st.markdown(f"**Source ID:** `{new_assert['justification']['sourceID']}`")
            
            # === ADD NEW ASSERTION FORM ===
            st.markdown("---")
            with st.expander("➕ Add New Assertion", expanded=False):
                st.markdown("Create a new assertion for this utterance:")
                
                new_text = st.text_area(
                    "Assertion Text",
                    placeholder="The response should...",
                    key=f"new_assertion_text_{selected_index}",
                    height=100
                )
                
                new_level = st.selectbox(
                    "Level",
                    ["critical", "expected", "aspirational"],
                    index=1,
                    key=f"new_assertion_level_{selected_index}"
                )
                
                new_reason = st.text_area(
                    "Justification Reason",
                    placeholder="Why is this assertion important?",
                    key=f"new_assertion_reason_{selected_index}",
                    height=80
                )
                
                new_source_id = st.text_input(
                    "Source ID (optional)",
                    placeholder="Entity ID from LOD data (e.g., FileId, EventId)",
                    key=f"new_assertion_source_{selected_index}"
                )
                
                if st.button("➕ Add Assertion", key=f"add_new_assertion_btn_{selected_index}"):
                    if new_text:
                        new_assertion_data = {
                            "text": new_text,
                            "level": new_level,
                            "justification": {
                                "reason": new_reason,
                                "sourceID": new_source_id
                            }
                        }
                        add_new_assertion(utterance_text, new_assertion_data)
                        st.success("✅ New assertion added!")
                        st.rerun()
                    else:
                        st.error("Please enter assertion text.")
    else:
        st.warning("⚠️ No generated output found for this input meeting.")

if __name__ == "__main__":
    main()
