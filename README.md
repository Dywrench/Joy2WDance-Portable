# Joy2WDance Portable

A portable setup for using Joy-Con 2 controllers with JoyDance and Joy2Win on Windows.

## Quick Setup Guide

### 1. Install vJoy

Open the `Installer_Vjoy` folder and run `vJoySetup.exe`. Follow the installation instructions.

After installation, open **Configure vJoy** and make sure the required virtual controller is enabled and configured.

### 2. Connect your controllers

Pair both Joy-Con 2 controllers with your PC using Bluetooth through Windows settings.

### 3. Set up the environment

Run `Setup_Portable.bat` from the main project folder.

This script checks for Python 3.10, creates the Python virtual environment if needed, and installs the dependencies required by JoyDance and Joy2Win.

An internet connection is required to download the dependencies. If Python 3.10 is missing, follow the installation instructions displayed by the setup script.

### 4. Start Joy2WDance

Once setup finishes, run `Launcher_Portable.bat`.

### 5. Connect the controllers

When the Bridge console opens, select option `0` to use both Joy-Con controllers.

### 6. Open Melody

Wait for JoyDance to start. Melody should open automatically in your browser. If it does not, visit:

http://localhost:32623

## Important Notes

* Keep the Bridge and JoyDance console windows open while playing.
* Do not start Joy2Win separately while the Bridge is running.
* Install and configure vJoy before playing.
* Do not delete the `.venv` folder while using your existing setup. It contains the local Python environment.
* If setup fails, check the error displayed in the console before trying again.

## Credits

This project combines JoyDance and Joy2Win. Please refer to their original repositories and license files for their respective authors, acknowledgements, and licensing terms.
