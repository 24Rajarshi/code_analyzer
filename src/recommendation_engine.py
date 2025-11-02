import os
import sys
import json
import time
from typing import List, Dict

def recommend_files(user_query: str, code_summaries: List[Dict]) -> str:
    recommendations = []
    for summary in code_summaries:
        file_name = summary.get('file_name') or summary.get('file')
        file_summary = ' '.join(summary.get('summary', [])).lower() if isinstance(summary.get('summary'), list) else summary.get('summary', '').lower()
        parameters = summary.get('parameters', [])
        # Simple keyword matching for demonstration
        if any(keyword in file_summary for keyword in user_query.lower().split()):
            recommendations.append(
                f"- {file_name}: {file_summary.strip()} (Relevant to query)"
            )
        elif any(keyword in param.lower() for param in parameters for keyword in user_query.lower().split()):
            recommendations.append(
                f"- {file_name}: Parameters match query context"
            )
    output = f"USER QUERY: {user_query}\n\nRECOMMENDATIONS:\n"
    if recommendations:
        output += "\n".join(recommendations)
        output += "\n\nGENERAL SUGGESTION:\nReview the above files/functions for your task. If unsure, start with files whose summaries or parameters closely match your query keywords."
    else:
        output += "No direct match found.\n\nGENERAL SUGGESTION:\nConsider searching for keywords from your query in the codebase, or review files with broad functionality related to your task."
    return output

if __name__ == "__main__":
    print("Executing recommendation_engine.py")
    analysis_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # Accept parameters as strings from environment variables
    temp_workspace = os.environ.get("GNAI_TEMP_WORKSPACE", ".")
    user_query = os.environ.get("GNAI_INPUT_USER_QUERY")
    code_summaries_path = os.environ.get("GNAI_INPUT_CODE_SUMMARIES_PATH")

    if not user_query or not code_summaries_path:
        print(json.dumps({"output": {"error": "Required environment variables not set: GNAI_INPUT_USER_QUERY and/or GNAI_INPUT_CODE_SUMMARIES_PATH."}}, indent=2))
        sys.exit(1)

    code_summaries_full_path = os.path.join(temp_workspace, code_summaries_path)
    if not os.path.exists(code_summaries_full_path):
        print(json.dumps({"output": {"error": f"Code summaries file not found: {code_summaries_full_path}"}}, indent=2))
        sys.exit(1)

    print(f"Reading code summaries from: {code_summaries_full_path}")
    with open(code_summaries_full_path, "r") as f:
        code_summaries = json.load(f)

    # If the file is a dict with a "files" key, convert to list of dicts
    if isinstance(code_summaries, dict) and "files" in code_summaries:
        code_summaries = [
            {"file": k, "summary": v.get("summary", []), "parameters": v.get("parameters", [])}
            for k, v in code_summaries["files"].items()
        ]

    print("Running recommendation analysis...")
    result = recommend_files(user_query, code_summaries)
    print("Recommendation Result:")
    print(result)

    analysis_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"Analysis time: from {analysis_start_time} to {analysis_end_time}")
    print("Thank you for using the recommendation engine tool.")
