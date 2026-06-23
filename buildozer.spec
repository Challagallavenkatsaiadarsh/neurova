[app]

title = Neurova
package.name = neurova
package.domain = org.neurova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,kivymd,requests

orientation = portrait

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

android.arch = arm64-v8a

android.allow_backup = True

android.permissions = INTERNET