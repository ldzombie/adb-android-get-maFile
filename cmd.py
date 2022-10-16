import os
import subprocess
import shutil
import tarfile
from xml.dom import minidom
import json

name_backup_file = "val.ba"
name_tar_file = "valve.tar"
dir_ext_tarfile = "tar_file"
dir_mafiles = "maFiles/"

path_uuid = f"{dir_ext_tarfile}/apps/com.valvesoftware.android.steam.community/sp/steam.uuid.xml"
path_steam_guard = f"{dir_ext_tarfile}/apps/com.valvesoftware.android.steam.community/f/"

cmd_devices = "adb devices"
cmd_get_backup = f"adb backup -apk com.valvesoftware.android.steam.community -f {name_backup_file}"
cmd_ba_to_tar = f"java -jar abe.jar unpack {name_backup_file} {name_tar_file}"

uuid_key = None
steam_guard = None
name_mafile = None


# Проверка наличия java и adb
def check_dependency():
    if subprocess.call('adb version', creationflags=0x08000000):
        print("Adb not found")
        exit()
    if subprocess.call('java --version', creationflags=0x08000000):
        print("Java not found")
        exit()

    if not os.path.exists(dir_mafiles):
        os.mkdir(dir_mafiles)

    command()


# выполнение команд
def command():
    os.system(cmd_devices)
    if not os.path.exists(name_backup_file):
        os.system(cmd_get_backup)
    if os.path.getsize(name_backup_file) == 0:
        os.remove(name_backup_file)
        exit()

    if not os.path.exists(name_tar_file) and os.path.exists(name_backup_file):
        os.system(cmd_ba_to_tar)


def extract_file():
    try:
        if not os.path.exists(dir_ext_tarfile) and tarfile.is_tarfile(name_tar_file):
            with tarfile.open(name=name_tar_file, mode="r") as file:
                file.extractall(dir_ext_tarfile)
            print("Extract tar success")
    except Exception as e:
        print(e)


# Получение из данных uuid
def parse_files():
    global uuid_key
    global name_mafile
    try:
        uuid_doc = minidom.parse(path_uuid)
        uuid_key = uuid_doc.getElementsByTagName("string")[0].firstChild.data

        steam_guard_files = os.listdir(path_steam_guard)
        if (l := len(steam_guard_files)) > 1:
            print("--Select steam guard file---")
            for i in range(l):
                print(f"{i}. {steam_guard_files[i]}")
            inp = int(input())
            if inp <= l:
                steam_guard_file = steam_guard_files[inp]
            else:
                parse_files()
        else:
            steam_guard_file = steam_guard_files[0]

        name_mafile = f"{dir_mafiles}{steam_guard_file.split('-')[1]}.maFile"

        if not os.path.exists(name_mafile):
            open_steam_guard_file(steam_guard_file)
    except Exception as e:
        print(e)


def open_steam_guard_file(sg_file):
    global steam_guard
    try:
        with open(path_steam_guard+sg_file, "r") as file:
            sg_text = file.read()
        print(f"File {sg_file} read success")
        steam_guard = json.loads(sg_text)
        if steam_guard is not None:
            edit_steam_guard()
    except FileNotFoundError:
        print(f"File {sg_file} not found")
    except Exception as e:
        print(e)


def edit_steam_guard():
    global steam_guard
    steam_guard["status"] = "1"
    steam_guard["device_id"] = uuid_key
    steam_guard["fully_enrolled"] = "true"
    dictionary = {"SessionID": "",
                  "SteamLogin": "",
                  "SteamLoginSecure": "",
                  "WebCookie": "",
                  "OAuthToken": "",
                  "SteamID": steam_guard['steamid']}
    steam_guard["Session"] = dictionary

    steam_guard.pop("steamguard_scheme")
    steam_guard.pop("steamid")

    save_mafile()


def save_mafile():
    global steam_guard
    global name_mafile
    try:
        with open(name_mafile, "w") as file:
            file.write(str(steam_guard))
        print(f"File {name_mafile.split('/')[1]} create success!")
        clean_files()
    except Exception as e:
        print(f"File create FAIL!\n {e}")


def clean_files():
    imp = input("Delete files created during work?(y/n): ")
    match imp:
        case "y":
            if os.path.exists(dir_ext_tarfile):
                shutil.rmtree(dir_ext_tarfile)
            if os.path.exists(name_backup_file):
                os.remove(name_backup_file)
            if os.path.exists(name_tar_file):
                os.remove(name_tar_file)
        case _:
            print("END")


def main():
    check_dependency()
    extract_file()
    parse_files()



if __name__ == "__main__":
    main()


