import os
from .parameterloader import ParameterLoader
from ..config import ExperimentContext


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
        result = super().load_parameters()
        # Make the script executable
        os.system(f"chmod +x {result}")
        return result

    def get_context(self):
        if self.experiment_context.simulation_context.gem5:
            raise NotImplementedError(
                "--gem5 is not supported for the timing simulation yet: "
                "run_flexus.sh uses vanilla QEMU, which has no id-overrides, "
                "so it cannot load snapshots taken with --gem5. "
                "Convert the snapshots to gem5 checkpoints instead.")
        return {
            # TODO add some check to make sure this core_count is not the doubled version as that is being sent in as a separate parameter
            "CORE_COUNT": self.experiment_context.simulation_context.core_count,
            "DOUBLED_VCPU": self.experiment_context.simulation_context.doubled_vcpu,
            "MEMORY": self.experiment_context.simulation_context.memory_gb * 1024,  # in MB
            "QEMU_NIC": self.experiment_context.simulation_context.qemu_nic.strip().lower(),
        }