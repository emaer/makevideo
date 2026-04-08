# 幻灯片视频生成器

一个基于 MoviePy 的 Python 脚本，用于将图片文件夹转换为带音乐和转场效果的视频。

## 功能特性

- 支持多种图片格式 (JPG, PNG, JPEG, BMP)
- 模糊背景效果，突出主体图片
- 两种转场模式：
  - `cube`: 正方体风格滑动转场
  - `fade`: 经典淡入淡出转场
- 自动音频循环或剪辑适配
- 支持竖屏和横屏视频输出

## 安装依赖

确保安装以下 Python 库：

```bash
pip install moviepy pillow numpy
```

### 依赖说明

- **moviepy**: 视频编辑和合成
- **pillow**: 图片处理
- **numpy**: 数组操作

## 使用方法

### 基本使用

```bash
python make_video.py
```

### 指定转场模式

```bash
# 使用正方体滑动转场 (默认)
python make_video.py --transition cube

# 使用淡入淡出转场
python make_video.py --transition fade
```

### 查看帮助

```bash
python make_video.py --help
```

## 配置说明

在脚本顶部的配置区修改以下参数：

```python
MY_IMAGES = r"C:\Users\User\Desktop\photos"                                  # 图片文件夹路径
MY_MUSIC = r"C:\Users\User\Desktop\photos\Spring_Welcome_Walk_春日徒步.mp3"   # 音乐文件路径
OUTPUT_NAME = f"my_album_{time.strftime('%Y%m%d_%H%M%S')}.mp4"               # 输出文件名
VIDEO_SIZE = (1080, 1920)  # 视频分辨率 (宽, 高)
IMAGE_DURATION = 4.0       # 每张图片显示时长 (秒)
TRANSITION_TIME = 0.8      # 转场重叠时间 (秒)
```

## 文件结构

```
make_video.py          # 主脚本
README.md             # 使用说明
```

## 输出格式

- 视频格式: MP4
- 编码: H.264
- 帧率: 24 FPS
- 分辨率: 可配置 (默认 1080x1920 竖屏)

## 注意事项

1. 确保图片文件夹路径正确且包含支持的图片格式
2. 音乐文件路径正确，支持 MP3 等常见音频格式
3. 输出目录需要有写入权限
4. 首次运行可能需要下载 MoviePy 的依赖 (如 FFmpeg)

## 故障排除

### 常见错误

1. **ModuleNotFoundError**: 缺少依赖库，请运行 `pip install moviepy pillow numpy`

2. **FileNotFoundError**: 检查图片文件夹和音乐文件路径是否正确

3. **AttributeError**: MoviePy 版本问题，请确保使用兼容版本

### 性能优化

- 对于大量图片，处理时间会较长
- 建议使用高分辨率图片以获得更好效果
- 可以调整 `IMAGE_DURATION` 和 `TRANSITION_TIME` 来控制视频节奏

## 许可证

本项目仅供学习和个人使用。
