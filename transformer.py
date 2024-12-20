import re
import yaml
import logging

class Transformer:
    def __init__(self, host_site_rules_path, host_tenant_rules_path, vm_role_rules_path, vm_tenant_rules_path, skip_rules_path):
        """
        Initialize the Transformer with paths to regex rules for site and tenant mappings.
        """
        self.host_site_rules = self._load_rules(host_site_rules_path)
        self.host_tenant_rules = self._load_rules(host_tenant_rules_path)
        self.vm_tenant_rules = self._load_rules(vm_tenant_rules_path)
        self.vm_role_rules = self._load_rules(vm_role_rules_path)
        self.skip_vm_rules = self._load_rules(skip_rules_path)

    def _load_rules(self, path):
        """
        Load regex rules from a YAML or JSON file.
        """
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load rules from {path}: {e}")
            exit(1)

    def apply_regex_replacements(self, value, rules):
        for rule in rules:
            # Validate rule structure
            if len(rule) != 2:
                logging.error(f"Malformed rule: {rule}")
                continue

            pattern, replacement = rule
            if re.match(pattern, value, flags=re.IGNORECASE):
                return re.sub(pattern, replacement, value, flags=re.IGNORECASE)

        return value

    def should_skip_vm(self, vm_name):
        """
        Determines if a VM should be skipped based on the skip rules.
        """
        for pattern in self.skip_vm_rules:
            if re.match(pattern, vm_name, flags=re.IGNORECASE):
                logging.info(f"Skipping VM: {vm_name} (matched pattern: {pattern})")
                return True
        return False
    
    def host_to_site(self, name):
        """
        Transform a host's cluster name to its site name.
        """
        return self.apply_regex_replacements(name, self.host_site_rules)

    def host_to_tenant(self, name):
        """
        Transform a host's name to its tenant.
        """
        return self.apply_regex_replacements(name, self.host_tenant_rules)

    def vm_to_tenant(self, name):
        """
        Transform a VM's name to its tenant.
        """
        return self.apply_regex_replacements(name, self.vm_tenant_rules)
    
    def vm_to_role(self, name):
        """
        Transform a VM's name to its tenant.
        """
        return self.apply_regex_replacements(name, self.vm_role_rules)

    def clean_name(self, name):
        """
        Remove '.clemson.edu.*' from a hostname or VM name.
        """
        return re.sub(r'\.clemson\.edu.*', '', name, flags=re.IGNORECASE)
