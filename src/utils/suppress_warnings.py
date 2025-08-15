"""
Early warning suppression - import this FIRST before any other modules
"""

import os
import warnings

# Set environment variables for C-level warning suppression
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning,ignore::UserWarning"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Apply all warning filters
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

# Catch specific warnings we're seeing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Additional filters for the specific messages
warnings.filterwarnings("ignore", message=".*pkg_resources.*")
warnings.filterwarnings("ignore", message=".*declare_namespace.*")
warnings.filterwarnings("ignore", message=".*Pydantic.*")
warnings.filterwarnings("ignore", message=".*@validator.*")
warnings.filterwarnings("ignore", message=".*__fields__.*")
warnings.filterwarnings("ignore", message=".*schema.*method.*")
warnings.filterwarnings("ignore", message=".*config.*deprecated.*")

# Module-specific suppressions
warnings.filterwarnings("ignore", module="pkg_resources")
warnings.filterwarnings("ignore", module="crewai")
warnings.filterwarnings("ignore", module="pydantic")
warnings.filterwarnings("ignore", module="google")
