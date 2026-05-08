# -*- coding: utf-8 -*-
# AUTHOR Dsimson
# VERSION 3.0
# 渲染通道图
import lux
import os
import glob

def main():
    # 1. 获取当前界面分辨率作为自定义默认值
    try:
        info = lux.getSceneInfo()
        cur_w = info.get("width", 1920)
        cur_h = info.get("height", 1080)
    except:
        cur_w, cur_h = 1920, 1080

    # 2. 对话框
    resolutions = ["4K (3840×2160)", "8K (7680×4320)", "自定义"]
    formats = ["PNG", "EXR", "TIFF"]
    control_modes = ["采样数（自动切换 CPU）", "时间限制（秒，GPU 可用）", "不控制（使用界面设置）"]

    values = [
        ("preset", lux.DIALOG_ITEM, "分辨率预设", 0, resolutions),
        ("custom_w", lux.DIALOG_INTEGER, "自定义宽度", cur_w),
        ("custom_h", lux.DIALOG_INTEGER, "自定义高度", cur_h),
        ("mode", lux.DIALOG_ITEM, "质量控制方式", 0, control_modes),
        ("samples", lux.DIALOG_INTEGER, "采样数（仅方式1）", 64),
        ("seconds", lux.DIALOG_INTEGER, "时间限制秒（仅方式2）", 60),
        ("format", lux.DIALOG_ITEM, "输出格式", 0, formats),
        ("outdir", lux.DIALOG_FOLDER, "输出文件夹", os.path.expanduser("~/Desktop")),
        ("basename", lux.DIALOG_TEXT, "文件名前缀", "通道图"),
    ]

    dlg = lux.getInputDialog(
        title="渲染通道图",
        desc="选择分辨率、质量控制方式、格式与输出位置。\n"
             "通道类型请在 KeyShot 渲染面板中勾选（需选择“单独文件”模式）。",
        values=values,
        id="RenderChannelsOnly_v3.0"
    )

    if dlg is None:
        print("用户取消。")
        return

    # 3. 解析分辨率
    preset_data = dlg.get("preset", (0, ""))
    preset_idx = preset_data[0] if isinstance(preset_data, (list, tuple)) else int(preset_data)

    if preset_idx == 0:
        width, height = 3840, 2160
    elif preset_idx == 1:
        width, height = 7680, 4320
    else:
        width = int(dlg.get("custom_w", cur_w))
        height = int(dlg.get("custom_h", cur_h))

    # 4. 质量控制方式
    mode_data = dlg.get("mode", (0, ""))
    mode_idx = mode_data[0] if isinstance(mode_data, (list, tuple)) else int(mode_data)

    # 5. 输出格式
    fmt_data = dlg.get("format", (0, ""))
    fmt_idx = fmt_data[0] if isinstance(fmt_data, (list, tuple)) else int(fmt_data)
    out_fmt = formats[fmt_idx]

    # 6. 输出路径
    out_dir = dlg.get("outdir", os.path.expanduser("~/Desktop"))
    if not out_dir:
        print("错误：未选择输出文件夹。")
        return
    base_name = dlg.get("basename", "通道图")
    if not base_name:
        base_name = "通道图"

    save_path = os.path.join(out_dir, base_name + "." + out_fmt.lower())
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"分辨率: {width}x{height} | 格式: {out_fmt}")
    print(f"输出: {save_path}")

    # 7. 应用质量控制
    opts = lux.getRenderOptions()

    if mode_idx == 0:        # 采样数（自动切 CPU）
        samples = int(dlg.get("samples", 64))
        print(f"质量控制: 采样数 = {samples}，尝试切换 CPU...")
        try:
            lux.setRenderEngine("cpu")
            opts.setAdvancedRendering(samples)
            print("已切换为 CPU，采样数设置成功。")
        except Exception as e:
            print(f"切换 CPU 失败（{e}），采样数可能未生效，将使用界面当前设置。")

    elif mode_idx == 1:      # 时间限制（秒）
        seconds = int(dlg.get("seconds", 60))
        print(f"质量控制: 时间限制 = {seconds} 秒（GPU/CPU 通用）")
        try:
            opts.setMaxTimeRendering(seconds)
        except Exception as e:
            print(f"设置时间限制失败: {e}")

    else:                    # 不控制
        print("质量控制: 使用界面当前设置（采样/时间）")

    # 8. 渲染并删除原图
    try:
        lux.renderImage(save_path, width, height, opts)
        print("渲染完成，正在删除原图...")

        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"已删除原图: {save_path}")
        else:
            print("未发现原图文件（请确认输出模式为“单独文件”）")

        dir_path = os.path.dirname(save_path)
        pattern = os.path.join(dir_path, f"{base_name}_*")
        channel_files = glob.glob(pattern)
        print("生成的通道文件：")
        for f in channel_files:
            print(f"  {f}")
    except Exception as e:
        print(f"渲染出错: {e}")

if __name__ == "__main__":
    main()
