def run_security_agent(files):
    """
    Scans for security vulnerabilities and hardcoded secrets.
    """
    issues = []
    
    # Common secret keywords to look for in filenames or types
    secret_patterns = [".env", "key", "secret", "token", "password"]
    
    for f in files:
        name = f["filename"].lower()
        if any(pattern in name for pattern in secret_patterns) and not name.endswith(".example"):
            issues.append(f"Potential secret file **{f['filename']}** detected. Ensure secrets are not committed.")

    return {
        "agent": "Security Agent",
        "issues": issues
    }
