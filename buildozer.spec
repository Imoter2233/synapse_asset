[app]
# (str) Title of your application
title = Synapse

# (str) Package name
package.name = synapse

# (str) Package domain (needed for android/ios packaging)
package.domain = org.imoter

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,csv

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Added hostpython3 and openssl so the 'requests' library can handle HTTPS
requirements = python3,kivy==2.2.1,kivymd,requests,urllib3,chardet,idna,certifi,hostpython3,openssl

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API (33 is good for 2024/2025 standards)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (list) The Android archs to build for
# Added armeabi-v7a for better device compatibility
android.archs = arm64-v8a, armeabi-v7a

# (bool) Automatically accept SDK license agreements (CRITICAL for GitHub Actions)
android.accept_sdk_license = True

# (str) Icon and Presplash
icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off)
warn_on_root = 0
