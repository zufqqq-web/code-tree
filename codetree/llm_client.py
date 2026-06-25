import sys
import json
import urllib.request
import urllib.error
import re
import os

BATCH_PROMPT_TEMPLATE = """Below are skeletons of {count} related source files from the same project folder.
For EACH file, write ONE short sentence (max 15 words) describing its purpose.
Respond ONLY with valid JSON in this exact format, no other text:
{{"filename1.ext": "description", "filename2.ext": "description"}}

Files:
{file_skeletons}
"""

class LLMClient:
    def __init__(self, api_url="http://localhost:1234/v1", api_key="lm-studio", model="local-model"):
        # Normalize endpoint URL
        if api_url.endswith('/'):
            api_url = api_url[:-1]
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def _post(self, path, data):
        url = f"{self.api_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        req_body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"API Error connecting to {url}: {e}", file=sys.stderr)
            raise e

    def get_file_summary(self, filename, language, skeleton):
        """
        Requests summary for a single file.
        """
        prompt = f"Вот сигнатуры и докстринги файла {language} ({filename}):\n\n{skeleton}\n\nОпиши в 2-3 предложениях назначение файла и его ключевые функции. Ответь ТОЛЬКО на русском языке, без перевода на другие языки."
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a senior software architect summarizing project code."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        try:
            res_str = self._post("/chat/completions", payload)
            res_data = json.loads(res_str)
            return res_data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Failed to get summary for {filename}: {e}", file=sys.stderr)
            return None

    def get_batch_summaries(self, files_list):
        """
        Requests summaries for a batch of files.
        files_list is a list of tuples: (rel_path, language, skeleton)
        Returns a dictionary: { rel_path: description }
        """
        # Format the skeletons for the prompt
        skeletons_formatted = []
        for rel_path, lang, skeleton in files_list:
            filename = os.path.basename(rel_path)
            skeletons_formatted.append(f"--- File: {filename} (Language: {lang}) ---\n{skeleton}\n")
            
        file_skeletons = "\n".join(skeletons_formatted)
        prompt = BATCH_PROMPT_TEMPLATE.format(count=len(files_list), file_skeletons=file_skeletons)
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a code analyzer. Respond ONLY with valid JSON. Do not write anything outside the JSON object."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        
        try:
            res_str = self._post("/chat/completions", payload)
            res_data = json.loads(res_str)
            response_content = res_data['choices'][0]['message']['content'].strip()
            
            # Parse batch response
            return self._parse_batch_json(response_content, files_list)
        except Exception as e:
            print(f"Batch request failed: {e}", file=sys.stderr)
            return None

    def _parse_batch_json(self, raw_content, files_list):
        """
        Parses raw LLM output using the approved fallback chain.
        """
        # Try direct JSON parsing
        try:
            parsed = json.loads(raw_content)
            return self._match_batch_results(parsed, files_list)
        except Exception as e1:
            print(f"Direct JSON parsing failed for batch: {e1}\nRaw content: {raw_content}", file=sys.stderr)
            
            # Fallback 1: Extract JSON using regex
            try:
                match = re.search(r'(\{.*\})', raw_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    parsed = json.loads(json_str)
                    return self._match_batch_results(parsed, files_list)
            except Exception as e2:
                print(f"Regex JSON extraction failed: {e2}", file=sys.stderr)
                
        # If everything fails, returns None to trigger individual file querying fallback
        return None

    def _match_batch_results(self, parsed_json, files_list):
        """
        Matches filenames in parsed JSON keys to their rel_path,
        supporting case-insensitive and partial matching.
        """
        results = {}
        for rel_path, _, _ in files_list:
            filename = os.path.basename(rel_path)
            
            # Find the best match key in parsed_json
            matched_val = None
            for key, val in parsed_json.items():
                if key.lower() == filename.lower() or os.path.basename(key).lower() == filename.lower():
                    matched_val = val
                    break
            
            if matched_val:
                results[rel_path] = str(matched_val).strip()
            else:
                # Key not found in JSON
                print(f"Warning: Filename '{filename}' not found in JSON response keys.", file=sys.stderr)
                
        return results
