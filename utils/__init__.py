"""
Package initialization exposing high-level data aggregation and plotting utilities.
"""

from .plotting_culture import plot_publication_trajectories
from .compare_models import execute_model_comparison

__all__ = ["plot_publication_trajectories", "execute_model_comparison"]
