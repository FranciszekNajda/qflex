import os
from commands.config import ExperimentContext
from commands import gem5_profile

class QemuCommonArgParser:
    def __init__(self, experiment_context: ExperimentContext, is_boot: bool = False):
        self.experiment_context = experiment_context
        self.simulation_context = self.experiment_context.simulation_context
        self.image_address = self.experiment_context.get_local_image_address()
        self.memory_size_mb = self.experiment_context.simulation_context.memory_gb * 1024
        self.cores = self.experiment_context.simulation_context.core_count
        self.double_cores = self.experiment_context.simulation_context.doubled_vcpu
        self.cpu_model = self.experiment_context.simulation_context.cpu_model
        self.core_coeff = 1
        if self.double_cores:
            self.core_coeff = 2

        
        
        self.nic_command = self.experiment_context.simulation_context.qemu_nic.strip().lower()

        self.loadvm = ''
        if self.experiment_context.loadvm_name is not None and len(self.experiment_context.loadvm_name) > 0:
            self.loadvm = f'-loadvm {self.experiment_context.loadvm_name}'
    
        check_period_quantum_coeff = self.simulation_context.check_period_quantum_coeff
        self.quantum_command = ''
        # TODO check why 53 : checked this is a check done to see whether or not we need to do checkpointing, with the assumption being it will usually be way less than the sampling interval
        if self.simulation_context.is_parallel:
            self.quantum_command = f'   -quantum size={self.simulation_context.quantum_size},check_period={int(self.simulation_context.quantum_size * check_period_quantum_coeff)} '
        else:
            self.quantum_command = f'   -icount shift=0,align=off,sleep=off,q={self.simulation_context.quantum_size},check_period={int(self.simulation_context.quantum_size * check_period_quantum_coeff)} '

        self.cd_rom = ''
        self.use_cd_rom = self.simulation_context.use_cd_rom
        if self.use_cd_rom:
            alpine_image_name = 'alpine-virt-3.22.1-aarch64.iso'
            experiment_folder = self.experiment_context.get_experiment_folder_address()
            if not os.path.isfile(f'{experiment_folder}/images/{alpine_image_name}'):
                alpine_url = f'https://dl-cdn.alpinelinux.org/alpine/v3.22/releases/aarch64/{alpine_image_name}'
                os.system(f'wget {alpine_url} -O {experiment_folder}/images/{alpine_image_name}')
            self.cd_rom = f'-cdrom {experiment_folder}/images/{alpine_image_name} '

        # QEMU options constrained by --gem5 (commands/gem5_profile.py).
        # Without --gem5, these are the original values.
        self.gem5 = self.simulation_context.gem5
        self.machine = gem5_profile.machine_args(
            self.gem5, "virt,gic-version=max,virtualization=off,secure=off")
        self.disk_command = (
            f"-drive {gem5_profile.disk_interface(self.gem5)},"
            f"file={self.image_address},format=qcow2 "
            f"{gem5_profile.disk_device(self.gem5)}")
        gem5_profile.check_marker(self.gem5, self.image_address, is_boot)
        


        
    def get_qemu_base_args(self) -> str:

        qemu_args = f""" -M {self.machine} \
        -smp {self.core_coeff * self.cores} \
        -cpu {self.cpu_model} -m {self.memory_size_mb} \
        -boot order=d,menu=on \
        -bios ./QEMU_EFI.fd \
        {self.disk_command} \
        {self.nic_command} \
        -rtc clock=vm \
        {self.loadvm} \
        {self.cd_rom} \
        -nographic -no-reboot"""
        print("="*50+"QEMU command arguments:"+"="*50)
        print(qemu_args)
        return qemu_args

    def quantum_args(self) -> str:
        print("="*50+"Quantum command arguments:"+"="*50)
        print(self.quantum_command)
        return self.quantum_command
 

    






