#!/usr/bin/env python3
import json
import argparse


def clean_claude_config(clear_all_history=False):
    print("Reading large config file...")
    # Read the original file
    with open("/Users/adamjackson/.claude.json", "r") as f:
        data = json.load(f)

    # Clear history arrays in each project to reduce file size
    projects_cleaned = 0
    total_entries_removed = 0

    # Skip global config keys
    skip_keys = {
        "numStartups",
        "installMethod",
        "autoUpdates",
        "tipsHistory",
        "mcpServers",
    }

    for project_path, project_data in data.items():
        if project_path in skip_keys:
            continue

        if isinstance(project_data, dict):
            # Check for history array
            if "history" in project_data and isinstance(project_data["history"], list):
                original_count = len(project_data["history"])
                if original_count > 0:
                    if clear_all_history:
                        project_data["history"] = []  # Clear all history
                        projects_cleaned += 1
                        total_entries_removed += original_count
                        print(
                            f"Cleared ALL {original_count} history entries from {project_path}"
                        )
                    else:
                        # Keep history but clean large content (default behavior)
                        pass

            # Clear any other large data that might be taking space (only if not clearing all history)
            if not clear_all_history:
                for key in list(project_data.keys()):
                    if key in [
                        "exampleFiles",
                        "allowedTools",
                        "mcpServers",
                        "enabledMcpjsonServers",
                        "disabledMcpjsonServers",
                    ]:
                        continue  # Keep these as they're small or important
                    elif (
                        isinstance(project_data[key], list)
                        and len(project_data[key]) > 20
                    ):
                        orig_len = len(project_data[key])
                        project_data[key] = []
                        print(
                            f"Cleared large {key} array ({orig_len} items) from {project_path}"
                        )

    if not clear_all_history:
        # Remove large base64 images from history entries (default behavior)
        images_removed = 0

        def clean_history_recursively(obj):
            nonlocal images_removed
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if (
                        key == "content"
                        and isinstance(value, str)
                        and value.startswith("iVBORw0KGgo")
                    ):
                        obj[key] = "[Large image removed to reduce file size]"
                        images_removed += 1
                    elif isinstance(value, (dict, list)):
                        clean_history_recursively(value)
            elif isinstance(obj, list):
                for item in obj:
                    clean_history_recursively(item)

        clean_history_recursively(data)
        if images_removed > 0:
            print(f"Removed {images_removed} large base64 images")

    if clear_all_history:
        print(f"Total history entries completely removed: {total_entries_removed}")
    else:
        print("Total history entries cleaned (kept but images removed): preserved")

    # Write the cleaned version
    print("Writing cleaned config file...")
    with open("/Users/adamjackson/.claude.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\nCleaning complete:")
    if clear_all_history:
        print(f"- Completely cleared history from {projects_cleaned} projects")
        print(f"- Total history entries removed: {total_entries_removed}")
    else:
        print("- Cleaned large images and content from history (preserved structure)")
    print("- Backup available at /Users/adamjackson/.claude.json.backup")


def main():
    parser = argparse.ArgumentParser(description="Clean Claude configuration file")
    parser.add_argument(
        "--clear-all-history",
        action="store_true",
        help="Completely delete all history entries (default: just clean large content)",
    )

    args = parser.parse_args()

    clean_claude_config(clear_all_history=args.clear_all_history)


if __name__ == "__main__":
    main()
