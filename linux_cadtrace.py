import os
import sys
import cv2
import ezdxf
from PIL import Image
from svgpathtools import svg2paths2
from ezdxf.math import Vec2
import subprocess

potrace_path = '/usr/bin/potrace'  # Adjust if needed

def convert_to_pbm(input_image_path):
    img = Image.open(input_image_path).convert('L')  # grayscale
    bw = img.point(lambda x: 0 if x < 128 else 255, '1')  # binarize
    pbm_path = os.path.splitext(input_image_path)[0] + ".pbm"
    bw.save(pbm_path)
    return pbm_path

def trace_with_potrace(pbm_path):
    svg_path = pbm_path.replace(".pbm", ".svg")
    # Use subprocess for safety
    result = subprocess.run([potrace_path, pbm_path, '-s', '-o', svg_path], capture_output=True)
    if result.returncode != 0:
        print(f"Potrace failed: {result.stderr.decode()}")
        return None
    return svg_path

def svg_path_to_dxf_coords(path_obj, samples=100):
    coords = []
    for segment in path_obj:
        for t in [i / samples for i in range(samples + 1)]:
            point = segment.point(t)
            coords.append((point.real, -point.imag))  # flip Y axis for DXF
    return coords

def svg_to_dxf(svg_path, dxf_path, samples_per_curve=40):
    print(f"[SVG→DXF] Parsing SVG from: {svg_path}")
    try:
        paths, attributes, svg_attr = svg2paths2(svg_path)
    except Exception as e:
        print(f"Error reading SVG: {e}")
        return False

    if not paths:
        print("No paths found in SVG.")
        return False

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    path_count = 0
    for path in paths:
        coords = []
        for segment in path:
            for t in [i / samples_per_curve for i in range(samples_per_curve + 1)]:
                point = segment.point(t)
                coords.append((point.real, -point.imag))

        simplified = [Vec2(*coords[0])]
        for pt in coords[1:]:
            if Vec2(*pt).distance(simplified[-1]) > 0.1:
                simplified.append(Vec2(*pt))

        if len(simplified) >= 2:
            msp.add_lwpolyline(simplified, close=True)
            path_count += 1

    if path_count > 0:
        doc.saveas(dxf_path)
        print(f"[✔] DXF saved to: {dxf_path} with {path_count} polylines.")
        return True
    else:
        print("[!] No valid paths found to write to DXF.")
        return False

def main(image_path):
    if not os.path.exists(image_path):
        print("Image file not found.")
        return

    print(f"[1] Preprocessing {image_path}")
    pbm_path = convert_to_pbm(image_path)

    print(f"[2] Tracing with Potrace")
    svg_path = trace_with_potrace(pbm_path)
    if not svg_path:
        print("Potrace failed, aborting.")
        return

    print(f"[3] Exporting to DXF")
    dxf_path = svg_path.replace(".svg", ".dxf")
    success = svg_to_dxf(svg_path, dxf_path)
    if success:
        print("Done.")
        return dxf_path 
    else:
        print("DXF export failed.")

