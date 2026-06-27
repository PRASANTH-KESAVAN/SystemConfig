Secret App Vault

A highly secure, hidden app vault disguised as a broken Android system app. Built purely with Python + Kivy.

How to Build the APK (Free & Cloud-based)

You do not need Android Studio, Java, or Python installed on your computer.

Fork this repository to your own GitHub account.

Go to the Actions tab in your forked repository.

Click "I understand my workflows, go ahead and enable them".

Make any small change to the README.md (or simply go to Actions -> Build Android APK -> Run workflow).

Wait roughly 15-20 minutes for the cloud runner to download the Android SDK and compile your app.

Once the build turns green ✅, scroll down to the Artifacts section at the bottom of the run summary.

Download the vault-apk.zip file.

Extract the .apk file and send it to your Android device.

Install the APK (Make sure "Install from unknown sources" is enabled in your Android settings).

Features

Disguise Screen: Appears as a corrupted system app or crash screen.

Gesture Unlock: Draw a secret geometric pattern anywhere on the error screen to wake the PIN pad.

Panic Gesture: Draw an alternate gesture to instantly wipe the screen back to fake errors.

App Hiding: Select apps to hide. (Note: Deep hiding via pm disable requires the device to be rooted. On non-rooted devices, the app acts as an isolated launcher).

Intruder Selfie: Automatically takes a silent photo using the front camera if the wrong PIN is entered multiple times.
