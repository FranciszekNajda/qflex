import os
from .parameterloader import ParameterLoader
from ..config import ExperimentContext

# Message of the run_flexus.sh generated with --gem5 (see load_parameters).
GEM5_TIMING_ERROR = (
    "--gem5 is not supported for the timing simulation yet: run_flexus.sh "
    "uses vanilla QEMU, which has no id-overrides, so it cannot load "
    "snapshots taken with --gem5. Convert the snapshots to gem5 "
    "checkpoints instead.")


class FlexusScriptLoader(ParameterLoader):
    def __init__(self,
                    experiment_context: ExperimentContext):
            super().__init__(
                experiment_context=experiment_context,
                parameter_template='run_flexus.sh.j2',
                output_name='run_flexus.sh',
                out_folder='scripts'
            )
    
    def load_parameters(self) -> str:
        # run_flexus.sh is generated early (e.g. by init_warm) and run later
        # by the timing steps. With --gem5, generate a script that refuses
        # to run, so that only the timing simulation is blocked.
        if self.experiment_context.simulation_context.gem5:
            return self._write_gem5_stub()
        result = super().load_parameters()
        # Make the script executable
        os.system(f"chmod +x {result}")
        return result

    def _write_gem5_stub(self) -> str:
        path = (f"{self.experiment_context.get_experiment_folder_address()}"
                f"/{self.folder}/{self.output_name}")
        with open(path, "w") as f:
            f.write("#!/bin/bash\n"
                    "# Generated with --gem5 (see flexus_script_loader.py).\n"
                    f"echo 'ERROR: {GEM5_TIMING_ERROR}' >&2\n"
                    "exit 1\n")
        os.system(f"chmod +x {path}")
        return path

    def get_context(self):
        return {
            # TODO add some check to make sure this core_count is not the doubled version as that is being sent in as a separate parameter
            "CORE_COUNT": self.experiment_context.simulation_context.core_count,
            "DOUBLED_VCPU": self.experiment_context.simulation_context.doubled_vcpu,
            "MEMORY": self.experiment_context.simulation_context.memory_gb * 1024,  # in MB
            "QEMU_NIC": self.experiment_context.simulation_context.qemu_nic.strip().lower(),
        }