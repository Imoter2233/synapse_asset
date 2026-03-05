[app]
title = Synapse
package.name = synapse
package.domain = org.imoter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 0.1

# REQUIREMENTS
# Keeping our "Golden Combo" of Kivy 2.2.1 + KivyMD 1.1.1 + OpenSSL
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,pillow,pyjnius,openssl,urllib3,chardet,idna,certifi

# ORIENTATION FIX - This forces the app to stay vertical!
orientation = portrait

# PERMISSIONS
android.permissions = INTERNET

# ANDROID API SETTINGS
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b

# SPLASH SCREEN & ICONS
icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

# BUILD SETTINGS
[buildozer]
log_level = 2
warn_on_root = 0
