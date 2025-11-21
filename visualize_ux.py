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
OUTPUT_FILE = os.path.join("docs", "output_v2.jsonl")

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
    st.markdown("Visualize inputs from `LOD_1121.jsonl` and outputs from `output_v2.jsonl`.")

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
        st.header(f"Utterance: {utterance_text}")
        
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
                            if 'reasoning' in assertion:
                                with st.expander("Reasoning"):
                                    st.markdown(f"**Reason:** {assertion['reasoning'].get('reason')}")
                                    st.markdown(f"**Source:** {assertion['reasoning'].get('source')}")
                            st.divider()
                else:
                    st.info("No assertions found.")
            else:
                st.warning("No corresponding output found for this utterance in `output_v2.jsonl`.")

if __name__ == "__main__":
    main()
