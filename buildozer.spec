[app]
title = Synapse
package.name = synapse
package.domain = org.imoter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 0.1

# MANDATORY: Kivy 2.2.1 + KivyMD 1.1.1 must be used for maximum stability
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,pillow,pyjnius,openssl,urllib3,chardet,idna,certifi

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b

icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

[buildozer]
log_level = 2
warn_on_root = 0
