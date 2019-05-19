from ipykernel.kernelapp import IPKernelApp
from . import PsqlKernel

IPKernelApp.launch_instance(kernel_class=PsqlKernel)
