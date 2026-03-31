import os
import json
from openai import OpenAI

class PipelineAnalyzer:
    def analyze(self, log_content: str, job_config: str = "") -> dict:
        api_key = os.environ.get("GROQ_API_KEY")
        
        if not log_content:
            return {
                'failure_type': 'Unknown Error',
                'root_cause_title': 'Empty Log Output',
                'explanation': 'No console logs were captured from Jenkins. The pipeline may have failed extremely early.',
                'snippet': ''
            }
            
        if not api_key or api_key == "your_groq_api_key_here":
            return {
                'failure_type': 'API Key Missing',
                'root_cause_title': 'Groq Backend Offline',
                'explanation': 'Please paste your valid Groq API Key into docker-compose.yml to authorize analysis via Llama 3.',
                'snippet': '\n'.join(log_content.splitlines()[-10:])
            }

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        

        truncated_log = log_content[-6000:]
        truncated_config = job_config[:3000] if job_config else "N/A"
        
        prompt = f"""
You are an expert DevOps AI analyzer. I will provide you with the raw Jenkins console stack trace AND the XML Jenkins Job Configuration (script/shell steps).
Your explicit job is to cross-reference the console trace against the configuration to identify the EXACT root cause (e.g. typos like 'gut' instead of 'git', incorrect shell commands, missing libraries, or exceptions).

You MUST respond strictly in valid JSON format mapping precisely these exactly four key parameters:
1. "failure_type": A short generic category (e.g., "Misconfigured Command", "Compilation Error", "Environment Issue", "Execution Crash")
2. "root_cause_title": A 3 to 6 word explicit title of the error (e.g. "Invalid Git Command Typo", "Missing Shell Script Target").
3. "explanation": A highly detailed, human-readable sentence explaining exactly why the build crashed natively in English. If you notice a typo in the job_config, specifically point it out!
4. "snippet": The exact isolated 2-5 line block from the console log or config that proves this targeted error exists.

Jenkins Job Configuration XML (Build Steps):
{truncated_config}

Jenkins Console Output Trace:
{truncated_log}
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": "You are a Jenkins error analyzer backend service. You natively strictly output valid JSON parameters matching exactly four keys."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            payload = json.loads(response.choices[0].message.content)
            
            return {
                'failure_type': payload.get('failure_type', 'Dynamic Analysis Extraction'),
                'root_cause_title': payload.get('root_cause_title', 'Categorization Failed'),
                'explanation': payload.get('explanation', 'Groq Llama3 parsed the error but failed stringifying the explanation.'),
                'snippet': payload.get('snippet', '\n'.join(log_content.splitlines()[-10:]))
            }
            
        except Exception as e:

            lines = log_content.splitlines()
            error_keywords = ['exception', 'error:', 'error=', 'failed:', 'fatal:', 'traceback', 'compilation errors']
            for i in range(len(lines)-1, -1, -1):
                line_lower = lines[i].lower()
                if any(keyword in line_lower for keyword in error_keywords):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 6)
                    snippet = '\n'.join(lines[start:end])
                    
                    clean_line = lines[i].strip()
                    if len(clean_line) > 200:
                        clean_line = clean_line[:200] + "..."
                        
                    return {
                        'failure_type': 'Dynamic Analysis Extraction',
                        'root_cause_title': 'Uncategorized Script Crash',
                        'explanation': f'Fallback trace explicitly extracted natively (Groq Inference Interrupted): "{clean_line}"',
                        'snippet': snippet.strip()
                    }


            return {
                'failure_type': 'Extracted Context',
                'root_cause_title': 'Abrupt Stream Termination',
                'explanation': 'The pipeline failed abruptly. The system dynamically extracted the final chunk natively.',
                'snippet': '\n'.join(lines[-15:]).strip()
            }

analyzer = PipelineAnalyzer()
