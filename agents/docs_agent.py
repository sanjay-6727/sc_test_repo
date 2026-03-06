def run_docs_agent(files):
    """
    Checks for missing documentation or README updates.
    """
    issues = []
    
    has_readme_change = any("README" in f["filename"] for f in files)
    
    for f in files:
        # Heuristic: New large files should probably have docstrings or README updates
        if f.get("additions", 0) > 50 and not has_readme_change:
            issues.append(f"Significant changes in **{f['filename']}** without a corresponding README update.")

    return {
        "agent": "Docs Agent",
        "issues": issues
    }
