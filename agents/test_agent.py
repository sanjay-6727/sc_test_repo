def run_test_agent(files):
    """
    Analyzes whether new code has corresponding tests.
    """
    issues = []

    for f in files:
        name = f["filename"]

        # Simple logic: if a file is in src/ but nothing in tests/ is changed, warn.
        # This is a basic placeholder; a real implementation would check for matching test files.
        if name.startswith("src/") and f.get("additions", 0) > 20:
            # Check if any other file in the list looks like a test for this file
            test_exists = any("test" in other["filename"].lower() for other in files)
            if not test_exists:
                issues.append(
                    f"**{name}** adds significant logic but no corresponding test files were found in this PR."
                )

    return {
        "agent": "Test Agent",
        "issues": issues
    }
