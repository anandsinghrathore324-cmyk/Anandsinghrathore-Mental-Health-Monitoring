import os
import shutil
import kagglehub

def download_and_setup(dataset_handle):
    print(f"\n--- Processing {dataset_handle} ---")
    print(f"Downloading dataset using kagglehub...")
    path = kagglehub.dataset_download(dataset_handle)
    print("Downloaded to cache path:", path)
    
    # Get the dataset directory name (e.g. sentiment140 or depression-reddit-cleaned)
    dataset_dirname = dataset_handle.split("/")[-1]
    dest_dir = os.path.join(os.getcwd(), "data", dataset_dirname)
    os.makedirs(dest_dir, exist_ok=True)
    
    print(f"Copying files from {path} to {dest_dir}...")
    for item in os.listdir(path):
        src_item = os.path.join(path, item)
        dest_item = os.path.join(dest_dir, item)
        if os.path.isdir(src_item):
            if os.path.exists(dest_item):
                shutil.rmtree(dest_item)
            shutil.copytree(src_item, dest_item)
        else:
            shutil.copy2(src_item, dest_item)
            
    print(f"Dataset successfully set up at: {dest_dir}")
    print("Files inside directory:")
    for file in os.listdir(dest_dir):
        print(f" - {file}")

def cleanup_legacy():
    # Clean up the loose csv file that was placed directly in the data folder previously
    legacy_file = os.path.join(os.getcwd(), "data", "training.1600000.processed.noemoticon.csv")
    if os.path.exists(legacy_file):
        print(f"Cleaning up legacy file: {legacy_file}")
        os.remove(legacy_file)

def main():
    cleanup_legacy()
    datasets = [
        "kazanova/sentiment140",
        "infamouscoder/depression-reddit-cleaned",
        "reihanenamdari/mental-health-corpus"
    ]
    for dataset in datasets:
        download_and_setup(dataset)

if __name__ == "__main__":
    main()
