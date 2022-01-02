import distutils.util
import os.path
import pathlib
import re
import sys
import requests
from tqdm import tqdm
import Logger

working_directory: pathlib.Path = pathlib.Path(sys.path[0])

if __name__ == "__main__":
    amount = len(sys.argv)
    if amount == 2:
        auto_update = distutils.util.strtobool(sys.argv[1]).__bool__()
    elif amount > 2:
        working_directory = pathlib.Path(sys.argv[1])
        Logger.debug_mode = distutils.util.strtobool(sys.argv[2]).__bool__()

    if not working_directory.is_dir():
        Logger.error(f"The supplied directory {sys.argv[1]} does not exist.")
        exit()

Logger.debug(working_directory)

jar_file = ""
pattern = re.compile(r"(purpur|paper)-([0-9]+(\.[0-9]+)+)-([0-9]+)\.jar")
for (dirpath, dirnames, filenames) in os.walk(working_directory):
    for filename in filenames:
        if not pattern.fullmatch(filename):
            continue
        jar_file = filename
        break

Logger.debug(jar_file)

regex_jar = pattern.match(jar_file)
fork = regex_jar.group(1)
mc_version = regex_jar.group(2)
version = int(regex_jar.group(4))
Logger.debug(f"Fork: {regex_jar.group(1)}")
Logger.debug(f"McVersion: {regex_jar.group(2)}")
Logger.debug(f"Version: {regex_jar.group(4)}")


def get_property(url: str, name: str):
    r = requests.get(url)
    if r.status_code != 200:
        print(f"There was an error while querying the url {url}")
        exit()
    return r.json()[name]


latest = None
latestVersion: int = 0
match regex_jar.group(1):
    case "purpur":
        fork_url = f"https://api.purpurmc.org/v2/purpur/{mc_version}/latest/"
        latestVersion = int(get_property(fork_url, "build"))
    case "paper":
        version_group = mc_version.split('.', 3)
        version_group = f"{version_group[0]}.{version_group[1]}"
        Logger.debug(version_group)
        fork_url = f"https://papermc.io/api/v2/projects/paper/version_group/{version_group}/builds"
        prop: list = get_property(fork_url, "builds")
        dict: dict = dict()
        i: int = 0
        for build in prop:
            dict[i] = build["build"]
            i = i + 1
        latestVersion = int(dict[max(dict)])


def download(url: str, file_name: str):
    resp = requests.get(url, stream = True)
    total = int(resp.headers.get('content-length', 0))
    with open(f"{working_directory.as_posix()}/{file_name}", 'wb') as file, tqdm(
        desc = file_name,
        total = total,
        unit = 'iB',
        unit_scale = True,
        unit_divisor = 1024,
    ) as bar:
        for data in resp.iter_content(chunk_size = 1024):
            size = file.write(data)
            bar.update(size)


if latestVersion > version:
    print(f"You are running {fork} version {version} for {mc_version}, the latest version is {latestVersion}.")
    update = distutils.util.strtobool(input("Would you like to update? [Y/N]")).__bool__()
    if update is True:
        url: str = ""
        match fork:
            case "purpur":
                url = f"https://api.purpurmc.org/v2/purpur/{mc_version}/{latestVersion}/download"
            case "paper":
                url = f"https://papermc.io/api/v2/projects/paper/versions/{mc_version}/builds/{latestVersion}/downloads/paper-{mc_version}-{latestVersion}.jar"

        file_name = f"{fork}-{mc_version}-{latestVersion}.jar"
        download(url, file_name)
        # r = requests.get(url)
        # meta = r.headers
        # file_size = int(meta.get("Content-Length")[0])
        # with open(file_name, 'wb') as file:
        #     print("Downloading: %s Bytes: %s" % (file_name, file_size))
        #     file_size_dl = 0
        #     block_sz = 8192
        #     while True:
        #         buffer = file.read(block_sz)
        #         if not buffer:
        #             break
        #         file_size_dl += len(buffer)
        #         file.write(buffer)
        #         status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        #         status = status + chr(8) * (len(status) + 1)
        #         print(status)
        #
        #     file.close()
