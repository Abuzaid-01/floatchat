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




# import os
# import re
# from typing import Dict, Optional, List
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from dotenv import load_dotenv

# load_dotenv()


# class AdvancedSQLGenerator:
#     """
#     Production-grade SQL generator with:
#     - Smart query understanding
#     - Spatial query optimization
#     - Temporal query handling
#     - Safety validation
#     - Query explanation
#     """
    
#     # Database schema
#     SCHEMA = """
#     Table: argo_profiles
#     Columns:
#         - id: INTEGER (Primary Key)
#         - float_id: VARCHAR(50) - Float identifier
#         - cycle_number: INTEGER - Measurement cycle
#         - latitude: FLOAT - Latitude in degrees (-90 to 90)
#         - longitude: FLOAT - Longitude in degrees (-180 to 180)
#         - timestamp: TIMESTAMP - Measurement date/time
#         - pressure: FLOAT - Pressure in dbar (depth proxy)
#         - temperature: FLOAT - Temperature in Celsius
#         - salinity: FLOAT - Salinity in PSU
#         - dissolved_oxygen: FLOAT - DO in μmol/kg
#         - chlorophyll: FLOAT - Chlorophyll in mg/m³
#         - ph: FLOAT - pH value
#         - depth_m: FLOAT - Approximate depth in meters
#         - ocean_region: VARCHAR(50) - Ocean region name
#         - year: INTEGER - Year of measurement
#         - month: INTEGER - Month of measurement
#         - temp_qc: INTEGER - Temperature QC flag
#         - sal_qc: INTEGER - Salinity QC flag
#         - data_mode: VARCHAR(1) - R/D/A (Realtime/Delayed/Adjusted)
#         - platform_type: VARCHAR(50) - Platform type
    
#     Indexes:
#         - idx_lat_lon: (latitude, longitude)
#         - idx_timestamp: (timestamp)
#         - idx_float_id: (float_id)
#         - idx_spatial_temporal: (latitude, longitude, timestamp)
#     """
    
#     SQL_PROMPT_TEMPLATE = """You are an expert PostgreSQL query generator for oceanographic ARGO float data.

# Database Schema:
# {schema}

# User Query: {user_query}

# Context from similar profiles:
# {context}

# IMPORTANT RULES:
# 1. ALWAYS use proper PostgreSQL syntax
# 2. For geographic queries, use bounding boxes:
#    - latitude BETWEEN lat_min AND lat_max
#    - longitude BETWEEN lon_min AND lon_max
# 3. For date queries use: timestamp >= 'YYYY-MM-DD' AND timestamp <= 'YYYY-MM-DD'
# 4. For "recent" queries, use: timestamp >= CURRENT_DATE - INTERVAL 'N months'
# 5. ALWAYS include LIMIT clause (default 1000, max 10000)
# 6. Use meaningful column aliases
# 7. For aggregations, always GROUP BY properly
# 8. For depth queries, use pressure or depth_m column
# 9. Quality filtering: WHERE temp_qc IN (1,2) AND sal_qc IN (1,2)
# 10. Return ONLY the SQL query, no explanations

# Common Query Patterns:

# Geographic Search:
# SELECT * FROM argo_profiles 
# WHERE latitude BETWEEN 10 AND 20 
#   AND longitude BETWEEN 60 AND 80
# LIMIT 1000;

# Temporal Search:
# SELECT * FROM argo_profiles 
# WHERE timestamp >= '2023-01-01' 
#   AND timestamp <= '2023-12-31'
# LIMIT 1000;

# Statistics:
# SELECT 
#     AVG(temperature) as avg_temp,
#     AVG(salinity) as avg_sal,
#     COUNT(*) as measurements
# FROM argo_profiles 
# WHERE ocean_region = 'Arabian Sea'
#   AND year = 2023;

# Profile Search:
# SELECT * FROM argo_profiles
# WHERE float_id = '2902696'
#   AND cycle_number = 100
# ORDER BY pressure;

# Region Keywords:
# - Arabian Sea: lat 5-30, lon 40-80
# - Bay of Bengal: lat 5-25, lon 80-100
# - Equatorial Indian Ocean: lat -10 to 5, lon 40-100
# - Southern Indian Ocean: lat -50 to -10, lon 20-120

# Generate the SQL query:"""
    
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model=os.getenv('GOOGLE_MODEL', 'gemini-2.5-flash'),
#             temperature=0.0,  # Zero for deterministic SQL
#             google_api_key=os.getenv('GOOGLE_API_KEY')
#         )
        
#         self.prompt_template = PromptTemplate(
#             input_variables=["user_query", "context", "schema"],
#             template=self.SQL_PROMPT_TEMPLATE
#         )
        
#         # Query patterns for fallback
#         self.query_patterns = self._initialize_patterns()
    
#     def _initialize_patterns(self) -> Dict:
#         """Predefined query patterns for common requests"""
#         return {
#             'all_data': "SELECT * FROM argo_profiles ORDER BY timestamp DESC LIMIT 1000;",
#             'recent_data': "SELECT * FROM argo_profiles WHERE timestamp >= CURRENT_DATE - INTERVAL '1 month' ORDER BY timestamp DESC LIMIT 1000;",
#             'count': "SELECT COUNT(*) as total_measurements, COUNT(DISTINCT float_id) as unique_floats FROM argo_profiles;",
#             'regions': "SELECT ocean_region, COUNT(*) as count FROM argo_profiles GROUP BY ocean_region ORDER BY count DESC;",
#         }
    
#     def generate_sql(self, user_query: str, context: str = "") -> Optional[str]:
#         """
#         Generate SQL with intelligent understanding
        
#         Args:
#             user_query: Natural language question
#             context: Retrieved context from vector store
        
#         Returns:
#             Valid SQL query or None
#         """
#         # Check for simple patterns first
#         simple_sql = self._check_simple_patterns(user_query)
#         if simple_sql:
#             print(f"📌 Using pattern match")
#             return simple_sql
        
#         try:
#             # Generate SQL using LLM
#             formatted_prompt = self.prompt_template.format(
#                 user_query=user_query,
#                 context=context,
#                 schema=self.SCHEMA
#             )
            
#             response = self.llm.invoke(formatted_prompt)
#             sql_query = self._clean_sql(response.content)
            
#             # Validate
#             if not self.validate_sql(sql_query):
#                 print("⚠️ Generated SQL failed validation")
#                 return None
            
#             # Optimize
#             sql_query = self._optimize_query(sql_query)
            
#             print(f"✅ Generated SQL: {sql_query[:100]}...")
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ SQL generation error: {e}")
#             return None
    
#     def _check_simple_patterns(self, query: str) -> Optional[str]:
#         """Check for simple query patterns"""
#         query_lower = query.lower()
        
#         # Show all/everything
#         if any(word in query_lower for word in ['show all', 'get all', 'everything']):
#             if 'recent' in query_lower:
#                 return self.query_patterns['recent_data']
#             return self.query_patterns['all_data']
        
#         # Count queries
#         if 'how many' in query_lower or 'count' in query_lower:
#             return self.query_patterns['count']
        
#         # Region queries
#         if 'region' in query_lower:
#             return self.query_patterns['regions']
        
#         return None
    
#     def _clean_sql(self, sql: str) -> str:
#         """Clean SQL query from LLM response"""
#         # Remove markdown
#         sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
#         sql = re.sub(r'```\s*', '', sql)
        
#         # Remove comments
#         sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
#         sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
#         # Clean whitespace
#         sql = ' '.join(sql.split())
#         sql = sql.strip()
        
#         # Ensure semicolon
#         if not sql.endswith(';'):
#             sql += ';'
        
#         return sql
    
#     def _optimize_query(self, sql: str) -> str:
#         """Optimize SQL query"""
#         # Add LIMIT if missing
#         if 'LIMIT' not in sql.upper() and 'COUNT' not in sql.upper():
#             sql = sql.rstrip(';') + ' LIMIT 1000;'
        
#         # Check LIMIT size
#         limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
#         if limit_match:
#             limit_val = int(limit_match.group(1))
#             if limit_val > 10000:
#                 sql = re.sub(r'LIMIT\s+\d+', 'LIMIT 10000', sql, flags=re.IGNORECASE)
#                 print("⚠️ Limited query to 10000 rows")
        
#         return sql
    
#     def validate_sql(self, sql: str) -> bool:
#         """
#         Comprehensive SQL validation
        
#         Security checks:
#         - No dangerous operations
#         - Proper syntax
#         - Valid table names
#         """
#         if not sql or len(sql) < 10:
#             return False
        
#         sql_upper = sql.upper()
        
#         # Check dangerous operations
#         dangerous = [
#             'DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 
#             'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC',
#             'EXECUTE', 'UNION', 'INFORMATION_SCHEMA'
#         ]
        
#         for keyword in dangerous:
#             if keyword in sql_upper:
#                 print(f"⚠️ Dangerous keyword: {keyword}")
#                 return False
        
#         # Must be SELECT
#         if not sql_upper.strip().startswith('SELECT'):
#             print("⚠️ Query must start with SELECT")
#             return False
        
#         # Check table name
#         if 'argo_profiles' not in sql_upper:
#             print("⚠️ Invalid table name")
#             return False
        
#         # Check for multiple statements
#         if sql.count(';') > 1:
#             print("⚠️ Multiple statements not allowed")
#             return False
        
#         return True
    
#     def explain_query(self, sql: str) -> str:
#         """Generate human-readable explanation of SQL query"""
#         try:
#             explain_prompt = f"""Explain this SQL query in simple terms for oceanographers:

# {sql}

# Provide a brief 2-3 sentence explanation of what data this query returns."""

#             response = self.llm.invoke(explain_prompt)
#             return response.content
#         except:
#             return "Query explanation unavailable"
    
#     def suggest_improvements(self, user_query: str, sql: str) -> List[str]:
#         """Suggest query improvements"""
#         suggestions = []
        
#         sql_upper = sql.upper()
        
#         # Check for QC filtering
#         if 'temp_qc' not in sql_upper and 'sal_qc' not in sql_upper:
#             suggestions.append("Consider adding quality control filters: WHERE temp_qc IN (1,2)")
        
#         # Check for ORDER BY
#         if 'ORDER BY' not in sql_upper and 'GROUP BY' not in sql_upper:
#             suggestions.append("Add ORDER BY clause for consistent results")
        
#         # Check for geographic constraints
#         if any(word in user_query.lower() for word in ['near', 'around', 'location']) and 'latitude' not in sql_upper:
#             suggestions.append("Add geographic constraints for location-based queries")
        
#         return suggestions
    
#     def get_query_statistics(self, sql: str) -> Dict:
#         """Analyze query characteristics"""
#         stats = {
#             'type': 'unknown',
#             'has_aggregation': False,
#             'has_grouping': False,
#             'has_ordering': False,
#             'has_limit': False,
#             'estimated_complexity': 'low'
#         }
        
#         sql_upper = sql.upper()
        
#         # Query type
#         if 'COUNT' in sql_upper or 'AVG' in sql_upper or 'SUM' in sql_upper:
#             stats['type'] = 'aggregation'
#             stats['has_aggregation'] = True
#         elif 'JOIN' in sql_upper:
#             stats['type'] = 'join'
#         else:
#             stats['type'] = 'select'
        
#         # Check components
#         stats['has_grouping'] = 'GROUP BY' in sql_upper
#         stats['has_ordering'] = 'ORDER BY' in sql_upper
#         stats['has_limit'] = 'LIMIT' in sql_upper
        
#         # Estimate complexity
#         complexity_score = 0
#         complexity_score += 1 if stats['has_aggregation'] else 0
#         complexity_score += 1 if stats['has_grouping'] else 0
#         complexity_score += 1 if 'WHERE' in sql_upper else 0
#         complexity_score += 2 if 'JOIN' in sql_upper else 0
        
#         if complexity_score <= 1:
#             stats['estimated_complexity'] = 'low'
#         elif complexity_score <= 3:
#             stats['estimated_complexity'] = 'medium'
#         else:
#             stats['estimated_complexity'] = 'high'
        
#         return stats


# # Usage Example
# if __name__ == "__main__":
#     generator = AdvancedSQLGenerator()
    
#     test_queries = [
#         "Show me temperature profiles in Arabian Sea",
#         "What's the average salinity in March 2023?",
#         "Find floats between 10-20°N and 60-80°E",
#         "Show recent data from the last month"
#     ]
    
#     for query in test_queries:
#         print(f"\n{'='*60}")
#         print(f"Query: {query}")
#         sql = generator.generate_sql(query)
        
#         if sql:
#             print(f"SQL: {sql}")
#             print(f"Explanation: {generator.explain_query(sql)}")
#             print(f"Stats: {generator.get_query_statistics(sql)}")
#             suggestions = generator.suggest_improvements(query, sql)
#             if suggestions:
#                 print(f"Suggestions: {suggestions}")
#         else:
#             print("Failed to generate SQL")