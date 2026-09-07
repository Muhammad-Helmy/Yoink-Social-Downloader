import os
import shutil
import subprocess

def detect_hardware() -> dict:
    """
    Detects presence of NVIDIA GPU and NVENC hardware encoding support in FFmpeg.
    """
    gpu_info = {
        "has_nvidia": False,
        "gpu_name": "",
        "nvenc_supported": False,
        "supported_codecs": [],
        "active_mode": "cpu"
    }

    no_win_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    # 1. Check nvidia-smi
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=no_win_flags
        )
        if res.returncode == 0 and res.stdout.strip():
            gpu_info["has_nvidia"] = True
            gpu_info["gpu_name"] = res.stdout.strip().splitlines()[0]
    except Exception:
        pass

    # 2. Check ffmpeg nvenc encoders
    try:
        res = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True,
            text=True,
            timeout=4,
            creationflags=no_win_flags
        )
        if res.returncode == 0:
            out = res.stdout.lower()
            if "h264_nvenc" in out:
                gpu_info["nvenc_supported"] = True
                gpu_info["supported_codecs"].append("h264_nvenc")
            if "hevc_nvenc" in out:
                gpu_info["supported_codecs"].append("hevc_nvenc")
            if "av1_nvenc" in out:
                gpu_info["supported_codecs"].append("av1_nvenc")
    except Exception:
        pass

    # Determine default active mode
    if gpu_info["has_nvidia"] and gpu_info["nvenc_supported"]:
        gpu_info["active_mode"] = "gpu"
    else:
        gpu_info["active_mode"] = "cpu"

    return gpu_info

def get_ffmpeg_hardware_args(mode: str = "auto") -> list:
    """
    Returns optimal FFmpeg arguments for yt-dlp based on user setting ('auto', 'gpu', 'cpu').
    """
    hw = detect_hardware()
    use_gpu = False

    if mode == "auto":
        use_gpu = hw["has_nvidia"] and hw["nvenc_supported"]
    elif mode == "gpu":
        use_gpu = hw["nvenc_supported"]
    else:
        use_gpu = False

    if use_gpu:
        # Pass NVENC video converter arguments when merging or converting
        return ["--postprocessor-args", "VideoConvertor:-c:v h264_nvenc -preset p4 -cq 23"]
    return []
