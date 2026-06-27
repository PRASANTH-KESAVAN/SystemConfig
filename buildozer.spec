[app]
title = System Config
package.name = vaultapp
package.domain = org.vault
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

requirements = python3,kivy,pyjnius,pillow,android

orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, QUERY_ALL_PACKAGES, REQUEST_DELETE_PACKAGES
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

icon.filename = %(source.dir)s/assets/default_icon.png
presplash.filename = %(source.dir)s/assets/default_presplash.png

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
