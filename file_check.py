import subprocess

FFMPEG_PATH = "C:\\Users\\angel\\ffmpeg-2024-06-06-git-d55f5cba7b-full_build\\bin\\ffmpeg.exe"  
test_command = [FFMPEG_PATH, '-version']

try:
    process = subprocess.Popen(test_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode())
    print(stderr.decode())
except PermissionError as e:
    print(f"Permission error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
