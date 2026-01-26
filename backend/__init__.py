# Backend package initialization

# Lazy import of models to avoid circular dependencies
def __getattr__(name):
    if name == 'models':
        from backend.shared.models import models
        return models
    if name == 'crud':
        import backend.crud as crud
        return crud
    if name == 'schemas':
        import backend.schemas as schemas
        return schemas
        
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
