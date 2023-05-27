import os
import subprocess
from pathlib import Path

VIDEOS_BASE_PATH = '/Volumes/980evo/wj_videos'


def main():
    for root, _, files in os.walk(VIDEOS_BASE_PATH):
        for file in files:
            if file.startswith("._"):
                continue
            file_path = os.path.join(root, file)

            new_filename_prefix = f"{Path(file_path).parent.name}.{file.split()[-1].removesuffix('.mp4')}"
            print(new_filename_prefix)
            subprocess.run(["ffmpeg",
                            "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
                            "-i", file_path,
                            # h264 1080
                            "-c:v", "h264_nvenc", "-b:v", "6000k", "-preset:v", "p7",
                            "-c:a", "libopus", "-b:a", "128k",
                            new_filename_prefix + ".h264.1080.mp4",

                            # h264 720
                            "-c:v", "h264_nvenc", "-b:v", "2400k", "-preset:v", "p7",
                            "-c:a", "libopus", "-b:a", "96k",
                            new_filename_prefix + ".h264.720.mp4",

                            # hevc 1080
                            "-c:v", "hevc_nvenc", "-b:v", "6000k", "-preset:v", "p7",
                            "-c:a", "libopus", "-b:a", "128k",
                            new_filename_prefix + ".hevc.1080.mp4",

                            # hevc 720
                            "-c:v", "hevc_nvenc", "-b:v", "2400k", "-preset:v", "p7",
                            "-c:a", "libopus", "-b:a", "96k",
                            new_filename_prefix + ".hevc.720.mp4",
                            ])


if __name__ == '__main__':
    main()
