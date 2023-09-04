#!/bin/bash

# ---------------------------------------------------------------------------- #
#              This script is to simplify the development process              #
#              of making react native sdks. The steps we do is                 #
#              pack the package, add it to sample app, install                 #
#              the package in the sample app after node modules                #
#              are cleared so the cached version of app isn't used.            #
#              All are required to correctly clear the old files               #
#              and install the new package. If it still doesn't                #
#              work, you're on your own.... Goodluck!!                         #
# ---------------------------------------------------------------------------- #

# ----------------------------- Exit on any error ---------------------------- #
set -e

dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

# ------------------------ Standard output requirement ----------------------- #
bash_output_dir=/dev/stdout
build_output_dir=/dev/null

# -------------- Setting the directories, change this as needed -------------- #
react_native_package_dir="<package directory relative to script directory>"
react_native_app_dir="<app directory relative to script directory>"

# -------- New filename has timestamp so that old caches are not used -------- #
timestamp=$(date +%s)
new_package_name="RNPackage-$timestamp.tgz"

# -------------------------- NPM packed package name ------------------------- #
react_native_package_name="$(
  jq -r '.name' $dir/$react_native_package_dir/package.json
)-$(
  jq -r '.version' $dir/$react_native_package_dir/package.json
).tgz"

# -------------------- Function to print usage information ------------------- #
print_usage() {
  printf "\nUsage: $0 [-v] [-s] [-i package_directory] [-o app_directory] [-h]\n"
  printf "  -v: Verbose output, prints whole build process\n"
  printf "  -s: Silent\n"
  printf "  -i: Package Directory\n"
  printf "  -o: App Directory\n"
  printf "  -h: Print this help message.\n"
}

# ----------------------- Process command line options ----------------------- #
while getopts "h?vsi:o:" opt; do
  case $opt in
  v)
    build_output_dir=/dev/stdout
    ;;
  s)
    bash_output_dir=/dev/null
    OUTPUT_DIR=/dev/null
    ;;
  i | --input)
    react_native_package_dir=$OPTARG
    ;;
  o)
    react_native_app_dir=$OPTARG
    ;;
  h)
    print_usage
    exit 0
    ;;
  \?)
    printf "Invalid option: -$OPTARG" >&2
    print_usage
    exit 1
    ;;
  esac
done
printDescription() {
  printf "$1\n" >$bash_output_dir
}

# ---------------------------- Script starts here ---------------------------- #

printDescription "react_native_package_dir=$react_native_package_dir"
printDescription "react_native_app_dir=$react_native_app_dir\n"

cd $react_native_package_dir

printDescription "Cleaning sdk Android directory"
cd android
rm -rf $dir/$react_native_package_dir/android/.gradle
rm -rf $dir/$react_native_package_dir/build
$dir/$react_native_package_dir/android/gradlew clean >$build_output_dir
cd ..

printDescription "Deleting old build files"
rm -rf $dir/$react_native_package_dir/lib

printDescription "Pre packing sdk"
npm run prepack >$build_output_dir
printDescription "Packing the sdk"
npm pack >$build_output_dir 2>$build_output_dir

cd $dir

printDescription "Copying the packed sdk\n"
cp "$dir/$react_native_package_dir/$react_native_package_name" $dir/$react_native_app_dir/$new_package_name
printDescription "Removing the packed sdk\n"
rm "$dir/$react_native_package_dir/$react_native_package_name"

cd $react_native_app_dir

printDescription "Updating package.json of sample app\n"
new_package_json=$(
  jq --arg packname "$new_package_name" \
    '.dependencies."detect-blur" = $packname' $dir/$react_native_app_dir/package.json
)
printf "$new_package_json" >$dir/$react_native_app_dir/package.json

printDescription "Deleting react native node modules and dependency locks\n"
rm -rf $dir/$react_native_app_dir/node_modules
rm $dir/$react_native_app_dir/package-lock.json

printDescription "Installing react native node modules\n"
# -------------- Uncomment this line if cache issue still occurs ------------- #
# npm cache clean -f >$build_output_dir 2>$build_output_dir
npm i >$build_output_dir 2>$build_output_dir

printDescription "Running gradle clean for android"
cd android
rm -rf $dir/$react_native_app_dir/.gradle
rm -rf $dir/$react_native_app_dir/build
$dir/$react_native_app_dir/android/gradlew clean >$build_output_dir
cd ..

# ------------------------------- Cleanup Phase ------------------------------ #
printDescription "Cleaning up installed SDK"
rm $dir/$react_native_app_dir/$new_package_name

printDescription "Reverting package.json changes"
git restore $dir/$react_native_app_dir/package.json

cd $dir
