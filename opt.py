import tarfile
from pathlib import Path

from StringIO import StringIO
from time import sleep

import application.const
import docker


def start():
    list_of_instruments = []
    list_of_instruments.extend(application.const.all_instruments.keys())

    divide = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    list_of_list = divide(list_of_instruments, 4)

    docker_name = 'my-quotes-test'

    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    client_2 = docker.from_env()

    try:
        client_2.images.get(docker_name)
    except:
        print("please wait while docker images will be build")
        client.build(path="./", tag=docker_name)

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
            sleep(1)


def check_container_is_running(list_of_containers, list_of_instrument):
    for docker_container in list_of_containers:
        if "optimisation done" in str(docker_container.logs()):
            for instrument in list_of_instrument:
                temp_inst = ''.join(e for e in instrument if e.isalnum())
                bits, stat = docker_container.get_archive("/my-quotes/application/{}.txt".format(temp_inst))
                for d in bits:
                    pw_tar = tarfile.TarFile(fileobj=StringIO(d.decode('utf-8')))
                    pw_tar.extractall()
            docker_container.stop()
            docker_container.remove(force=True)
            list_of_containers.remove(docker_container)
    if len(list_of_containers) == 0:
        return False
    return True


if __name__ == "__main__":
    start()