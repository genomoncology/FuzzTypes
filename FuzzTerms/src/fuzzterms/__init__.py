__version__ = "0.2.0"

# logging
import logging

logger = logging.getLogger("fuzzterms")
logger.setLevel(logging.WARNING)

from . import const
from . import flags
from .entity import Entity
from .project import Project, Config
from . import db


__all__ = (
    "Config",
    "Entity",
    "Project",
    "const",
    "db",
    "flags",
    "logger",
)
