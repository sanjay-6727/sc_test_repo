def run_code_agent(files):
    """
    Analyzes code quality and complexity based on file metadata.
    """
    issues = []
    for f in files:
        # Heuristic: highlight extremely large files
        if f.get("additions", 0) > 100:
            issues.append(f"**{f['filename']}** is quite large (>100 lines). Consider breaking it into smaller modules.")
        
        # Heuristic: check for long filenames (often indicates poor naming)
        if len(f['filename']) > 50:
             issues.append(f"Filename **{f['filename']}** is very long. Consider a more concise name.")

    return {
        "agent": "Code Agent",
        "issues": issues
    }
