[app]
title = Synapse
package.name = synapse
package.domain = org.imoter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 0.1

# REQUIREMENTS 
# Added openssl back so 'requests' doesn't crash the app on launch!
requirements = python3,kivy==2.3.0,kivymd,requests,pillow,pyjnius,openssl,urllib3,chardet,idna,certifi

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b

icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png
android.presplash_color = #000000

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
