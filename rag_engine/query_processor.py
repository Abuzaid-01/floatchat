# from typing import Dict, List, Tuple
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.db_setup import DatabaseSetup
from vector_store.vector_db import FAISSVectorStore
from vector_store.embeddings import EmbeddingGenerator
from rag_engine.sql_generator import SQLGenerator
import pandas as pd
import time

class QueryProcessor:
    """
    Main RAG pipeline processor.
    Orchestrates: Vector search → SQL generation → Database query → Response
    """
    
    def __init__(self):
        self.db_setup = DatabaseSetup()
        self.vector_store = FAISSVectorStore()
        self.vector_store.load()
        self.embedding_generator = EmbeddingGenerator()
        self.sql_generator = SQLGenerator()
    
    def process_query(self, user_query: str, top_k: int = 3) -> Dict:
        """
        Complete RAG pipeline for processing user queries.
        
        Pipeline steps:
        1. Generate embedding for user query
        2. Search vector store for similar profiles
        3. Use retrieved context to generate SQL
        4. Execute SQL query on database
        5. Return structured results
        
        Args:
            user_query: Natural language question from user
            top_k: Number of similar profiles to retrieve
            
        Returns:
            Dictionary with query results, metadata, and SQL
        """
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🔍 Processing Query: {user_query}")
        print(f"{'='*60}")
        
        # Step 1: Vector Search
        print("\n📊 Step 1: Searching vector store...")
        query_embedding = self.embedding_generator.generate_embedding(user_query)
        similar_profiles = self.vector_store.search(query_embedding, k=top_k)
        
        # Extract context from similar profiles
        context = self._format_context(similar_profiles)
        print(f"✅ Found {len(similar_profiles)} similar profiles")
        
        # Step 2: Generate SQL
        print("\n🔧 Step 2: Generating SQL query...")
        sql_query = self.sql_generator.generate_sql(user_query, context)
        
        if not sql_query or not self.sql_generator.validate_sql(sql_query):
            return {
                'success': False,
                'error': 'Could not generate valid SQL query',
                'query': user_query
            }
        
        # Step 3: Execute SQL
        print("\n💾 Step 3: Executing database query...")
        results_df, error = self._execute_sql(sql_query)
        
        if error:
            return {
                'success': False,
                'error': error,
                'query': user_query,
                'sql': sql_query
            }
        
        # Step 4: Prepare response
        execution_time = time.time() - start_time
        print(f"\n✅ Query completed in {execution_time:.2f} seconds")
        print(f"📈 Retrieved {len(results_df)} records")
        
        return {
            'success': True,
            'query': user_query,
            'sql': sql_query,
            'results': results_df,
            'result_count': len(results_df),
            'similar_profiles': similar_profiles,
            'execution_time': execution_time
        }
    
    def _format_context(self, similar_profiles: List[Tuple[float, dict]]) -> str:
        """Format retrieved profiles as context for LLM"""
        context_parts = []
        for i, (score, metadata) in enumerate(similar_profiles, 1):
            context_parts.append(
                f"{i}. {metadata.get('summary_text', 'No summary available')}"
            )
        return "\n".join(context_parts)
    
    def _execute_sql(self, sql_query: str) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Execute SQL query and return results as DataFrame.
        
        Returns:
            Tuple of (DataFrame, error_message)
        """
        session = self.db_setup.get_session()
        
        try:
            # Execute query
            result = session.execute(text(sql_query))
            
            # Convert to DataFrame
            rows = result.fetchall()
            if len(rows) == 0:
                return pd.DataFrame(), None
            
            # Get column names
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            
            return df, None
            
        except Exception as e:
            error_msg = f"SQL execution error: {str(e)}"
            print(f"❌ {error_msg}")
            return pd.DataFrame(), error_msg
            
        finally:
            session.close()
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics from query results"""
        if df.empty:
            return {}
        
        stats = {
            'record_count': len(df),
            'columns': list(df.columns)
        }
        
        # Add numeric statistics
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            stats[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median())
            }
        
        return stats
    

# Add to QueryProcessor class

def validate_query_safety(self, user_query: str) -> bool:
    """Validate query is safe and appropriate"""
    # Check for SQL injection attempts
    dangerous_patterns = [
        r';\s*DROP',
        r';\s*DELETE',
        r';\s*UPDATE',
        r'UNION\s+SELECT',
        r'--',
        r'/\*.*\*/',
    ]
    
    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, user_query, re.IGNORECASE):
            return False
    
    return True

def get_query_suggestions(self, user_query: str) -> List[str]:
    """Get query suggestions based on input"""
    suggestions = []
    
    query_lower = user_query.lower()
    
    if 'temperature' in query_lower:
        suggestions.append("Show temperature-depth profiles")
        suggestions.append("Compare temperature across regions")
    
    if 'salinity' in query_lower:
        suggestions.append("Analyze salinity distribution")
        suggestions.append("Show T-S diagram")
    
    if any(region in query_lower for region in ['arabian', 'bengal', 'indian']):
        suggestions.append("Show geographic distribution on map")
        suggestions.append("Compare with other regions")
    
    return suggestions[:3]

def log_query(self, user_query: str, sql_query: str, result_count: int, 
              execution_time: float, success: bool):
    """Log query to database for analytics"""
    from database.models import QueryLog
    
    session = self.db_setup.get_session()
    
    try:
        log = QueryLog(
            user_query=user_query,
            generated_sql=sql_query,
            result_count=result_count,
            execution_time=execution_time,
            success=1 if success else 0
        )
        session.add(log)
        session.commit()
    except Exception as e:
        print(f"Failed to log query: {e}")
    finally:
        session.close()    

# Usage example
if __name__ == "__main__":
    processor = QueryProcessor()
    
    # Test query
    result = processor.process_query(
        "Show me temperature profiles in the Arabian Sea between 10-20 degrees North"
    )
    
    if result['success']:
        print(f"\n📊 Results Preview:")
        print(result['results'].head())
        print(f"\n📈 Statistics:")
        stats = processor.get_statistics(result['results'])
        print(stats)
    else:
        print(f"❌ Error: {result['error']}")
