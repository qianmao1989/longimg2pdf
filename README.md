# longimg2pdf

将手机长截图/长图按自带横线切片，放大后生成多页A4 PDF。

## 特性

- 自动检测文档中的水平分隔线
- 在空白行处切割，不劈文字
- 每段放大到2480px宽度，保持文字清晰
- 自适应JPEG质量，确保输出 ≤ 10MB
- 支持 jpg/png/bmp 等常见图片格式

## 安装

```bash
pip install Pillow PyMuPDF numpy
```

## 使用

```bash
# 基本用法
python longimg2pdf.py input.jpg

# 指定输出路径
python longimg2pdf.py input.jpg -o output.pdf

# 自定义参数
python longimg2pdf.py input.jpg --width 2480 --quality 90 --max-size 8
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input` | (必填) | 输入图片路径 |
| `-o, --output` | 同目录同名.pdf | 输出PDF路径 |
| `--width` | 2480 | 目标图片宽度(px) |
| `--quality` | 95 | 初始JPEG质量(超限自动降低) |
| `--max-size` | 10 | 最大文件大小(MB) |

## 原理

1. 扫描图片找水平横线（连续深色像素超过宽度50%）
2. 在横线附近找最空白的行作为切割点
3. 每段放大到目标宽度，放入A4页面
4. 如果文件超限，自动降低JPEG质量重试

## License

MIT
