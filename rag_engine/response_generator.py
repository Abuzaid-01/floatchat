import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI  # ← CHANGED
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from rag_engine.prompt_templates import RESPONSE_GENERATION_PROMPT
import pandas as pd

class ResponseGenerator:
    """
    Generate natural language responses using Gemini.
    FREE Google Gemini API!
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            temperature=0.7,  # Higher for natural responses
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print(f"✅ Response Generator using: {os.getenv('GEMINI_MODEL')}")
        
        self.prompt_template = PromptTemplate(
            input_variables=["question", "context", "query_results"],
            template=RESPONSE_GENERATION_PROMPT
        )
    
    def generate_response(
        self,
        question: str,
        query_results: pd.DataFrame,
        context: str = ""
    ) -> str:
        """
        Generate natural language response from query results.
        
        Args:
            question: User's original question
            query_results: DataFrame with query results
            context: Retrieved context from vector store
            
        Returns:
            Natural language response
        """
        try:
            # Format query results
            results_summary = self._format_results(query_results)
            
            # Generate response using Gemini
            formatted_prompt = self.prompt_template.format(
                question=question,
                context=context,
                query_results=results_summary
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I encountered an error while generating the response."
    
    def _format_results(self, df: pd.DataFrame, max_rows: int = 10) -> str:
        """Format DataFrame results for Gemini"""
        if df.empty:
            return "No data found matching the query."
        
        summary_parts = [
            f"Total records: {len(df)}",
            f"Columns: {', '.join(df.columns)}",
            "\nSummary Statistics:"
        ]
        
        # Add numeric statistics
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            summary_parts.append(
                f"- {col}: min={df[col].min():.2f}, "
                f"max={df[col].max():.2f}, "
                f"mean={df[col].mean():.2f}"
            )
        
        # Add sample data
        summary_parts.append(f"\nSample Data (first {min(max_rows, len(df))} rows):")
        summary_parts.append(df.head(max_rows).to_string())
        
        return "\n".join(summary_parts)
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate quick summary without LLM call"""
        if df.empty:
            return "No results found."
        
        summary = f"Found {len(df)} records"
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            lat_range = (df['latitude'].min(), df['latitude'].max())
            lon_range = (df['longitude'].min(), df['longitude'].max())
            summary += f" spanning {lat_range[0]:.2f}°N to {lat_range[1]:.2f}°N, "
            summary += f"{lon_range[0]:.2f}°E to {lon_range[1]:.2f}°E"
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            time_range = (df['timestamp'].min(), df['timestamp'].max())
            summary += f" from {time_range[0].strftime('%Y-%m-%d')} to {time_range[1].strftime('%Y-%m-%d')}"
        
        return summary







# import os
# from typing import Dict, List
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from rag_engine.prompt_templates import RESPONSE_GENERATION_PROMPT
# import pandas as pd
# import json


# class EnhancedResponseGenerator:
#     """Production-grade response generator with context awareness"""
    
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
#             temperature=0.7,
#             google_api_key=os.getenv('GOOGLE_API_KEY')
#         )
        
#         self.prompt_template = PromptTemplate(
#             input_variables=["question", "context", "query_results", "statistics"],
#             template="""You are FloatChat, an expert oceanographic data analyst.

# User Question: {question}

# Retrieved Context:
# {context}

# Query Results Summary:
# {statistics}

# Sample Data:
# {query_results}

# Provide a comprehensive, professional response that includes:
# 1. Direct answer to the question
# 2. Key findings from the data
# 3. Statistical insights
# 4. Oceanographic interpretation
# 5. Relevant recommendations or follow-up suggestions

# Use precise scientific language but keep it accessible. Always cite specific numbers from the data.

# Response:"""
#         )
    
#     def generate_response(
#         self,
#         question: str,
#         query_results: pd.DataFrame,
#         context: str = "",
#         include_interpretation: bool = True
#     ) -> Dict:
#         """
#         Generate comprehensive response with statistics
        
#         Returns:
#             Dict with 'response', 'statistics', 'recommendations'
#         """
#         try:
#             # Calculate statistics
#             stats = self._calculate_statistics(query_results)
            
#             # Format results for LLM
#             results_summary = self._format_results_for_llm(query_results)
            
#             # Generate response
#             formatted_prompt = self.prompt_template.format(
#                 question=question,
#                 context=context,
#                 query_results=results_summary,
#                 statistics=json.dumps(stats, indent=2)
#             )
            
#             response = self.llm.invoke(formatted_prompt)
            
#             # Generate recommendations
#             recommendations = self._generate_recommendations(question, query_results)
            
#             return {
#                 'response': response.content,
#                 'statistics': stats,
#                 'recommendations': recommendations,
#                 'data_quality': self._assess_data_quality(query_results)
#             }
            
#         except Exception as e:
#             print(f"❌ Response generation error: {e}")
#             return {
#                 'response': "I encountered an error generating a detailed response.",
#                 'statistics': {},
#                 'recommendations': [],
#                 'data_quality': 'unknown'
#             }
    
#     def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
#         """Calculate comprehensive statistics"""
#         stats = {
#             'total_records': len(df),
#             'date_range': {},
#             'geographic_extent': {},
#             'parameters': {}
#         }
        
#         # Temporal
#         if 'timestamp' in df.columns:
#             df['timestamp'] = pd.to_datetime(df['timestamp'])
#             stats['date_range'] = {
#                 'start': df['timestamp'].min().strftime('%Y-%m-%d'),
#                 'end': df['timestamp'].max().strftime('%Y-%m-%d'),
#                 'duration_days': (df['timestamp'].max() - df['timestamp'].min()).days
#             }
        
#         # Geographic
#         if 'latitude' in df.columns and 'longitude' in df.columns:
#             stats['geographic_extent'] = {
#                 'lat_range': [float(df['latitude'].min()), float(df['latitude'].max())],
#                 'lon_range': [float(df['longitude'].min()), float(df['longitude'].max())],
#                 'center': [float(df['latitude'].mean()), float(df['longitude'].mean())]
#             }
        
#         # Parameters
#         param_cols = ['temperature', 'salinity', 'pressure', 'dissolved_oxygen', 'chlorophyll', 'ph']
#         for col in param_cols:
#             if col in df.columns:
#                 stats['parameters'][col] = {
#                     'min': float(df[col].min()),
#                     'max': float(df[col].max()),
#                     'mean': float(df[col].mean()),
#                     'median': float(df[col].median()),
#                     'std': float(df[col].std())
#                 }
        
#         return stats
    
#     def _format_results_for_llm(self, df: pd.DataFrame, max_rows: int = 5) -> str:
#         """Format DataFrame for LLM context"""
#         if df.empty:
#             return "No data available"
        
#         # Select important columns
#         important_cols = ['latitude', 'longitude', 'timestamp', 'temperature', 'salinity', 'pressure']
#         available_cols = [col for col in important_cols if col in df.columns]
        
#         sample_df = df[available_cols].head(max_rows)
#         return sample_df.to_string()
    
#     def _generate_recommendations(self, question: str, df: pd.DataFrame) -> List[str]:
#         """Generate follow-up recommendations"""
#         recommendations = []
        
#         # Based on data characteristics
#         if 'ocean_region' in df.columns and df['ocean_region'].nunique() > 1:
#             recommendations.append("Compare results across different ocean regions")
        
#         if 'timestamp' in df.columns:
#             recommendations.append("Analyze temporal trends with time-series visualization")
        
#         if len(df) > 1000:
#             recommendations.append("Consider filtering by date range or region for detailed analysis")
        
#         if 'float_id' in df.columns and df['float_id'].nunique() > 1:
#             recommendations.append("Examine individual float trajectories")
        
#         return recommendations[:3]  # Top 3
    
#     def _assess_data_quality(self, df: pd.DataFrame) -> str:
#         """Assess data quality"""
#         if df.empty:
#             return 'no_data'
        
#         # Check QC flags if available
#         if 'temp_qc' in df.columns:
#             good_quality = (df['temp_qc'].isin([1, 2])).sum() / len(df)
#             if good_quality > 0.95:
#                 return 'excellent'
#             elif good_quality > 0.80:
#                 return 'good'
#             else:
#                 return 'moderate'
        
#         return 'unvalidated'