import glob
import tarfile
from pathlib import Path

from time import sleep

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import application.const
import docker


def start():
    list_of_instruments = []
    list_of_instruments.extend(application.const.all_instruments.keys())

    divide = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    list_of_list = divide(list_of_instruments, 3)

    docker_name = 'my-quotes-opt-3-frames'

    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    client_2 = docker.from_env()

    try:
        client_2.images.get(docker_name)
    except:
        print("please wait while docker images will be build")
        build_image = client.build(path="./", tag=docker_name)
        sleep(10)

    while checking_image(client_2, docker_name):
        print("waiting...")
        sleep(15)

    for list in list_of_list:
        port = 8090
        list_of_containers = []
        for instrument in list:
            container = client_2.containers.run(docker_name, detach=True, ports={'{}/tcp'.format(8080): port},
                                                volumes={'{}/test_stocks/stock/application/quotes.db'.format(str(Path.home())):
                                                             {'bind': '/quotes.db', 'mode': 'rw'}},
                                                environment=["INSTRUMENT={}".format(instrument)])
            list_of_containers.append(container)
            port = port + 1

        while check_container_is_running(list_of_containers, list):
            sleep(15)

    for file in glob.glob("./results/*.tar"):
        tar = tarfile.open(file, "r")
        tar.extractall("./results")

    for file in glob.glob("./logs/*.tar"):
        tar = tarfile.open(file, "r")
        tar.extractall("./logs")

    extract_tar("results")
    extract_tar("logs")

    merge_files("results")
    merge_files("logs")


def merge_files(path):
    with open('./{}/results.txt'.format(path), 'w') as outfile:
        for fname in glob.glob("./{}/*.txt".format(path)):
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line + "\n")


def extract_tar(path):
    for file in glob.glob("./{}/*.tar".format(path)):
        tar = tarfile.open(file, "r")
        tar.extractall("./{}".format(path))


def check_container_is_running(list_of_containers, list_of_instrument):
    for docker_container in list_of_containers:
        logs = docker_container.logs()
        if "optimisation done" in str(logs):
            for instrument in list_of_instrument:
                temp_inst = ''.join(e for e in instrument if e.isalnum())
                try:
                    bits, stat = docker_container.get_archive("{}.txt".format(temp_inst))
                    f = open('./results/{}.tar'.format(temp_inst), 'wb')
                    for chunk in bits:
                        f.write(chunk)
                    f.close()
                    bits, stat = docker_container.get_archive("{}_logs.txt".format(temp_inst))
                    f = open('./logs/{}_logs.tar'.format(temp_inst), 'wb')
                    for chunk in bits:
                        f.write(chunk)
                    f.close()
                    docker_container.stop()
                    docker_container.remove(force=True)
                    list_of_containers.remove(docker_container)
                    break
                except:
                    continue

    if len(list_of_containers) == 0:
        return False
    return True


def checking_image(client_2, docker_name):
    try:
        client_2.images.get(docker_name)
        return False
    except:
        return True


if __name__ == "__main__":
    start()