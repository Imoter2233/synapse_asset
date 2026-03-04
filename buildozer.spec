[app]
title = Synapse
package.name = synapse
package.domain = org.imoter
source.dir = .
# This includes all your PNG and JPG medical assets
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 0.1

# MANDATORY: hostpython3 and openssl for your HTTPS requests
requirements = python3,kivy==2.2.1,kivymd,requests,urllib3,chardet,idna,certifi,hostpython3,openssl,jnius

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# Auto-accepts SDK licenses so the build doesn't hang
android.accept_sdk_license = True

icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

[buildozer]
log_level = 2
warn_on_root = 0
