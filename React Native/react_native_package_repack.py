"""
React Native SDK Packaging and Installation Script

This script simplifies the development process of creating React Native SDKs.
It packs a React Native package, copies it to a sample app, installs the required
Node modules, and clears cache.

Usage:
    python script.py [-v] [-s] [-i PACKAGE_DIR] [-o APP_DIR]

Options:
    -v, --verbose    Verbose output, prints the entire build process.
    -s, --silent     Silent mode, suppresses most output.
    -i, --input      Specify the package directory.
    -o, --output     Specify the app directory.

Example:
    python script.py -v -i /path/to/custom/package -o /path/to/custom/app

Note:
    - The script cleans the SDK Android directory by removing temporary files.
    - It generates a timestamped package name and copies it to the app directory.
    - You can specify custom package and app directories using -i and -o options.

Author: scramjet911
"""

import os
import subprocess
import json
import time
import shutil
import argparse
import sys
import platform


config_file_path = ".rn_script_config.json"
config_package_key = "package_directory"
config_app_key = "sample_app_directory"

package_dir = ""
app_dir = ""


def print_description(output, text):
    output.write(f"{text}\n")


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print(f"File: {filename} doesn't exist")
    except TypeError as e:
        print(f"File: {filename} doesn't exist")


def get_filenames_from_user():
    global package_dir, app_dir

    print("Enter the paths to the package and sample app (starting from script directory, eg: 'react-native-package' or 'some/dir/path/package')")
    package_dir = input("Package directory: ")
    app_dir = input("Sample app directory: ")

    config = {
        config_package_key: package_dir,
        config_app_key: app_dir
    }

    with open(config_file_path, "w") as config_file:
        json.dump(config, config_file)


def get_saved_paths():
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            return json.load(config_file)
    else:
        return None


def get_gradle_file():
    if (platform.system() == "Windows"):
        return "gradlew.bat"
    else:
        return "./gradlew"


def parse_arguments():
    global package_dir, app_dir

    parser = argparse.ArgumentParser(
        description="Simplify the development process of making React Native SDKs.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output, prints the whole build process")
    parser.add_argument(
        "-s", "--silent", action="store_true", help="Silent mode")
    parser.add_argument("-i", "--input", dest="package_dir",
                        help="Package Directory")
    parser.add_argument("-o", "--output", dest="app_dir",
                        help="Sample App Directory")

    args = parser.parse_args()
    saved_paths = get_saved_paths()

    if args.package_dir or args.app_dir:
        # User provided paths as command line arguments
        updated_config = saved_paths.copy() if saved_paths else {}

        if args.package_dir:
            updated_config[config_package_key] = args.package_dir
        if args.app_dir:
            updated_config[config_app_key] = args.app_dir

        with open(config_file_path, "w") as config_file:
            json.dump(updated_config, config_file)

        print("Paths updated:")
        package_dir = updated_config.get(config_package_key)
        app_dir = updated_config.get(config_app_key)

    elif saved_paths:
        package_dir = saved_paths.get(config_package_key)
        app_dir = saved_paths.get(config_app_key)

        if package_dir is None or app_dir is None:
            get_filenames_from_user()

    else:
        get_filenames_from_user()

    print(f"Package Directory: {package_dir}")
    print(f"Sample App Directory: {app_dir}")

    return args


def main():
    global package_dir, app_dir

    args = parse_arguments()

    dir_path = os.getcwd()

    gradle = get_gradle_file()

    step_logging_dir = open(os.devnull, "w") if args.silent else sys.stdout
    verbose_logging_dir = open(os.devnull, "w")

    timestamp = int(time.time())
    new_package_name = f"ImageSDK-{timestamp}.tgz"

    with open(f"{package_dir}/package.json", "r") as package_json:
        package_json_data = json.load(package_json)
        react_native_package_name = f"{package_json_data['name']}-{package_json_data['version']}.tgz"

    if args.verbose:
        verbose_logging_dir = sys.stdout

    if args.package_dir:
        package_dir = args.package_dir
    if args.app_dir:
        app_dir = args.app_dir

    print_description(
        step_logging_dir, f"package_dir={package_dir}")
    print_description(
        step_logging_dir, f"app_dir={app_dir}\n")

    print_description(step_logging_dir, "Cleaning sdk Android directory")
    package_android_dir = os.path.join(package_dir, "android")

    shutil.rmtree(os.path.join(package_android_dir,
                  ".gradle"), ignore_errors=True)
    shutil.rmtree(os.path.join(package_dir,
                  "build"), ignore_errors=True)
    subprocess.run([gradle, "clean"], cwd=package_android_dir,
                   stdout=verbose_logging_dir)

    print_description(step_logging_dir, "Deleting old build files")
    shutil.rmtree(os.path.join(package_dir, "lib"),
                  ignore_errors=True)

    print_description(step_logging_dir, "Pre packing sdk")
    subprocess.run(["npm", "run", "prepack"], cwd=package_dir,
                   stdout=verbose_logging_dir)
    print_description(step_logging_dir, "Packing the sdk")
    subprocess.run(["npm", "pack"], cwd=package_dir, stdout=verbose_logging_dir,
                   stderr=verbose_logging_dir)

    print_description(step_logging_dir, "Copying the packed sdk\n")
    source_package_path = os.path.join(package_dir, react_native_package_name)
    dest_package_path = os.path.join(app_dir, new_package_name)
    shutil.copy(source_package_path, dest_package_path)
    print_description(step_logging_dir, "Removing the packed sdk\n")
    silent_remove(source_package_path)

    print_description(step_logging_dir,
                      "Updating package.json of the sample app\n")
    with open(f"{app_dir}/package.json", "r") as app_package_json:
        app_package_data = json.load(app_package_json)
        app_package_data["dependencies"]["detect-blur"] = new_package_name
    with open(f"{app_dir}/package.json", "w") as app_package_json:
        json.dump(app_package_data, app_package_json)

    print_description(
        step_logging_dir, "Deleting React Native node modules and dependency locks\n")
    shutil.rmtree(os.path.join(app_dir, "node_modules"), ignore_errors=True)
    silent_remove(os.path.join(app_dir, "package-lock.json"))

    print_description(step_logging_dir,
                      "Installing React Native node modules\n")
    subprocess.run(["npm", "i"], cwd=app_dir, stdout=verbose_logging_dir,
                   stderr=verbose_logging_dir)

    print_description(step_logging_dir, "Running gradle clean for Android")
    app_android_dir = os.path.join(app_dir, "android")
    shutil.rmtree(os.path.join(app_android_dir, ".gradle"), ignore_errors=True)
    shutil.rmtree(os.path.join(app_dir, "build"), ignore_errors=True)
    subprocess.run([gradle, "clean"], cwd=app_android_dir,
                   stdout=verbose_logging_dir)

    print_description(step_logging_dir, "Cleaning up installed SDK")
    silent_remove(dest_package_path)

    print_description(step_logging_dir, "Reverting package.json changes")
    subprocess.run(["git", "restore", "package.json"], cwd=app_dir,
                   stdout=verbose_logging_dir)


if __name__ == "__main__":
    main()

