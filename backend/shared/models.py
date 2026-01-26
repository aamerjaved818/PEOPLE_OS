import importlib
from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models
from backend.domains.gen_admin import models as gen_admin_models

class ModelsProxy:
    """
    Standard proxy to maintain 'models.DB...' compatibility across the project.
    Resolves model names by searching through domain-specific modules.
    """
    def __getattr__(self, name):
        if hasattr(core_models, name):
            return getattr(core_models, name)
        if hasattr(hcm_models, name):
            return getattr(hcm_models, name)
        if hasattr(gen_admin_models, name):
            return getattr(gen_admin_models, name)
        
        # Fallback to dynamic loading if not pre-imported (rare case)
        for module_path in ["backend.domains.core.models", "backend.domains.hcm.models", "backend.domains.gen_admin.models"]:
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, name):
                    return getattr(mod, name)
            except ImportError:
                continue
                
        raise AttributeError(f"Model '{name}' not found in Core or HCM domains")

# Global instance for shared use
models = ModelsProxy()
