import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

VIDEO = "termux/home/downloads/baby-fishey-dance-magic-show.mp4"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    return json.loads(r.stdout)


def info(path):
    data = probe(path)
    for s in data["streams"]:
        if s["codec_type"] == "video":
            dur = float(data["format"]["duration"])
            print(f"File:       {path}")
            print(f"Duration:   {dur:.1f}s")
            print(f"Resolution: {s['width']}x{s['height']}")
            print(f"FPS:        {s.get('r_frame_rate', '?')}")
            print(f"Codec:      {s['codec_name']}")
            print(f"Size:       {int(data['format']['size']) / 1e6:.1f} MB")


def extract_frames(path, outdir="frames", every=1):
    Path(outdir).mkdir(exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-vf", f"fps=1/{every}",
        f"{outdir}/frame_%04d.jpg",
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"Frames saved to {outdir}/")


def trim(path, start, end, out="trimmed.mp4"):
    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-ss", str(start), "-to", str(end),
        "-c", "copy", out,
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"Saved {out}")


def clip(path, start, duration, out="clip.mp4"):
    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-ss", str(start), "-t", str(duration),
        "-c", "copy", out,
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"Saved {out}")


def main():
    p = argparse.ArgumentParser(description="Video analysis & editing tools")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("info")

    pf = sub.add_parser("frames")
    pf.add_argument("--every", type=int, default=1, help="Extract one frame every N seconds")

    pt = sub.add_parser("trim")
    pt.add_argument("start", type=float)
    pt.add_argument("end", type=float)

    pc = sub.add_parser("clip")
    pc.add_argument("start", type=float)
    pc.add_argument("duration", type=float)

    a = p.parse_args()
    if a.cmd == "info":
        info(VIDEO)
    elif a.cmd == "frames":
        extract_frames(VIDEO, every=a.every)
    elif a.cmd == "trim":
        trim(VIDEO, a.start, a.end)
    elif a.cmd == "clip":
        clip(VIDEO, a.start, a.duration)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
