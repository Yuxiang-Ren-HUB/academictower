[app]
title = 学术魔塔
package.name = academictower
package.domain = org.pygame.game
source.dir = .
source.include_exts = py,webp,ogg
source.exclude_dirs = build, .github, __pycache__
version = 1.0
requirements = python3,cython,pygame==2.5.2
orientation = portrait
fullscreen = 1
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a
p4a.bootstrap = sdl2
log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2
warn_on_root = 0
