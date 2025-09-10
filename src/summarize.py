import argparse
import re

def summarize_code(file_path):
    with open(file_path, 'r') as f:
        code = f.read()

    # Regex to match C function definitions (simple heuristic)
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

    print("Summary:")
    print('\n'.join(summary))
    print("\nAll parameters found:")
    print(', '.join(parameters))

if __name__ == "__main__":
    import os
    import json

    print("Executing summarize.py")
    temp_workspace = os.environ.get("GNAI_TEMP_WORKSPACE")
    if temp_workspace is None:
        temp_workspace = '.'
    code_file_name = os.environ.get("GNAI_INPUT_GOP_REPO_PATH")
    if not code_file_name:
        print(json.dumps({"output": {"error": "GNAI_INPUT_GOP_REPO_PATH environment variable not set."}}, indent=2))
    else:
        file_path = os.path.join(temp_workspace, code_file_name)
        summarize_code(file_path)