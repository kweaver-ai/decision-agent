"""Unit test configuration - mock missing external dependencies"""
import sys
from unittest.mock import MagicMock, Mock


class DolphinModuleFinder:
    """A custom module finder that creates mock modules for dolphin.* imports"""
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("dolphin.") or fullname == "dolphin" or fullname == "limiter":
            # Create a mock spec for the module
            from importlib.machinery import ModuleSpec
            mock_module = MagicMock(name=fullname)
            mock_module.__name__ = fullname
            mock_module.__package__ = fullname.rsplit('.', 1)[0] if '.' in fullname else fullname
            mock_module.__path__ = []  # Make it a package

            spec = ModuleSpec(fullname, self, origin="mock")
            spec.loader = self
            return spec
        return None

    def create_module(self, spec):
        mock_module = MagicMock(name=spec.name)
        mock_module.__name__ = spec.name
        mock_module.__package__ = spec.name.rsplit('.', 1)[0] if '.' in spec.name else spec.name
        mock_module.__path__ = []

        # Special handling for VarOutput.is_serialized_dict to return False
        if spec.name == "dolphin.core.context.var_output":
            mock_var_output = MagicMock()
            mock_var_output.is_serialized_dict = Mock(return_value=False)
            mock_module.VarOutput = mock_var_output

        # Special handling for ResumeHandle class
        if spec.name == "dolphin.core.coroutine.resume_handle":
            # Create a real class that mimics ResumeHandle
            class MockResumeHandle:
                def __init__(self, frame_id, snapshot_id, resume_token, interrupt_type, current_block, restart_block):
                    self.frame_id = frame_id
                    self.snapshot_id = snapshot_id
                    self.resume_token = resume_token
                    self.interrupt_type = interrupt_type
                    self.current_block = current_block
                    self.restart_block = restart_block
            mock_module.ResumeHandle = MockResumeHandle

        return mock_module

    def exec_module(self, module):
        pass


# Install the custom finder
sys.meta_path.insert(0, DolphinModuleFinder())
