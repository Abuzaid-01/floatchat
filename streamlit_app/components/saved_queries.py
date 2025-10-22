"""
Saved queries management system
"""

import streamlit as st
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class SavedQueriesManager:
    """Manage user saved queries"""
    
    def __init__(self, save_dir: str = "./data_cache/saved_queries"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_query(self, name: str, query: str, description: str = "", tags: List[str] = []):
        """Save a query"""
        query_data = {
            "name": name,
            "query": query,
            "description": description,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "executions": 0
        }
        
        file_path = self.save_dir / f"{name}.json"
        
        with open(file_path, 'w') as f:
            json.dump(query_data, f, indent=2)
        
        return True
    
    def load_query(self, name: str) -> Dict:
        """Load a saved query"""
        file_path = self.save_dir / f"{name}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_queries(self) -> List[str]:
        """List all saved queries"""
        return [f.stem for f in self.save_dir.glob("*.json")]
    
    def delete_query(self, name: str):
        """Delete a saved query"""
        file_path = self.save_dir / f"{name}.json"
        if file_path.exists():
            file_path.unlink()
    
    def update_execution_count(self, name: str):
        """Increment execution count"""
        query_data = self.load_query(name)
        if query_data:
            query_data['executions'] += 1
            query_data['last_executed'] = datetime.now().isoformat()
            
            file_path = self.save_dir / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(query_data, f, indent=2)

def render_saved_queries_ui(query_processor):
    """Render saved queries UI in Streamlit"""
    
    st.subheader("💾 Saved Queries")
    
    manager = SavedQueriesManager()
    
    # Tabs for manage/load
    tab1, tab2 = st.tabs(["📂 Load Saved", "💾 Save Current"])
    
    with tab1:
        saved = manager.list_queries()
        
        if not saved:
            st.info("No saved queries yet")
        else:
            selected = st.selectbox("Select a query", saved)
            
            if selected:
                query_data = manager.load_query(selected)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.text(f"📝 {query_data['description']}")
                
                with col2:
                    st.metric("Executions", query_data['executions'])
                
                with col3:
                    if st.button("🗑️ Delete"):
                        manager.delete_query(selected)
                        st.rerun()
                
                st.code(query_data['query'], language='sql')
                
                if st.button("▶️ Execute"):
                    with st.spinner("Executing..."):
                        result = query_processor.process_query(query_data['query'])
                        manager.update_execution_count(selected)
                        st.session_state.last_query_results = result
                        st.success("Query executed!")
    
    with tab2:
        if st.session_state.get('last_query_results'):
            query_name = st.text_input("Query Name")
            query_desc = st.text_area("Description")
            query_tags = st.multiselect("Tags", ["comparison", "analysis", "regional", "temporal"])
            
            if st.button("💾 Save Query"):
                last_result = st.session_state.last_query_results
                manager.save_query(
                    query_name,
                    last_result['sql'],
                    query_desc,
                    query_tags
                )
                st.success(f"✅ Saved as '{query_name}'")
        else:
            st.info("Run a query first to save it")