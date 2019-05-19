from ipykernel.kernelapp import IPKernelApp
from . import BashKernel

IPKernelApp.launch_instance(kernel_class=BashKernel)
