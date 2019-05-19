from ipykernel.kernelbase import Kernel

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

import logging
import time
import uuid


def _recvall(resp, timeout):
    data = ''
    while True:
        line = resp.readline_stdout(timeout)
        if line is None:
            break
        data += line + '\n'
    return data

class BashK8sKernel(Kernel):
    implementation = 'Kubernetes'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Shell script',
        'mimetype': 'text/x-shellscript',
        'file_extension': '.sh',
    }
    banner = "Kubernetes pod bash kernel - as useful as a parrot"
    image = 'bash'
    command = ["bash"]
    gpus = 0 # If it is greater than zero requires nvidia runtime as default
    request_timeout = 120

    @property
    def pod_manifest(self):
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': self.name,
            },
            'spec': {
                'containers': [{
                    'image': self.image,
                    'name': self.name,
                    'args': self.command,
                    'stdin': True,
                    'tty': True,
                    'resources': {
                        'limits': {
                            'nvidia.com/gpu': self.gpus,
                        },
                    } 
                }]
            },
        }
    
    def _create_pod(self):
        config.load_kube_config()
        c = Configuration()
        c.assert_hostname = False
        Configuration.set_default(c)
        self.api = core_v1_api.CoreV1Api()
        resp = self.api.create_namespaced_pod(
            body=self.pod_manifest,
            namespace='default')
        # Loop until pod is created
        while True:
            #TODO timeout
            resp = self.api.read_namespaced_pod(
                name=self.name,
                namespace='default')
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        self.container = resp.spec.containers[0]
        
    def start(self):
        self.name = f'{self.image}-{uuid.uuid1()}'
        self._create_pod()
        self.resp = stream(self.api.connect_get_namespaced_pod_attach,
                           self.name,
                           'default',
                           stderr=True,
                           stdin=True,
                           stdout=True,
                           tty=True,
                           _preload_content=False,
                          )
        super(BashK8sKernel, self).start()

    def do_shutdown(self, restart):
        self.api.delete_namespaced_pod(
            name=self.name,
            namespace="default",
        )
        super(BashK8sKernel, self).do_shutdown(restart)

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            stream_content = {'name': 'stdout'}
            try:
                self.resp.write_stdin(f'{code}\n')
                output = _recvall(self.resp, timeout=2)
            except Exception as e:
                logging.exception('message')
                msg = (f'{self.container.image}: '
                       f'{self.container.name}: {str(e)}')
                stream_content = {'name': 'stderr',
                                  'text': msg}
                status = 'error'
            else:
                msg = (f'{self.container.image}: '
                       f'{self.container.name}# '
                       f'{output}')
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
