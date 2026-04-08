# makevideo
Generate video from images

通过图片和音频文件生成视频
本来想做两种转场的没搞定，目前只有一个淡出淡入转场

# 使用方法
做如下配置后直接运行即可
# ================= 配置区 =================
MY_IMAGES = r"C:\Users\User\Desktop\photos"                          # 图片文件夹
MY_MUSIC = r"C:\Users\User\Desktop\photos\Spring_Welcome_Walk.mp3"   # 音乐路径
OUTPUT_NAME = f"my_album_{time.strftime('%Y%m%d_%H%M%S')}.mp4"       # 输出文件名

# 建议设置一个标准分辨率，比如 1080p (1920x1080) 或 竖屏 (1080x1920)
VIDEO_SIZE = (1080, 1920) 
IMAGE_DURATION = 4.0   # 每张图片显示的秒数 (你可以随意修改这个常量)
TRANSITION_TIME = 0.8  # 转场重叠时间 (秒)，建议小于图片时长的一半

