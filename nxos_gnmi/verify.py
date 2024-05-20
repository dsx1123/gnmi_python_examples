import os
import logging
from iac_validate.validator import Validator
from iac_validate.yaml import load_yaml_files

logger = logging.getLogger(__name__)


class FabricValidator:
    def __init__(self, schema_path: str, rules_path: str):
        self.schema = None
        self.Validator = Validator(schema_path, rules_path)

    def validate_syntax(self, root_path: str, env: str) -> tuple[bool, dict]:
        input_paths = []
        config_folder = os.path.join(root_path, "config")
        topo_folder = os.path.join(root_path, f"env/{env}")

        if not os.path.isdir(root_path):
            logger.error(f"invalid root path: {root_path}")
            return False, {}
        if not os.path.isdir(config_folder):
            logger.error(f"invalid config path: {config_folder}")
            return False, {}
        if not os.path.isdir(topo_folder):
            logger.error(f"invalid topology path: {topo_folder}")
            return False, {}

        for f in os.listdir(config_folder):
            _, file_extension = os.path.splitext(f)
            if ".yaml" != file_extension and ".yml" != file_extension:
                continue
            input_paths.append(os.path.join(config_folder, f))
        for f in os.listdir(topo_folder):
            _, file_extension = os.path.splitext(f)
            if ".yaml" != file_extension and ".yml" != file_extension:
                continue
            input_paths.append(os.path.join(topo_folder, f))

        err = self.Validator.validate_syntax(input_paths)
        if err:
            return not err, {}
        else:
            return not err, load_yaml_files(input_paths)
