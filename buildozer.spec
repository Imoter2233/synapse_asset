[app]
title = Synapse
package.name = synapse
package.domain = org.imoter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 0.1

# REQUIREMENTS 
# Swapped 'jnius' for 'pyjnius' (the correct Android recipe).
# Removed redundant networking libs as 'requests' handles them.
requirements = python3,kivy==2.3.0,kivymd,requests,pillow,pyjnius

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
# Force a stable NDK version
android.ndk = 25b

icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

# This is critical for API 33 compatibility
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
