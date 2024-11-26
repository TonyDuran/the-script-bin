#!/usr/bin/env python3

import os
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

# def rename_images(vault_path, folder_name, rename_logic):
#     """Rename images in the target folder based on specific logic."""
#     target_folder = os.path.join(vault_path, folder_name)
#     if not os.path.isdir(target_folder):
#         print(f"Error: The folder '{target_folder}' does not exist.")
#         return

#     for file_name in os.listdir(target_folder):
#         old_path = os.path.join(target_folder, file_name)
#         if os.path.isfile(old_path):
#             new_name = rename_logic(file_name)
#             new_path = os.path.join(target_folder, new_name)
#             os.rename(old_path, new_path)
#             print(f"Renamed: {file_name} -> {new_name}")

def main(vault_path, folder_name, action):
    if action == "missing":
        missing_images = find_missing_images(vault_path, folder_name)
        print("Missing images:")
        for img in missing_images:
            print(f"  - {img}")
    # elif action == "rename":
    #     def rename_logic(file_name):
    #         # Placeholder logic: Modify as needed
    #         base, ext = os.path.splitext(file_name)
    #         return f"{base}_renamed{ext}"
        
    #     rename_images(vault_path, folder_name, rename_logic)
    else:
        print("Invalid action. Use 'missing'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility for managing screenshots in an Obsidian vault.")
    parser.add_argument("vault_path", help="The path to your Obsidian vault.")
    parser.add_argument("--folder", default="Files", help="The folder containing the images (default: 'Files').")
    parser.add_argument("--action", required=True, choices=["missing"], help="Action to perform: 'missing'.")

    args = parser.parse_args()
    main(args.vault_path, args.folder, args.action)

