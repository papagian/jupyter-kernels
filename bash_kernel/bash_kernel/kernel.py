from ipykernel.kernelbase import Kernel

from contextlib import closing

import docker
import logging
import re

def _recvall(sock, buff_size=4096, timeout=5):
    sock.settimeout(timeout)
    data = b''
    while True:
        try:
            part = sock.recv(buff_size)
        except:
            logging.exception('message')
            break
        else:
            data += part
    return data

class BashKernel(Kernel):
    implementation = 'Bash'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Shell script',
        'mimetype': 'text/x-shellscript',
        'file_extension': '.sh',
    }
    banner = "Bash kernel running inside a docker container - as useful as a parrot"
    image = 'bash:latest'
    command="bash"
    runtime = 'runc'
    environment = None
    network = None

    def _strip_image(self):
        # thanks to: https://stackoverflow.com/questions/39671641/regex-to-parse-docker-tag#answer-39672069
        pattern = '^(?P<repo>(?:(?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*))(?::(?P<tag>(?![.-])[a-zA-Z0-9_.-]{1,128}))?$'
        repo, _, tag = re.match(pattern, self.image).groups()
        if tag is None:
            tag = 'latest'
        return repo, tag

    def start(self):
        self.client = docker.APIClient(
            base_url='unix://var/run/docker.sock')
        self.client.pull(*self._strip_image())
        if self.network is not None:
            networking_config = self.client.create_networking_config({
                self.network: self.client.create_endpoint_config()
            })
        else:
            networking_config = None
        self.container = self.client.create_container(
            image=self.image,
            command=self.command,
            runtime=self.runtime,
            stdin_open=True,
            tty=True,
            networking_config=networking_config,
            environment=self.environment,
        )
        self.client.start(self.container)
        super(BashKernel, self).start()

    def do_shutdown(self, restart):
        self.client.stop(self.container['Id'])
        self.client.remove_container(self.container['Id'],
                                     v=True,
                                     force=True,)
        super(BashKernel, self).do_shutdown(restart)

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            stream_content = {'name': 'stdout'}
            try:
                cmd = f'{code}\n'.encode('utf-8')
                with closing(self.client.attach_socket(
                    self.container, params={'stdin': 1, 'stream': 1})) as _in:
                    with closing(self.client.attach_socket(
                        self.container, params={'stdout': 1, 'stream': 1})) as _out:
                        _in._sock.send(cmd)
                        output = _recvall(_out._sock)
            except Exception as e:
                logging.debug('>>>> 1')
                logging.exception('message')
                msg = (f'{self.image}: '
                       f'{self.container["Id"]}: {str(e)}')
                stream_content = {'name': 'stderr',
                                  'text': msg}
                status = 'error'
            else:
                logging.debug('>>>> 2')
                msg = (f'{self.image}: '
                       f'{self.container["Id"]}# '
                       f'{output.decode("utf-8")}')
                stream_content = {'name': 'stdout',
                                  'text': msg }
                status = 'ok'
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': status,
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
