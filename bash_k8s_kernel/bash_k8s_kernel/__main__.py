from ipykernel.kernelapp import IPKernelApp
from . import BashK8sKernel

IPKernelApp.launch_instance(kernel_class=BashK8sKernel)
