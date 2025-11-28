import streamlit as st
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Assertion Generation Visualizer",
    page_icon="📊",
    layout="wide"
)

# File paths
INPUT_FILE = os.path.join("docs", "LOD_1121.jsonl")
OUTPUT_FILE = os.path.join("docs", "11_25_output.jsonl")  # Updated to new format


def get_assertion_reasoning(assertion):
    """Get reasoning from assertion, handling both old and new formats."""
    if 'justification' in assertion:
        return assertion['justification']
    elif 'reasoning' in assertion:
        return assertion['reasoning']
    return {}


def get_assertion_source(assertion):
    """Get source reference from assertion, handling both formats."""
    reasoning = get_assertion_reasoning(assertion)
    return reasoning.get('sourceID') or reasoning.get('source') or ''


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
        for key in ['id', 'userId', 'userPrincipalName']:
            if key in user_data and user_data[key]:
                index[user_data[key]] = ('User', 0, user_data)
    
    # Index all entities
    entities = input_item.get('ENTITIES_TO_USE', [])
    for i, entity in enumerate(entities):
        etype = entity.get('type', 'Other')
        
        # Index by various ID fields
        id_fields = [
            'FileId', 'ChatId', 'EventId', 'ChannelMessageId', 'ChannelId',
            'ChannelMessageReplyId', 'OnlineMeetingId', 'EmailId', 'MessageId', 'id', 'Id'
        ]
        for field in id_fields:
            if field in entity and entity[field]:
                index[entity[field]] = (etype, i, entity)
        
        # Index ChatMessageIds from nested ChatMessages in Chat entities
        if etype == 'Chat' and 'ChatMessages' in entity:
            for msg in entity['ChatMessages']:
                if 'ChatMessageId' in msg:
                    index[msg['ChatMessageId']] = ('ChatMessage', i, entity)
    
    return index


def find_entity_by_source_id(source_id, entity_index):
    """Find an entity matching the given sourceID."""
    if not source_id or not entity_index:
        return None
    
    # Direct match
    if source_id in entity_index:
        return entity_index[source_id]
    
    # Try partial match
    for key, value in entity_index.items():
        if source_id in str(key) or str(key) in source_id:
            return value
    
    return None

@st.cache_data
def load_data(file_path):
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data

def main():
    st.title("📊 Assertion Generation Visualizer")
    st.markdown("Visualize inputs from `LOD_1121.jsonl` and outputs from `11_25_output.jsonl`.")

    # Load data
    input_data = load_data(INPUT_FILE)
    output_data = load_data(OUTPUT_FILE)

    if not input_data:
        st.error(f"Could not load input data from {INPUT_FILE}")
        return

    # Create a lookup for output data based on utterance
    output_lookup = {item.get('utterance'): item for item in output_data}

    # Sidebar for navigation
    st.sidebar.header("Navigation")
    
    # Create options for the selectbox (Index: Utterance Preview)
    options = [f"{i}: {item.get('UTTERANCE', {}).get('text', '')[:50]}..." for i, item in enumerate(input_data)]
    selected_option = st.sidebar.selectbox("Select an Example", options)
    
    if selected_option:
        selected_index = int(selected_option.split(":")[0])
        input_item = input_data[selected_index]
        utterance_text = input_item.get('UTTERANCE', {}).get('text', '')
        
        # Find corresponding output
        output_item = output_lookup.get(utterance_text)

        # Main Content
        st.header(f"Utterance: **{utterance_text}**")
        
        # Layout: Tabs for Input and Output
        tab1, tab2 = st.tabs(["📥 Input Context", "📤 Generated Output & Assertions"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("User Info")
                user_info = input_item.get('USER', {})
                st.json(user_info)
                
                st.subheader("Utterance Details")
                st.json(input_item.get('UTTERANCE', {}))

            with col2:
                st.subheader("Entities to Use")
                entities = input_item.get('ENTITIES_TO_USE', [])
                if entities:
                    for i, entity in enumerate(entities):
                        with st.expander(f"Entity {i+1}: {entity.get('type', 'Unknown Type')} - {entity.get('FileName', entity.get('Subject', 'No Name'))}"):
                            st.json(entity)
                else:
                    st.info("No entities provided.")

        with tab2:
            if output_item:
                st.subheader("Generated Response")
                response_text = output_item.get('response', 'No response text found.')
                st.markdown(response_text)
                
                st.divider()
                
                st.subheader("Assertions")
                assertions = output_item.get('assertions', [])
                
                if assertions:
                    for assertion in assertions:
                        level = assertion.get('level', 'unknown').lower()
                        color = "blue"
                        if level == 'critical':
                            color = "red"
                        elif level == 'expected':
                            color = "green"
                        elif level == 'aspirational':
                            color = "orange"
                        
                        with st.container():
                            st.markdown(f":{color}[**{level.upper()}**] {assertion.get('text')}")
                            # Handle both old (reasoning) and new (justification) formats
                            reasoning = get_assertion_reasoning(assertion)
                            if reasoning:
                                # Label based on format
                                expander_label = "Justification" if 'justification' in assertion else "Reasoning"
                                with st.expander(expander_label):
                                    st.markdown(f"**Reason:** {reasoning.get('reason', 'N/A')}")
                                    
                                    # Handle both old (source) and new (sourceID) formats
                                    source = get_assertion_source(assertion)
                                    if is_source_id_format(assertion):
                                        st.markdown("**Source ID:**")
                                        # Build entity index and try to find matching entity
                                        entity_index = build_entity_index(input_item)
                                        entity_info = find_entity_by_source_id(source, entity_index)
                                        
                                        if entity_info:
                                            entity_type, entity_idx, entity_data = entity_info
                                            # Matched - show in green
                                            entity_name = (entity_data.get('FileName') or 
                                                          entity_data.get('Subject') or 
                                                          entity_data.get('ChatName') or 
                                                          entity_data.get('DisplayName') or 'Unknown')
                                            st.markdown(
                                                f"<div style='background-color: #d4edda; padding: 8px; border-radius: 4px; border-left: 4px solid #28a745;'>"
                                                f"✅ <code>{source}</code><br>"
                                                f"<strong>{entity_type}</strong>: {entity_name}</div>",
                                                unsafe_allow_html=True
                                            )
                                        else:
                                            # Unmatched - show in light red
                                            st.markdown(
                                                f"<div style='background-color: #f8d7da; padding: 8px; border-radius: 4px; border-left: 4px solid #dc3545;'>"
                                                f"⚠️ <code>{source}</code><br>"
                                                f"<small>Unmatched ID - not found in LOD data</small></div>",
                                                unsafe_allow_html=True
                                            )
                                    else:
                                        st.markdown(f"**Source:** {source or 'N/A'}")
                            st.divider()
                else:
                    st.info("No assertions found.")
            else:
                st.warning("No corresponding output found for this utterance in `11_25_output.jsonl`.")

if __name__ == "__main__":
    main()
