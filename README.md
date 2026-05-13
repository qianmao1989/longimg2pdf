# 长图转PDF - Long Image to PDF

将手机截图、长图按自带横线切片，放大后生成多页PDF。每刀切在空白行上，不劈文字。

## 效果

- ✅ 自动识别图片中的水平分隔线
- ✅ 在横线附近找空白行切割，保证不劈文字
- ✅ 文字大小和原图一致（缩放比4.47px/pt）
- ✅ 页面高度自适应内容，不强制A4
- ✅ 自适应质量：从95开始，超10MB自动降低
- ✅ 输出<10MB，WPS不压缩画质

## 安装

```bash
pip install Pillow PyMuPDF
```

## 用法

```bash
# 基本用法
python longimg2pdf.py screenshot.jpg

# 指定输出路径
python longimg2pdf.py screenshot.jpg -o output.pdf

# 自定义参数
python longimg2pdf.py screenshot.jpg --quality 90 --max-size 8
```

## Python调用

```python
from longimg2pdf import convert_long_image_to_pdf

convert_long_image_to_pdf(
    input_path="screenshot.jpg",
    output_path="output.pdf",
    target_width=2480,      # 放大到2480px宽
    initial_quality=95,     # 从质量95开始试
    max_file_size_mb=10,    # 不超过10MB
)
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `target_width` | 2480 | 目标图片宽度（px） |
| `img_pt_width` | 555 | 图片在页面上的显示宽度（pt） |
| `page_pt_width` | 595 | 页面宽度（pt，A4=595） |
| `margin_pt` | 20 | 页面边距（pt） |
| `initial_quality` | 95 | 初始JPEG质量 |
| `max_file_size_mb` | 10 | 最大输出文件大小（MB） |

## 工作原理

1. **找横线**：扫描图片，找连续深色像素>50%宽度的行（文档自带分隔线）
2. **切割**：在横线附近找空白行（>95%白色），保证不劈文字
3. **放大**：每段从原图宽度放大到2480px（LANCZOS插值）
4. **排版**：放入A4宽度页面（595pt），图片居中显示（555pt宽）
5. **压缩**：自适应JPEG质量，确保输出<10MB

## 依赖

- Python 3.7+
- [Pillow](https://pillow.readthedocs.io/) - 图片处理
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF生成

## License

MIT
