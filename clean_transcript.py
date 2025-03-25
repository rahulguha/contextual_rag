import re
import os

def remove_timestamps_and_fix_speaker(text):
    """Removes timestamps, prevents repeated speaker names, and removes extra blank lines."""
    pattern = r'\d+\n\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n'
    cleaned_text = re.sub(pattern, '', text)

    lines = cleaned_text.split("\n")
    formatted_lines = []
    last_speaker = None

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if not line:
            continue  # Skip empty lines

        if ": " in line:
            speaker, dialogue = line.split(": ", 1)
            if speaker == last_speaker:
                formatted_lines.append(dialogue)
            else:
                formatted_lines.append(f"{speaker}: {dialogue}")
                last_speaker = speaker
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)

def clean_transcripts_in_folder(folder_path):
    """Cleans all .txt transcripts in the specified folder."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            
            # Read the file content
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Clean the content
            cleaned_content = remove_timestamps_and_fix_speaker(content)

            # Write the cleaned content back to the file (or save as a new file)
            cleaned_file_path = os.path.join(folder_path, f"cleaned_{filename}")
            with open(cleaned_file_path, "w", encoding="utf-8") as file:
                file.write(cleaned_content)
            
            print(f"Processed: {filename} -> {cleaned_file_path}")

# Specify the folder containing the text files



folder_path = "data/transcripts"  # Change this to your actual folder path
clean_transcripts_in_folder(folder_path)
