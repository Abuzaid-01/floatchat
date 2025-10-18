import streamlit as st
from typing import Dict
from rag_engine.query_processor import QueryProcessor
from rag_engine.response_generator import ResponseGenerator

class ChatInterface:
    """
    Interactive chat interface for FloatChat.
    Handles user queries and displays responses.
    """
    
    def __init__(self, query_processor: QueryProcessor):
        self.query_processor = query_processor
        self.response_generator = ResponseGenerator()
        
        # Initialize chat history in session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def render(self):
        """Render the chat interface"""
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show data if available
                if message.get("data") is not None:
                    with st.expander("📊 View Query Results"):
                        st.dataframe(message["data"].head(20))
                        st.caption(f"Showing first 20 of {len(message['data'])} records")
        
        # Chat input
        if prompt := st.chat_input("Ask me about ARGO ocean data..."):
            # Add user message to chat
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process query and generate response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching ARGO database..."):
                    result = self._process_user_query(prompt)
                    
                    if result['success']:
                        # Generate natural language response
                        context = self._format_similar_profiles(
                            result.get('similar_profiles', [])
                        )
                        response = self.response_generator.generate_response(
                            prompt,
                            result['results'],
                            context
                        )
                        
                        st.markdown(response)
                        
                        # Show metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Records Found", result['result_count'])
                        with col2:
                            st.metric("Execution Time", f"{result['execution_time']:.2f}s")
                        with col3:
                            st.metric("SQL Generated", "✅")
                        
                        # Show SQL query
                        with st.expander("🔧 View Generated SQL"):
                            st.code(result['sql'], language='sql')
                        
                        # Add assistant message to chat
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "data": result['results'],
                            "sql": result['sql']
                        })
                        
                        # Store results for other tabs
                        st.session_state.last_query_results = result
                        
                    else:
                        error_msg = f"❌ Error: {result['error']}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    def _process_user_query(self, query: str) -> Dict:
        """Process user query through RAG pipeline"""
        try:
            result = self.query_processor.process_query(query, top_k=3)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _format_similar_profiles(self, similar_profiles: list) -> str:
        """Format similar profiles for context"""
        if not similar_profiles:
            return ""
        
        context_parts = []
        for i, (score, metadata) in enumerate(similar_profiles, 1):
            context_parts.append(
                f"{i}. {metadata.get('summary_text', 'No summary')}"
            )
        return "\n".join(context_parts)

# Clear chat button
def render_clear_chat_button():
    """Add button to clear chat history"""
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.last_query_results = None
        st.rerun()
