#!/usr/bin/env python3
"""
长图转PDF工具 - Long Image to PDF Converter

将手机截图/长图按自带横线切片，放大后生成多页PDF。
每刀切在空白行上，不劈文字，文字大小和原图一致。

用法：
    python longimg2pdf.py input.jpg
    python longimg2pdf.py input.jpg -o output.pdf
    python longimg2pdf.py input.jpg --width 2480 --quality 95

依赖：
    pip install Pillow PyMuPDF
"""

import argparse
import os
import sys

try:
    from PIL import Image
    import fitz  # PyMuPDF
except ImportError:
    print("请先安装依赖：pip install Pillow PyMuPDF")
    sys.exit(1)


def find_horizontal_lines(img, min_width_ratio=0.5, threshold=150):
    """
    找图片中的水平横线（文档自带分隔线）。
    
    扫描每行，找连续深色像素超过图片宽度指定比例的行。
    返回横线的Y坐标列表。
    """
    import numpy as np
    arr = np.array(img.convert('L'))
    H, W = arr.shape
    min_line_width = W * min_width_ratio

    line_positions = []
    for y in range(H):
        row = arr[y]
        dark = row < threshold
        # 找最长连续深色像素段
        max_run = 0
        current_run = 0
        for px in dark:
            if px:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        if max_run > min_line_width:
            line_positions.append(y)

    # 合并相近的行（±10px内视为同一条线）
    lines = []
    if line_positions:
        start = line_positions[0]
        prev = line_positions[0]
        for r in line_positions[1:]:
            if r - prev > 10:
                lines.append((start + prev) // 2)
                start = r
            prev = r
        lines.append((start + prev) // 2)

    return lines


def find_cut_points(img, lines, search_range=50):
    """
    在每条横线附近找空白行（>95%白色），作为切割点。
    保证不劈文字。
    """
    import numpy as np
    arr = np.array(img.convert('L'))
    H = arr.shape[0]

    cuts = [0]
    for line_y in lines:
        best_y = line_y
        best_blank = 0
        for y in range(max(0, line_y - search_range), min(H, line_y + search_range)):
            row = arr[y]
            blank_ratio = (row > 200).mean()
            if blank_ratio > best_blank:
                best_blank = blank_ratio
                best_y = y
        cuts.append(best_y)
    cuts.append(H)

    return cuts


def convert_long_image_to_pdf(
    input_path,
    output_path=None,
    target_width=2480,
    img_pt_width=555,
    page_pt_width=595,
    margin_pt=20,
    max_file_size_mb=10,
    initial_quality=95,
):
    """
    长图转PDF主函数。
    
    流程：
    1. 找横线 → 空白行切割
    2. 每段放大到target_width
    3. 放入A4宽度页面，居中
    4. 自适应质量，确保输出<max_file_size_mb
    
    参数：
        input_path: 输入图片路径
        output_path: 输出PDF路径（默认同目录）
        target_width: 目标图片宽度（默认2480px）
        img_pt_width: 图片在页面上的显示宽度（默认555pt）
        page_pt_width: 页面宽度（默认595pt，A4）
        margin_pt: 边距（默认20pt）
        max_file_size_mb: 最大文件大小（默认10MB）
        initial_quality: 初始JPEG质量（默认95）
    """
    if not os.path.exists(input_path):
        print(f"错误：文件不存在 {input_path}")
        sys.exit(1)

    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".pdf"

    # 读取图片
    img = Image.open(input_path)
    W, H = img.size
    print(f"原图：{W}x{H}px")

    # 找横线和切割点
    lines = find_horizontal_lines(img)
    print(f"找到 {len(lines)} 条横线：{lines}")

    cuts = find_cut_points(img, lines)
    print(f"切割点：{cuts}")

    # 计算缩放参数
    scale = target_width / W
    pt_per_px = img_pt_width / target_width  # 每像素对应多少pt

    # 自适应质量
    quality = initial_quality
    while quality >= 30:
        doc = fitz.open()
        for i in range(len(cuts) - 1):
            top, bottom = cuts[i], cuts[i + 1]
            section_h = bottom - top
            section = img.crop((0, top, W, bottom))

            # 放大到target_width
            new_h = int(section_h * scale)
            resized = section.resize((target_width, new_h), Image.LANCZOS)

            # 计算页面高度
            img_display_h = new_h * pt_per_px
            page_h = img_display_h + 2 * margin_pt if img_display_h > (page_pt_width * 1.414) else page_pt_width * 1.414

            # 创建页面
            page = doc.new_page(width=page_pt_width, height=page_h)
            x = (page_pt_width - img_pt_width) / 2
            y = margin_pt
            rect = fitz.Rect(x, y, x + img_pt_width, y + img_display_h)

            # 临时JPEG
            tmp = f"_tmp_page_{i}.jpg"
            resized.save(tmp, "JPEG", quality=quality)
            page.insert_image(rect, filename=tmp)

        doc.save(output_path)
        doc.close()

        # 清理临时文件
        for i in range(len(cuts) - 1):
            tmp = f"_tmp_page_{i}.jpg"
            if os.path.exists(tmp):
                os.remove(tmp)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if size_mb <= max_file_size_mb:
            print(f"完成！{output_path} ({size_mb:.1f}MB, {len(cuts)-1}页, 质量={quality})")
            return output_path
        else:
            print(f"质量{quality}时 {size_mb:.1f}MB > {max_file_size_mb}MB，降低质量重试...")
            quality -= 5

    print(f"警告：即使质量=30仍超过{max_file_size_mb}MB")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="长图转PDF - 按横线切片，放大后生成多页PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python longimg2pdf.py screenshot.jpg
  python longimg2pdf.py screenshot.jpg -o output.pdf
  python longimg2pdf.py screenshot.jpg --quality 90 --max-size 8
        """,
    )
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("-o", "--output", help="输出PDF路径（默认同目录同名.pdf）")
    parser.add_argument("--width", type=int, default=2480, help="目标图片宽度（默认2480px）")
    parser.add_argument("--quality", type=int, default=95, help="初始JPEG质量（默认95，超10MB自动降低）")
    parser.add_argument("--max-size", type=float, default=10, help="最大文件大小MB（默认10）")

    args = parser.parse_args()
    convert_long_image_to_pdf(
        args.input,
        args.output,
        target_width=args.width,
        initial_quality=args.quality,
        max_file_size_mb=args.max_size,
    )


if __name__ == "__main__":
    main()
