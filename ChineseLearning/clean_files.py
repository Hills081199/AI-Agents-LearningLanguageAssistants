import os

def clean_file(file_path):
    print(f"Cleaning {file_path}...")
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for null bytes
        if b'\x00' in content:
            print(f"Found null bytes in {file_path}. Cleaning...")
            # Replace null bytes
            clean_content = content.replace(b'\x00', b'')
            
            # Write back
            with open(file_path, 'wb') as f:
                f.write(clean_content)
            print(f"Cleaned {file_path} (removed {len(content) - len(clean_content)} null bytes)")
        else:
            print(f"No null bytes found in {file_path}")
            
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

if __name__ == "__main__":
    clean_file('main.py')
    clean_file('tasks.py')
