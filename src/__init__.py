"""
OT Threat Intelligence Agent
Automated CVE monitoring for Industrial Control Systems (ICS) and Operational Technology (OT)

Modules:
    - data_pipeline: CVE fetching from NVD API
    - ai_agent: AI-powered OT/ICS filtering using Qwen LLM
    - report_generator: Structured JSON report generation
    - dashboard: Streamlit web interface

Author: Your Name
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Miracle Owolabi"

from .data_pipeline import CVEPipeline
from .ai_agent import OTAgent
from .report_generator import ReportGenerator

__all__ = ['CVEPipeline', 'OTAgent', 'ReportGenerator']
