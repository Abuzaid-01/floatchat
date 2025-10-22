# import os
# from typing import Dict, Optional
# from langchain_google_genai import ChatGoogleGenerativeAI  # ← CHANGED
# from langchain_core.prompts import PromptTemplate  # ← CHANGED: Use langchain_core

# from rag_engine.prompt_templates import SQL_GENERATION_PROMPT
# from dotenv import load_dotenv

# load_dotenv()

# class SQLGenerator:
#     """
#     Convert natural language queries to SQL using Gemini LLM.
#     Now using FREE Google Gemini API!
#     """
    
#     def __init__(self):
#         # Initialize Gemini LLM (FREE!)
#         self.llm = ChatGoogleGenerativeAI(
#             model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
#             temperature=0.1,
#             google_api_key=os.getenv('GOOGLE_API_KEY')
#         )
        
#         print(f"✅ Initialized Gemini: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
        
#         # Create prompt template
#         self.prompt_template = PromptTemplate(
#             input_variables=["user_query", "context"],
#             template=SQL_GENERATION_PROMPT
#         )
    
#     def generate_sql(self, user_query: str, context: str = "") -> str:
#         """
#         Generate SQL query from natural language using Gemini.
        
#         Args:
#             user_query: User's natural language question
#             context: Retrieved context from vector store
            
#         Returns:
#             SQL query string
#         """
#         try:
#             # Format prompt with user query and context
#             formatted_prompt = self.prompt_template.format(
#                 user_query=user_query,
#                 context=context
#             )
            
#             # Get Gemini response
#             response = self.llm.invoke(formatted_prompt)
#             sql_query = response.content.strip()
            
#             # Clean SQL query
#             sql_query = self._clean_sql(sql_query)
            
#             print(f"📝 Generated SQL: {sql_query}")
#             return sql_query
            
#         except Exception as e:
#             print(f"❌ Error generating SQL: {e}")
#             return None
    
#     def _clean_sql(self, sql: str) -> str:
#         """Remove markdown code blocks and extra whitespace"""
#         # Remove markdown code blocks like ```sql or ```
#         import re
#         sql = re.sub(r'```(?:sql)?\s*', '', sql)
#         sql = re.sub(r'```\s*$', '', sql)
#         # Remove extra whitespace
#         sql = ' '.join(sql.split())
#         return sql.strip()
    
#     def validate_sql(self, sql: str) -> bool:
#         """Basic SQL validation to prevent SQL injection"""
#         dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 'ALTER']
#         sql_upper = sql.upper()
        
#         for keyword in dangerous_keywords:
#             if keyword in sql_upper:
#                 print(f"⚠️ Dangerous SQL keyword detected: {keyword}")
#                 return False
        
#         return True







import os
import re
from typing import Dict, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class AdvancedSQLGenerator:
    """
    Advanced SQL generator with schema-aware query generation
    """
    
    DATABASE_SCHEMA = """
    Table: argo_profiles
    
    Core Columns:
    - id (INTEGER, Primary Key)
    - float_id (VARCHAR) - Unique float identifier
    - cycle_number (INTEGER) - Measurement cycle (1, 2, 3...)
    - latitude (FLOAT) - Latitude (-90 to 90)
    - longitude (FLOAT) - Longitude (-180 to 180)
    - timestamp (TIMESTAMP) - Measurement datetime
    - pressure (FLOAT) - Water pressure in dbar
    - temperature (FLOAT) - Temperature in Celsius
    - salinity (FLOAT) - Salinity in PSU (Practical Salinity Units)
    
    BGC Parameters:
    - dissolved_oxygen (FLOAT) - DO in μmol/kg
    - chlorophyll (FLOAT) - Chlorophyll-a in mg/m³
    - ph (FLOAT) - pH value (seawater pH scale)
    - nitrate (FLOAT) - Nitrate concentration in μmol/L
    - bbp700 (FLOAT) - Backscatter at 700nm
    
    Metadata:
    - data_mode (VARCHAR) - R/D/A (Realtime/Delayed/Adjusted)
    - platform_type (VARCHAR) - ARGO or BGC
    - temp_qc (INTEGER) - Temperature QC flag (1=good, 2=probably good, 3=questionable, 4=bad)
    - sal_qc (INTEGER) - Salinity QC flag (same scale)
    
    Indexes:
    - idx_lat_lon (latitude, longitude) - Geographic queries
    - idx_timestamp (timestamp) - Time-based queries
    - idx_float_id (float_id) - Float identification
    - idx_spatial_temporal (latitude, longitude, timestamp) - Combined
    
    Ocean Regions (Auto-detected):
    - Arabian Sea: lat 5-30°N, lon 40-80°E
    - Bay of Bengal: lat 5-25°N, lon 80-100°E
    - Equatorial Indian Ocean: lat -10 to 5°N, lon 40-100°E
    - Southern Indian Ocean: lat -50 to -10°N, lon 20-120°E
    - Red Sea: lat 12-30°N, lon 32-44°E
    
    Best Practices:
    1. Always use LIMIT (max 10000)
    2. Quality filter: WHERE temp_qc IN (1,2) AND sal_qc IN (1,2)
    3. For depth: use pressure column (1 dbar ≈ 1 meter)
    4. Date format: 'YYYY-MM-DD'
    5. Avoid N+1 queries - use aggregations
    6. Use proper indexes for performance
    """
    
    SQL_GENERATION_PROMPT = """You are an expert PostgreSQL query generator for oceanographic ARGO float data.

Database Schema:
{schema}

User Query: {user_query}

Context from similar profiles:
{context}

CRITICAL SQL RULES:
1. ALWAYS use PostgreSQL syntax (NOT MySQL)
2. ALWAYS include LIMIT (default 1000, max 10000)
3. Proper NULL handling: col IS NOT NULL
4. Date format: 'YYYY-MM-DD'
5. Case-insensitive searches: ILIKE instead of LIKE
6. Quality control filtering: WHERE temp_qc IN (1,2) for good data
7. Geographic queries: lat BETWEEN X AND Y, lon BETWEEN X AND Y
8. Aggregations: Always GROUP BY related columns
9. Aliases: Use meaningful aliases
10. Comments: Add -- comments for complex logic

Common Query Patterns:

Geographic Search:
SELECT * FROM argo_profiles 
WHERE latitude BETWEEN 10 AND 20 
  AND longitude BETWEEN 60 AND 80
  AND temp_qc IN (1,2)
ORDER BY timestamp DESC
LIMIT 1000;

Recent Data (Last N Days):
SELECT * FROM argo_profiles 
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
  AND temp_qc IN (1,2)
ORDER BY timestamp DESC
LIMIT 1000;

Regional Statistics:
SELECT 
    AVG(temperature) as avg_temp,
    MIN(temperature) as min_temp,
    MAX(temperature) as max_temp,
    AVG(salinity) as avg_salinity,
    COUNT(*) as measurements
FROM argo_profiles
WHERE ocean_region = 'Arabian Sea'
  AND timestamp >= CURRENT_DATE - INTERVAL '1 month'
  AND temp_qc IN (1,2);

Profile Analysis:
SELECT * FROM argo_profiles
WHERE float_id = '2902696'
  AND cycle_number = 100
ORDER BY pressure ASC;

BGC Analysis:
SELECT latitude, longitude, timestamp, 
       dissolved_oxygen, chlorophyll, ph
FROM argo_profiles
WHERE dissolved_oxygen IS NOT NULL
  AND chlorophyll IS NOT NULL
  AND ocean_region = 'Arabian Sea'
LIMIT 1000;

Temporal Trend:
SELECT DATE_TRUNC('day', timestamp) as date,
       AVG(temperature) as avg_temp,
       COUNT(*) as measurements
FROM argo_profiles
WHERE ocean_region = 'Bay of Bengal'
  AND temp_qc IN (1,2)
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY date DESC
LIMIT 30;

Regional Comparison:
SELECT ocean_region,
       AVG(temperature) as avg_temp,
       AVG(salinity) as avg_sal,
       COUNT(*) as measurements
FROM argo_profiles
WHERE temp_qc IN (1,2)
  AND timestamp >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY ocean_region
ORDER BY measurements DESC;

Float Trajectory:
SELECT latitude, longitude, timestamp, 
       temperature, salinity, cycle_number
FROM argo_profiles
WHERE float_id = '2902696'
ORDER BY timestamp ASC
LIMIT 5000;

IMPORTANT: 
- Return ONLY the SQL query
- Use proper formatting and indentation
- Include helpful comments for complex queries
- Validate all column names against schema
- Ensure WHERE clauses are complete

Generate the optimized PostgreSQL query:"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv('GOOGLE_MODEL', 'gemini-2.5-flash'),
            temperature=0.0,  # Deterministic for SQL
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["user_query", "context", "schema"],
            template=self.SQL_GENERATION_PROMPT
        )
        
        self.common_patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict:
        """Initialize common query patterns"""
        return {
            'all_data': "SELECT * FROM argo_profiles ORDER BY timestamp DESC LIMIT 1000;",
            'recent_month': "SELECT * FROM argo_profiles WHERE timestamp >= CURRENT_DATE - INTERVAL '1 month' ORDER BY timestamp DESC LIMIT 1000;",
            'region_stats': "SELECT ocean_region, COUNT(*) as count, AVG(temperature) as avg_temp FROM argo_profiles GROUP BY ocean_region ORDER BY count DESC;",
            'float_profile': "SELECT * FROM argo_profiles WHERE float_id = {float_id} ORDER BY timestamp DESC LIMIT 1000;",
            'depth_analysis': "SELECT pressure, AVG(temperature) as avg_temp, AVG(salinity) as avg_sal FROM argo_profiles WHERE temp_qc IN (1,2) GROUP BY pressure ORDER BY pressure;",
        }
    
    def generate_sql(self, user_query: str, context: str = "") -> Optional[str]:
        """
        Generate SQL query with schema awareness
        """
        try:
            # Check for quick patterns
            quick_sql = self._check_quick_patterns(user_query)
            if quick_sql:
                return quick_sql
            
            # Generate using LLM with full schema
            formatted_prompt = self.prompt_template.format(
                user_query=user_query,
                context=context,
                schema=self.DATABASE_SCHEMA
            )
            
            response = self.llm.invoke(formatted_prompt)
            sql_query = self._clean_sql(response.content)
            
            print(f"🔍 DEBUG - Generated SQL: {sql_query}")
            
            # Validate
            if not self.validate_sql(sql_query):
                print(f"⚠️ SQL validation failed for: {sql_query}")
                return None
            
            # Optimize
            sql_query = self._optimize_query(sql_query)
            
            print(f"✅ Generated SQL: {sql_query[:80]}...")
            return sql_query
            
        except Exception as e:
            print(f"❌ SQL generation error: {e}")
            return None
    
    def _check_quick_patterns(self, query: str) -> Optional[str]:
        """Check for common quick patterns"""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ['show all', 'get all', 'everything', 'all data']):
            return self.common_patterns['all_data']
        
        if 'recent' in query_lower or 'last month' in query_lower:
            return self.common_patterns['recent_month']
        
        if 'region' in query_lower and 'stat' in query_lower:
            return self.common_patterns['region_stats']
        
        return None
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL from markdown and extra whitespace"""
        sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*', '', sql)
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = ' '.join(sql.split())
        sql = sql.strip()
        
        if not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def _optimize_query(self, sql: str) -> str:
        """Optimize SQL query"""
        # Add LIMIT if missing
        if 'LIMIT' not in sql.upper():
            sql = sql.rstrip(';') + ' LIMIT 1000;'
        
        # Ensure reasonable LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if limit_match:
            limit_val = int(limit_match.group(1))
            if limit_val > 10000:
                sql = re.sub(r'LIMIT\s+\d+', 'LIMIT 10000', sql, flags=re.IGNORECASE)
        
        return sql
    
    def validate_sql(self, sql: str) -> bool:
        """Comprehensive SQL validation"""
        if not sql or len(sql) < 10:
            print(f"❌ Validation failed: SQL too short or empty")
            return False
        
        sql_upper = sql.upper()
        
        # Check dangerous operations
        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE', 'ALTER',
                    'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE']
        
        for keyword in dangerous:
            if keyword in sql_upper:
                print(f"❌ Validation failed: Dangerous keyword '{keyword}' found")
                return False
        
        # Must be SELECT
        if not sql_upper.strip().startswith('SELECT'):
            print(f"❌ Validation failed: Query must start with SELECT, got: {sql[:50]}")
            return False
        
        # Check valid table
        if 'ARGO_PROFILES' not in sql_upper:
            print(f"❌ Validation failed: Table 'argo_profiles' not found in query")
            return False
        
        # No multiple statements
        if sql.count(';') > 1:
            print(f"❌ Validation failed: Multiple statements detected")
            return False
        
        return True
    
    def explain_query(self, sql: str) -> str:
        """Generate human-readable explanation"""
        try:
            prompt = f"""Explain this SQL query in 2-3 sentences for oceanographers:\n\n{sql}\n\nFocus on what data it retrieves and why."""
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return "Query explanation unavailable"