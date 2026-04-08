import argparse
import os
import random
import time
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, vfx, afx, CompositeVideoClip
from PIL import Image, ImageFilter
import numpy as np

# ================= 配置区 =================
MY_IMAGES = r"C:\Users\HongWei\Desktop\photos\2"  # 图片文件夹
MY_MUSIC = r"C:\Users\HongWei\Desktop\photos\Spring_Welcome_Walk_春日徒步.mp3"   # 音乐路径
OUTPUT_NAME = f"my_album_{time.strftime('%Y%m%d_%H%M%S')}.mp4"                    # 输出文件名

# 建议设置一个标准分辨率，比如 1080p (1920x1080) 或 竖屏 (1080x1920)
VIDEO_SIZE = (1080, 1920) 
IMAGE_DURATION = 4.0   # 每张图片显示的秒数 (你可以随意修改这个常量)
TRANSITION_TIME = 0.8  # 转场重叠时间 (秒)，建议小于图片时长的一半
# ==========================================
def crop_to_fill(clip, target_size):
    """
    让图片按比例缩放并裁剪，直到填满指定的屏幕尺寸（无黑边）
    """
    w, h = clip.size
    target_w, target_h = target_size
    
    # 计算缩放比例，取大的那个，确保填满
    ratio = max(target_w / w, target_h / h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    
    # 缩放图片并裁剪中心区域
    clip = clip.resized(width=new_w) # 先缩放
    # 裁剪中心位置
    clip = clip.cropped(
        x_center=new_w / 2, 
        y_center=new_h / 2, 
        width=target_w, 
        height=target_h
    )
    return clip

def create_blurred_background(img_path, target_size, duration):
    """
    创建一个带有模糊背景的 Clip：
    底层是放大模糊的图片，顶层是完整显示的原图。
    """
    tw, th = target_size
    
    # 1. 创建顶层：完整图片 (保持比例)
    foreground = ImageClip(img_path).with_duration(duration)
    # 缩放至适应屏幕高度或宽度
    foreground = foreground.resized(height=th) if (foreground.w/foreground.h < tw/th) else foreground.resized(width=tw)
    # 居中
    foreground = foreground.with_position("center")

    # 2. 创建底层：模糊背景
    background_pil = Image.open(img_path)
    # 放大背景以填满全屏
    w, h = background_pil.size
    bg_ratio = max(tw / w, th / h)
    new_w, new_h = int(w * bg_ratio), int(h * bg_ratio)
    background_pil = background_pil.resize((new_w, new_h), Image.LANCZOS)
    # 裁剪中心区域
    left = (new_w - tw) / 2
    top = (new_h - th) / 2
    right = left + tw
    bottom = top + th
    background_pil = background_pil.crop((left, top, right, bottom))
    # 添加模糊
    background_pil = background_pil.filter(ImageFilter.GaussianBlur(radius=20))
    # 转换为数组
    background_array = np.array(background_pil)
    background = ImageClip(background_array, duration=duration)
    # 调暗背景，突出主体
    background = background.with_effects([vfx.LumContrast(lum=0.7)])

    # 3. 合并
    return CompositeVideoClip([background, foreground], size=target_size)

def create_cube_transition_clip(clip, is_first=False, is_last=False):
    """
    让每张图片在进入时从右侧滑入，在离开时向左侧滑出，模拟正方体顺时针旋转的效果。
    使用实际的位移动画来实现真正的滑动效果。
    """
    w, h = clip.size
    
    # 为第一张图片：从右侧滑入
    if is_first:
        # 从屏幕右侧外开始，移动到正常位置
        clip = clip.with_position(lambda t: (
            w * (1 - t / TRANSITION_TIME) if t < TRANSITION_TIME else 0,
            0
        ))
    # 为最后一张图片：向左侧滑出
    elif is_last:
        # 从正常位置开始，向左侧滑出
        clip = clip.with_position(lambda t: (
            -w * (t / TRANSITION_TIME) if t > (clip.duration - TRANSITION_TIME) else 0,
            0
        ))
    # 中间图片：从右侧滑入，然后向左侧滑出
    else:
        def get_position(t):
            if t < TRANSITION_TIME:
                # 进入阶段：从右侧滑入
                return (w * (1 - t / TRANSITION_TIME), 0)
            elif t > (clip.duration - TRANSITION_TIME):
                # 离开阶段：向左侧滑出
                exit_progress = (t - (clip.duration - TRANSITION_TIME)) / TRANSITION_TIME
                return (-w * exit_progress, 0)
            else:
                # 停留阶段：保持居中
                return (0, 0)
        clip = clip.with_position(get_position)
    
    return clip


def create_fade_transition_clip(clip):
    """
    经典淡入淡出转场。
    """
    return clip.with_effects([
        vfx.CrossFadeIn(TRANSITION_TIME),
        vfx.CrossFadeOut(TRANSITION_TIME)
    ])


def apply_transition(clip, mode, is_first=False, is_last=False):
    if mode == "cube":
        return create_cube_transition_clip(clip, is_first=is_first, is_last=is_last)
    else:
        return create_fade_transition_clip(clip)


def create_slide_transition_clip(clip, prev_clip=None, next_clip=None, is_first=False, is_last=False):
    """
    创建滑动转场效果 - 用于实现真正的立方体风格滑动
    这个函数用于创建两个clip之间的滑动转场
    """
    w, h = clip.size
    
    if is_first:
        # 第一张：从右向左滑入
        return clip.with_position(lambda t: (w * max(0, 1 - t/TRANSITION_TIME), 0))
    elif is_last:
        # 最后一张：从左向右滑出
        return clip.with_position(lambda t: (-w * max(0, (t - (clip.duration - TRANSITION_TIME))/TRANSITION_TIME), 0))
    else:
        # 中间图片：从右滑入，然后向左滑出
        def position_func(t):
            if t < TRANSITION_TIME:
                # 进入：从右向左
                return (w * (1 - t/TRANSITION_TIME), 0)
            elif t > clip.duration - TRANSITION_TIME:
                # 离开：从左向右
                progress = (t - (clip.duration - TRANSITION_TIME)) / TRANSITION_TIME
                return (-w * progress, 0)
            else:
                return (0, 0)
        return clip.with_position(position_func)


def create_smooth_slideshow(transition_mode="cube"):
    # 1. 获取图片列表
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = [
        os.path.join(MY_IMAGES, f) for f in sorted(os.listdir(MY_IMAGES))
        if f.lower().endswith(valid_extensions)
    ]
    
    if not image_files:
        print("错误：文件夹内没找到图片")
        return

    # 2. 处理图片片段
    image_files = [os.path.join(MY_IMAGES, f) for f in sorted(os.listdir(MY_IMAGES)) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    clips = []
    print(f"正在以【模糊背景模式】处理 {len(image_files)} 张图片...")
    print(f"转场效果:{'为正方体风格滑动' if transition_mode == 'cube' else '为淡入淡出'}")
    
    for index, img_path in enumerate(image_files):
        # 根据位置和转场模式计算每张图片的实际持续时间
        is_first = (index == 0)
        is_last = (index == len(image_files) - 1)
        
        if transition_mode == "cube":
            # cube模式下，中间图片需要额外的时间来完成滑入和滑出
            # 第一张：滑入时间 + 显示时间
            # 中间：滑入时间 + 显示时间 + 滑出时间
            # 最后一张：显示时间 + 滑出时间
            if is_first:
                duration = IMAGE_DURATION + TRANSITION_TIME
            elif is_last:
                duration = IMAGE_DURATION + TRANSITION_TIME
            else:
                duration = IMAGE_DURATION + 2 * TRANSITION_TIME
        else:
            # fade模式下保持原样
            duration = IMAGE_DURATION
        
        # 使用新函数创建复合片段
        clip = create_blurred_background(img_path, VIDEO_SIZE, duration)
        
        # 添加转场效果：cube 或 fade
        clip = apply_transition(
            clip,
            transition_mode,
            is_first=is_first,
            is_last=is_last
        )
        clips.append(clip)

    # 合成与导出 (method="compose" 是关键)
    if transition_mode == "cube":
        # cube模式下，使用负padding让视频重叠，实现滑动转场
        video = concatenate_videoclips(clips, method="compose", padding=-TRANSITION_TIME)
    else:
        video = concatenate_videoclips(clips, method="compose", padding=-TRANSITION_TIME)
    
    # 音频处理逻辑 (同之前)
    audio = AudioFileClip(MY_MUSIC)
    if audio.duration < video.duration:
        audio = audio.with_effects([afx.AudioLoop(duration=video.duration)])
    else:
        audio = audio.subclipped(0, video.duration).with_effects([afx.AudioFadeOut(2)])
    
    final_video = video.with_audio(audio)
    final_video.write_videofile(OUTPUT_NAME, fps=24, codec="libx264")
    
    # 资源释放
    final_video.close()
    audio.close()
    audio.close()
    
    print(f"--- 生成成功！文件保存在: {OUTPUT_NAME} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成带转场的幻灯片视频")
    parser.add_argument(
        "--transition",
        choices=["cube", "fade"],
        default="cube",
        help="转场类型：cube 为正方体风格滑动，fade 为淡入淡出"
    )
    args = parser.parse_args()
    create_smooth_slideshow(transition_mode=args.transition)