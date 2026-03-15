---
name: macos-screenshot
description: macOS 截屏技能。当需要截取屏幕截图时使用。触发词：截屏、截图、screenshot。
---

# macOS 截屏技能

使用 macOS 原生 `screencapture` 命令截取全屏内容。

## 截屏命令

```bash
mkdir -p screenshots && screencapture -x screenshots/screenshot-$(date +%Y-%m-%d-%H%M%S).png
```

`-x` 参数禁用截屏音效。截图保存到项目根目录下的 `screenshots/` 目录。

## 注意事项

- 首次使用时 macOS 可能需要授予终端屏幕录制权限（系统设置 > 隐私与安全 > 屏幕录制）
