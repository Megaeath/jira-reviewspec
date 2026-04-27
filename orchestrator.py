import json
import google.generativeai as genai
from typing import Dict, Any


import os
from datetime import datetime


class SpecReviewOrchestrator:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.prompts = {}
        self.rubrics = {}
        self.last_response = ""
        self.page_id = "manual"
        self.session_timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        self.total_token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def set_page_id(self, page_id: str):
        self.page_id = page_id

    def _save_step_log(self, agent_name: str, prompt: str, response: str, token_info: dict = None):
        log_dir = f"review/{self.page_id}/{self.session_timestamp}/{agent_name}"
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"{log_dir}/log.md"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# Agent: {agent_name}\n")
            f.write(f"Timestamp: {self.session_timestamp}\n")
            f.write(f"Page ID: {self.page_id}\n\n")
            if token_info:
                f.write("## Token Usage\n")
                f.write(f"- Prompt Tokens: {token_info.get('prompt_tokens', 0)}\n")
                f.write(f"- Completion Tokens: {token_info.get('completion_tokens', 0)}\n")
                f.write(f"- **Total Tokens:** {token_info.get('total_tokens', 0)}\n\n")
            f.write("## Request (Prompt)\n")
            f.write(f"```text\n{prompt}\n```\n\n")
            f.write("## Response\n")
            f.write(f"```text\n{response}\n```\n")
        print(f"--- Log saved: {log_file}")

    def set_prompts(self, prompts: Dict[int, str]):
        self.prompts = prompts

    def set_rubrics(self, rubrics: Dict[str, str]):
        self.rubrics = rubrics

    def _call_llm(self, prompt: str, agent_name: str, input_data: Any = None) -> str:
        full_prompt = prompt
        if input_data:
            if isinstance(input_data, str):
                full_prompt = full_prompt.replace("{{spec_text}}", input_data)
            elif isinstance(input_data, dict):
                for k, v in input_data.items():
                    # Handle both {{key}} and {{ key }}
                    full_prompt = full_prompt.replace(f"{{{{{k}}}}}", str(v))
                    full_prompt = full_prompt.replace(f"{{{{ {k} }}}}", str(v))

        # Ensure we ask for JSON if the prompt expects it
        print(
            f"\n--- Final Prompt sent to LLM ({agent_name}) ---\n{full_prompt[:500]}...\n--- End Prompt ---\n"
        )
        response = self.model.generate_content(full_prompt)
        text = response.text.strip()
        self.last_response = text
        
        token_info = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            token_info = {
                "prompt_tokens": getattr(usage, "prompt_token_count", 0),
                "completion_tokens": getattr(usage, "candidates_token_count", 0),
                "total_tokens": getattr(usage, "total_token_count", 0),
            }
            # Track total usage
            self.total_token_usage["prompt_tokens"] += token_info["prompt_tokens"]
            self.total_token_usage["completion_tokens"] += token_info["completion_tokens"]
            self.total_token_usage["total_tokens"] += token_info["total_tokens"]

        print(f"--- Raw LLM Response ({agent_name}): {text[:500]}...")

        # Save step log
        self._save_step_log(agent_name, full_prompt, text, token_info)

        # Robust JSON extraction: Find the outermost { } or [ ]
        import re
        text = text.strip()
        # Remove markdown code blocks if present
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        
        # We want to find the largest substring that starts with { or [ and ends with } or ]
        # BUT we should be careful if there are multiple objects.
        # Usually, the LLM returns one JSON object.
        
        start_brace = text.find("{")
        start_bracket = text.find("[")
        
        # Decide where to start: if both exist, pick the one that appears first
        if start_brace != -1 and start_bracket != -1:
            start_idx = min(start_brace, start_bracket)
        else:
            start_idx = max(start_brace, start_bracket)
            
        if start_idx != -1:
            # If we started with {, we must end with }
            # If we started with [, we must end with ]
            if text[start_idx] == "{":
                end_idx = text.rfind("}")
            else:
                end_idx = text.rfind("]")
                
            if end_idx != -1 and end_idx > start_idx:
                text = text[start_idx : end_idx + 1]

        return text.strip()

    def get_token_usage(self) -> Dict[str, int]:
        return self.total_token_usage

    def _parse_json(self, json_string: str) -> Dict[str, Any]:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            # Fix invalid escapes (e.g. \d, \w, \s) generated by LLMs
            import re
            fixed_string = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', json_string)
            try:
                return json.loads(fixed_string)
            except Exception:
                # If still failing, raise the original error
                raise e

    def save_raw_spec(self, spec_text: str, metadata: dict = None):
        log_dir = f"review/{self.page_id}/{self.session_timestamp}/1-raw-spec"
        os.makedirs(log_dir, exist_ok=True)
        log_file = f"{log_dir}/log.md"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# Raw Document Content (Input)\n")
            f.write(f"Timestamp: {self.session_timestamp}\n")
            f.write(f"Page ID: {self.page_id}\n")
            if metadata:
                f.write(f"Title: {metadata.get('title', 'N/A')}\n")
                f.write(f"Version: {metadata.get('version', 'N/A')}\n")
            f.write("\n## Raw Content fetched from Confluence / Input\n")
            f.write(f"```text\n{spec_text}\n```\n")
        print(f"--- Raw spec saved: {log_file}")

    def run_review(self, spec_text: str, progress_callback=None, metadata: dict = None) -> Dict[str, Any]:
        self.save_raw_spec(spec_text, metadata)
        
        # Step 1: Classify
        if progress_callback: progress_callback(1, "กำลังวิเคราะห์ประเภทของเอกสาร (Classify)...")
        classification_raw = self._call_llm(
            self.prompts[1], "2-classify", {"spec_text": spec_text}
        )
        classification = self._parse_json(classification_raw)
        doc_type = classification.get("document_type")
        if progress_callback: progress_callback(1, "วิเคราะห์เสร็จสิ้น", classification)

        # Step 2: Rubric Review
        if progress_callback: progress_callback(2, f"กำลังตรวจสอบตามเกณฑ์ {doc_type} (Review)...")
        rubric = self.rubrics.get(doc_type, "No rubric found for this type.")
        step2_input = {
            "document_type": doc_type,
            "spec_text": spec_text,
            "rubric": rubric,
        }
        step2_raw = self._call_llm(self.prompts[2], "3-review", step2_input)
        step2_data = self._parse_json(step2_raw)
        if progress_callback: progress_callback(2, "ตรวจสอบเนื้อหาเสร็จสิ้น", {"topics": len(step2_data.get("raw_topic_reviews", []))})

        # Step 3: Scoring & Coaching
        if progress_callback: progress_callback(3, "กำลังให้คะแนนและคำแนะนำ (Scoring)...")
        step3_input = {"raw_topic_reviews": step2_data.get("raw_topic_reviews", [])}
        step3_raw = self._call_llm(self.prompts[3], "4-score", step3_input)
        step3_data = self._parse_json(step3_raw)
        if progress_callback: progress_callback(3, "ให้คะแนนเสร็จสิ้น", None)

        # Step 4: Scenario Coverage
        if progress_callback: progress_callback(4, "กำลังสร้าง Test Scenarios (Scenario)...")
        step4_input = {"spec_text": spec_text, "document_type": doc_type}
        step4_raw = self._call_llm(self.prompts[4], "5-scenario", step4_input)
        step4_data = self._parse_json(step4_raw)
        if progress_callback: progress_callback(4, "สร้าง Scenarios เสร็จสิ้น", {"scenarios": len(step4_data.get("scenarios", []))})

        # Step 5: Final Summary
        if progress_callback: progress_callback(5, "กำลังสรุปผลภาพรวม (Summary)...")
        step5_input = {
            "topic_reviews": step3_data.get("topic_reviews", []),
            "scenarios": step4_data.get("scenarios", []),
            "metadata": {
                "title": "Spec Review",
                "version": "N/A",
            },  # Simplified for POC
        }
        step5_raw = self._call_llm(self.prompts[5], "6-summary", step5_input)
        final_data = self._parse_json(step5_raw)
        if progress_callback: progress_callback(5, "เสร็จสิ้นกระบวนการทั้งหมด", None)

        return final_data
    def run_single_request_review(self, spec_text: str, optimized_prompt: str, metadata: dict = None) -> Dict[str, Any]:
        self.save_raw_spec(spec_text, metadata)
        
        # Build input data for template replacement
        input_data = {
            "title": metadata.get("title", "Spec Review") if metadata else "Spec Review",
            "version": metadata.get("version", "N/A") if metadata else "N/A",
            "url": metadata.get("url", "N/A") if metadata else "N/A",
            "spec_text": spec_text
        }
        
        # Use _call_llm for consistent logging and JSON extraction
        raw_result = self._call_llm(optimized_prompt, "single-request", input_data)
        
        # Parse and return as dictionary
        return self._parse_json(raw_result)
