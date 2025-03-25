import os
import json
import shutil

def filter_podcast_files(folder_path, podcast_name):
    """Filters text files in a folder based on partial matching of the 'EPodcast Name' field in JSON content."""
    matching_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            try:
                # Read the file and parse as JSON
                with open(file_path, "r", encoding="utf-8") as file:
                    content = json.load(file)  # Load JSON from txt file
                
                # Check if 'EPodcast Name' exists and partially matches the search query
                if "Podcast Name" in content and podcast_name.lower() in content["Podcast Name"].lower():
                    matching_files.append(file_path)
            
            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON format.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return matching_files

def create_folder_and_copy_files(folder_path, matching_files, output_folder):
    """Creates a folder and copies the matching files into that folder."""
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    # Copy matching files to the new folder
    for file in matching_files:
        # Get the filename from the full file path
        filename = os.path.basename(file)
        destination = os.path.join(output_folder, filename)
        shutil.copy(file, destination)
        print(f"Copied {filename} to {output_folder}")

# Specify the folder and podcast name to search for (partial match)
folder_path = "data/local"  # Change this to your actual folder path
# podcast_name = "Your Podcast Name"   # Replace with part of the podcast name you're searching for
podcast_name = input("Enter the podcast name (or partial name) to search for: ")


# Specify the output folder where matching files will be copied
output_folder = folder_path +"/" +  podcast_name  # Specify the output folder here

# Get matching files
matching_files = filter_podcast_files(folder_path, podcast_name)

# Create folder and copy matching files
create_folder_and_copy_files(folder_path, matching_files, output_folder)
