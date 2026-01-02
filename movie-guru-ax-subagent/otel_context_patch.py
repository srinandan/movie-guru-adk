"""
Monkey patch for OpenTelemetry ContextVarsContext.detach to handle context mismatch errors.
This works around "ValueError: <Token ...> was created in a different Context" when using async generators
with OpenTelemetry instrumentation.
"""
import logging

logger = logging.getLogger(__name__)

def patch_opentelemetry_context():
    """
    Monkey-patches ContextVarsContext.detach to suppress "created in a different Context" errors.
    This is a workaround for an issue when using OpenTelemetry with async generators.
    """
    try:
        from opentelemetry.context.contextvars_context import ContextVarsContext
    except ImportError:
        logger.warning("Could not import ContextVarsContext, skipping OpenTelemetry patch.")
        return

    original_detach = ContextVarsContext.detach

    def safe_detach(self, token):
        try:
            original_detach(self, token)
        except ValueError as e:
            if "was created in a different Context" in str(e):
                logger.debug("Suppressing OpenTelemetry context detach error: %s", e)
            else:
                raise

    ContextVarsContext.detach = safe_detach
    logger.info("Patched OpenTelemetry ContextVarsContext.detach to handle async generator context issues.")

# Apply the patch immediately upon import
try:
    patch_opentelemetry_context()
except Exception as e:
    logger.warning(f"Failed to patch OpenTelemetry context: {e}")
