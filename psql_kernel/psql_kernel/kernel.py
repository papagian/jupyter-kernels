from bash_kernel.kernel import BashKernel

class PsqlKernel(BashKernel):
    implementation = 'Psql'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'PostgrSQL script',
        'mimetype': 'application/sql',
        'file_extension': '.sql',
    }
    banner = "Psql kernel running inside a docker container - as useful as a parrot"
    image = 'postgres'
    command='psql -h some-postgres -U postgres'
    environment = {'PGPASSWORD': 'mysecretpassword'}
    network = 'some-network'
