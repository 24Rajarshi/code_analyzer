import argparse
import re
import os
import json
import time

CACHE_FILE = "code_summary_cache.json"

def summarize_code(file_path):
    with open(file_path, 'r') as f:
        code = f.read()

    func_pattern = re.compile(
        r'^\s*([a-zA-Z_][a-zA-Z0-9_*\s]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )

    summary = []
    parameters = set()

    for match in func_pattern.finditer(code):
        ret_type = match.group(1).strip()
        func_name = match.group(2)
        param_str = match.group(3).strip()
        param_list = [p.strip().split()[-1] for p in param_str.split(',') if p.strip() and p.strip() != 'void']
        parameters.update(param_list)
        summary.append(f"Function: {func_name}")
        summary.append(f"  Return type: {ret_type}")
        summary.append(f"  Parameters: {', '.join(param_list) if param_list else 'None'}")

    return summary, list(parameters)

def get_file_mod_times(directory):
    mod_times = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.c', '.h')):
                file_path = os.path.join(root, file)
                mod_times[file_path] = os.path.getmtime(file_path)
    return mod_times

def load_cache(cache_path):
    if not os.path.exists(cache_path):
        return None
    with open(cache_path, 'r') as f:
        return json.load(f)

def save_cache(cache_path, data):
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)

def summarize_directory(directory):
    print("Executing summarize_directory.")
    mod_times = get_file_mod_times(directory)
    cache = load_cache(CACHE_FILE)
    use_cache = False

    if cache and cache.get("mod_times") == mod_times:
        use_cache = True

    summaries = []
    cache_data = {"mod_times": mod_times, "files": {}}

    if use_cache:
        print("Using cached summary data.")
        for file_path, file_data in cache["files"].items():
            summaries.append({
                "file": file_path,
                "summary": file_data["summary"]
            })
        return summaries
    else:
        print("Performing fresh analysis and updating cache.")
        for file_path in mod_times:
            summary, parameters = summarize_code(file_path)
            cache_data["files"][file_path] = {
                "summary": summary,
                "parameters": parameters
            }
            summaries.append({
                "file": file_path,
                "summary": summary
            })
        save_cache(CACHE_FILE, cache_data)
        return summaries

if __name__ == "__main__":
    print("Executing summarize.py")
    analysis_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    temp_workspace = os.environ.get("GNAI_TEMP_WORKSPACE")
    if temp_workspace is None:
        temp_workspace = '.'
    code_file_name = os.environ.get("GNAI_INPUT_GOP_REPO_PATH")
    if not code_file_name:
        print(json.dumps({"output": {"error": "GNAI_INPUT_GOP_REPO_PATH environment variable not set."}}, indent=2))
    else:
        file_path = os.path.join(temp_workspace, code_file_name)
        if os.path.isdir(file_path):
            summaries = summarize_directory(file_path)
            print("Summary:")
            for item in summaries:
                print(f"File: {item['file']}")
                print('\n'.join(item['summary']))
                print()
        else:
            # TO DO : For single file analysis we are not doing caching.
            summary, _ = summarize_code(file_path)
            print("Summary:")
            print('\n'.join(summary))
        cache_file_path = os.path.abspath(CACHE_FILE)
        print(f"Summary Path: {cache_file_path}")
        analysis_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"Analysis time: from {analysis_start_time} to {analysis_end_time}")
        print("Thank you for using the code summarizer tool.")
