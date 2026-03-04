[app]
# (str) Title of your application
title = Synapse
# (str) Package name
package.name = synapse
# (str) Package domain
package.domain = org.imoter
# (str) Source code where the main.py lives
source.dir = .
# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,csv
# (str) Application versioning
version = 0.1

# REQUIREMENTS: 
# hostpython3 and openssl are MANDATORY for 'requests' (HTTPS) to work on Android
requirements = python3,kivy==2.2.1,kivymd,requests,urllib3,chardet,idna,certifi,hostpython3,openssl,jnius

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API (33 is standard for Play Store now)
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# CRITICAL: This allows the build to finish without waiting for a user to click "Accept"
android.accept_sdk_license = True

# (str) Icon and Presplash (Ensure logo.png is in your main folder)
icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

android.private_storage = True

[buildozer]
# (int) Log level (2 = full debug output)
log_level = 2
# (int) Display warning if buildozer is run as root (0 = off)
warn_on_root = 0
