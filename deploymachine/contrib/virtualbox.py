from fabric.api import local
from fabric.decorators import task


@task
def create_vm(name):
    """
    Create a fresh ubuntu vm.
    Usage:
        fab create_vm:name=my_vm

    Assumes you already have downloaded a blank local image.
    Use vagrant?
    http://vagrantup.com/docs/getting-started/index.html
    """
    local("VBoxManage clonevdi lucid-server.vdi %s.vdi" % name)
    local("VBoxManage createvm --name '%s' --ostype 'Ubuntu_64'  --register" % name)
    local("VBoxManage modifyvm %s --memory 256 --acpi on --boot1 dvd --boot2 disk --boot3 none --boot4 none --nic1 nat --pae on" % name)
    local("VBoxManage storagectl %s --name 'IDE Controller' --add ide" % name)
    local("VBoxManage storageattach %s --storagectl 'IDE Controller' --port 0 --device 0 --type hdd --medium %s.vdi" % (name, name))
