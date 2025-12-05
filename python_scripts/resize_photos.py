import os
from PIL import Image
import io

def resize_and_compress_adaptive(image: Image.Image, target_max_size_kb=500):
    """
    根据原图方向自动选择目标比例并缩放至标准尺寸：
    - 横图（宽 >= 高）→ 800x600 (4:3)
    - 竖图（高 > 宽）  → 600x800 (3:4)
    保持中心裁剪 + 高质量缩放。
    """
    w, h = image.size

    if w >= h:
        # 横图：目标 800x600 (4:3)
        target_w, target_h = 800, 600
        crop_ratio = 4 / 3
    else:
        # 竖图：目标 600x800 (3:4)
        target_w, target_h = 600, 800
        crop_ratio = 3 / 4  # 宽/高

    # 计算裁剪区域（保持中心）
    if w / h > crop_ratio:
        # 太宽 → 裁左右
        new_w = int(h * crop_ratio)
        left = (w - new_w) // 2
        right = left + new_w
        top, bottom = 0, h
    else:
        # 太高 → 裁上下
        new_h = int(w / crop_ratio)
        top = (h - new_h) // 2
        bottom = top + new_h
        left, right = 0, w

    cropped = image.crop((left, top, right, bottom))
    # 重采样缩放到目标尺寸（高质量）
    print("target_w:",target_w,"target_h",target_h)
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return resized

def save_image_under_size(image: Image.Image, save_path: str, max_size_kb=500):
    quality = 95
    while quality >= 10:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
            return True
        quality -= 5
    # 最低质量仍超限，强制保存
    image.save(save_path, format="JPEG", quality=10, optimize=True)
    return False

def main():
    input_dir = "input"
    output_dir = "output"

    if not os.path.exists(input_dir):
        print(f"❌ 输入目录 '{input_dir}' 不存在，请创建并放入图片。")
        return

    os.makedirs(output_dir, exist_ok=True)

    supported_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_ext)]
    if not files:
        print("❌ 输入目录中没有找到支持的图片文件。")
        return

    files.sort()  # 保证顺序
    top_filename = input("请输入要作为 top.jpg 的图片文件名（含扩展名，例如 'me.png'）：").strip()

    index = 1
    top_saved = False

    for filename in files:
        src_path = os.path.join(input_dir, filename)
        try:
            with Image.open(src_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 自适应裁剪：横图→4:3，竖图→3:4
                img_cropped = resize_and_compress_adaptive(img)

                if filename == top_filename:
                    save_path = os.path.join(output_dir, "top.jpg")
                    save_image_under_size(img_cropped, save_path, max_size_kb=500)
                    print(f"✅ 保存 top.jpg <- {filename}")
                    top_saved = True
                else:
                    save_path = os.path.join(output_dir, f"{index}.jpg")
                    save_image_under_size(img_cropped, save_path, max_size_kb=500)
                    print(f"✅ 保存 {index}.jpg <- {filename}")
                    index += 1

        except Exception as e:
            print(f"⚠️  跳过文件 {filename}（处理出错）: {e}")

    if not top_saved and top_filename:
        print(f"⚠️  未找到指定的 top 图片 '{top_filename}'，未生成 top.jpg")

    print(f"\n🎉 处理完成！共生成 {index - 1} 张照片 + {'top.jpg' if top_saved else '无 top.jpg'}")

if __name__ == "__main__":
    main()