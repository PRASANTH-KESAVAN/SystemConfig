[app]

(str) Title of your application (CHANGE THIS TO WHATEVER YOU WANT)

title = System Config

(str) Package name (no spaces or special characters)

package.name = sysconfig

(str) Package domain (needed for android/ios packaging)

package.domain = org.myvault

(str) Source code where the main.py lives

source.dir = .

(list) Source files to include (let empty to include all the files)

source.include_exts = py,png,jpg,kv,atlas

(str) Application versioning

version = 1.0

(list) Application requirements

requirements = python3,kivy

(str) Custom source folders for requirements

Sets custom source for any requirements with recipes

(str) Presplash of the application

#presplash.filename = %(source.dir)s/data/presplash.png

(str) Icon of the application (CHANGE THIS TO YOUR CUSTOM LOGO)

Make sure you have a logo.png file in the same folder!

icon.filename = %(source.dir)s/logo.png

(str) Supported orientations (landscape, sensor or portrait)

orientation = portrait

(bool) Indicate if the application should be fullscreen or not

fullscreen = 1

(list) Permissions

android.permissions = INTERNET

(int) Target Android API, should be as high as possible.

android.api = 33

(int) Minimum API your APK will support.

android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1