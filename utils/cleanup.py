import os
import shutil

class SystemCleanup:
    @staticmethod
    def run():
        print("Cleaning up system files before exit...")
        dirs_to_remove = ['__pycache__', '.idea']
        for d in dirs_to_remove:
            if os.path.exists(d) and os.path.isdir(d):
                try:
                    shutil.rmtree(d, ignore_errors=True)
                    print(f"Removed {d} successfully.")
                except Exception as e:
                    print(f"Error removing {d}: {e}")
