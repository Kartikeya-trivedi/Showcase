import os

# We only look at these folders because this is where the logic lives
TARGET_FOLDERS = ['agents', 'app']

for folder in TARGET_FOLDERS:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            # Ignore cache folders to keep it clean
            if "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    print(f"\n{'='*40}")
                    print(f"FILE: {path}")
                    print(f"{'='*40}\n")
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            print(f.read())
                    except Exception as e:
                        print(f"# Could not read file: {e}")