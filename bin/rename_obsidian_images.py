#!/usr/bin/env python3

import os
import re
import argparse

def find_missing_images(vault_path, folder_name):
    """Find images in the folder that are not referenced in any markdown files."""
    target_folder = os.path.join(vault_path, folder_name)
    if not os.path.isdir(target_folder):
        print(f"Error: The folder '{target_folder}' does not exist.")
        return []
    
    # Get all markdown files in the vault
    md_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(vault_path)
        for file in files if file.endswith(".md")
    ]
    
    # Get all image files in the target folder
    image_files = [
        file for file in os.listdir(target_folder)
        if os.path.isfile(os.path.join(target_folder, file))
    ]

    # Find references in markdown files
    referenced_images = set()
    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            for image in image_files:
                if image in content:
                    referenced_images.add(image)
    
    # Find missing images
    missing_images = [img for img in image_files if img not in referenced_images]
    print(f"Found {len(missing_images)} missing images.")
    return missing_images

def delete_files(target_folder, files_to_delete):
    """Delete files from the specified folder."""
    for file_name in files_to_delete:
        file_path = os.path.join(target_folder, file_name)
        try:
            os.remove(file_path)
            print(f"Deleted: {file_name}")
        except Exception as e:
            print(f"Failed to delete {file_name}: {e}")

def rename_images(vault_path, folder_name):
    """Rename images following specific logic and update references in markdown files."""
    target_folder = os.path.join(vault_path, folder_name)
    if not os.path.isdir(target_folder):
        print(f"Error: The folder '{target_folder}' does not exist.")
        return

    # Get markdown files
    md_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(vault_path)
        for file in files if file.endswith(".md")
    ]

    # Regex for matching the specific file pattern
    pattern = r"Pasted image (\d{14})(\.\w+)$"

    # Rename files and update references
    for file_name in os.listdir(target_folder):
        match = re.match(pattern, file_name)
        if match:
            timestamp, extension = match.groups()
            new_name = f"image-{timestamp}{extension}"
            old_path = os.path.join(target_folder, file_name)
            new_path = os.path.join(target_folder, new_name)
            
            # Rename the file
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {file_name} -> {new_name}")
            except Exception as e:
                print(f"Failed to rename {file_name}: {e}")
                continue

            # Update references in markdown files
            for md_file in md_files:
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    updated_content = content.replace(file_name, new_name)
                    with open(md_file, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    print(f"Updated references in: {md_file}")
                except Exception as e:
                    print(f"Failed to update references in {md_file}: {e}")

def main(vault_path, folder_name, action):
    if action == "missing":
        missing_images = find_missing_images(vault_path, folder_name)
        print("Missing images:")
        for img in missing_images:
            print(f"  - {img}")

        # Prompt user for deletion
        if missing_images:
            delete_input = input("Would you like to delete these missing files? (y/n): ").strip().lower()
            if delete_input == "y":
                delete_files(os.path.join(vault_path, folder_name), missing_images)
            else:
                print("No files were deleted.")
    elif action == "rename":
        rename_images(vault_path, folder_name)
    else:
        print("Invalid action. Use 'missing' or 'rename'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility for managing screenshots in an Obsidian vault.")
    parser.add_argument("vault_path", help="The path to your Obsidian vault.")
    parser.add_argument("--folder", default="Files", help="The folder containing the images (default: 'Files').")
    parser.add_argument("--action", required=True, choices=["missing", "rename"], help="Action to perform: 'missing' or 'rename'.")

    args = parser.parse_args()
    main(args.vault_path, args.folder, args.action)

