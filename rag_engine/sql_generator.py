import os
from typing import Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI  # ← CHANGED
from langchain_core.prompts import PromptTemplate  # ← CHANGED: Use langchain_core

from rag_engine.prompt_templates import SQL_GENERATION_PROMPT
from dotenv import load_dotenv

load_dotenv()

class SQLGenerator:
    """
    Convert natural language queries to SQL using Gemini LLM.
    Now using FREE Google Gemini API!
    """
    
    def __init__(self):
        # Initialize Gemini LLM (FREE!)
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            temperature=0.1,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print(f"✅ Initialized Gemini: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["user_query", "context"],
            template=SQL_GENERATION_PROMPT
        )
    
    def generate_sql(self, user_query: str, context: str = "") -> str:
        """
        Generate SQL query from natural language using Gemini.
        
        Args:
            user_query: User's natural language question
            context: Retrieved context from vector store
            
        Returns:
            SQL query string
        """
        try:
            # Format prompt with user query and context
            formatted_prompt = self.prompt_template.format(
                user_query=user_query,
                context=context
            )
            
            # Get Gemini response
            response = self.llm.invoke(formatted_prompt)
            sql_query = response.content.strip()
            
            # Clean SQL query
            sql_query = self._clean_sql(sql_query)
            
            print(f"📝 Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            return None
    
    def _clean_sql(self, sql: str) -> str:
        """Remove markdown code blocks and extra whitespace"""
        # Remove markdown code blocks like ```sql or ```
        import re
        sql = re.sub(r'```(?:sql)?\s*', '', sql)
        sql = re.sub(r'```\s*$', '', sql)
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        return sql.strip()
    
    def validate_sql(self, sql: str) -> bool:
        """Basic SQL validation to prevent SQL injection"""
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 'ALTER']
        sql_upper = sql.upper()
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                print(f"⚠️ Dangerous SQL keyword detected: {keyword}")
                return False
        
        return True
