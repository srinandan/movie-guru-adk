"""
Monkey patch for OpenTelemetry ContextVarsRuntimeContext.detach to handle context mismatch errors.
This works around "ValueError: <Token ...> was created in a different Context" when using async generators
with OpenTelemetry instrumentation.
"""
import logging

logger = logging.getLogger(__name__)

def patch_opentelemetry_context():
    """
    Monkey-patches ContextVarsRuntimeContext.detach to suppress "created in a different Context" errors.
    This is a workaround for an issue when using OpenTelemetry with async generators.
    """
    # Try importing the modern class name
    ContextVarsClass = None
    try:
        from opentelemetry.context.contextvars_context import ContextVarsRuntimeContext
        ContextVarsClass = ContextVarsRuntimeContext
    except ImportError:
        pass

    # Fallback to older class name if necessary
    if ContextVarsClass is None:
        try:
            from opentelemetry.context.contextvars_context import ContextVarsContext
            ContextVarsClass = ContextVarsContext
        except ImportError:
            pass

    if ContextVarsClass is None:
        logger.warning("Could not import ContextVarsRuntimeContext or ContextVarsContext, skipping OpenTelemetry patch.")
        return

    original_detach = ContextVarsClass.detach

    def safe_detach(self, token):
        try:
            original_detach(self, token)
        except ValueError as e:
            if "was created in a different Context" in str(e):
                logger.debug("Suppressing OpenTelemetry context detach error: %s", e)
            else:
                raise

    ContextVarsClass.detach = safe_detach
    logger.info(f"Patched OpenTelemetry {ContextVarsClass.__name__}.detach to handle async generator context issues.")

# Apply the patch immediately upon import
try:
    patch_opentelemetry_context()
except Exception as e:
    logger.warning(f"Failed to patch OpenTelemetry context: {e}")
