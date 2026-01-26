"""
Main entry point for OT Threat Intelligence Agent
Orchestrates the complete pipeline: Fetch → Filter → Report
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import schedule

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_pipeline import CVEPipeline
from ai_agent import OTAgent
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ThreatIntelligenceAgent:
    """Main orchestrator for the OT Threat Intelligence Agent"""
    
    def __init__(self, nvd_api_key, qwen_model="qwen2.5:latest"):
        logger.info("Initializing OT Threat Intelligence Agent...")
        
        self.pipeline = CVEPipeline(nvd_api_key)
        self.ai_agent = OTAgent(model_name=qwen_model)
        self.report_gen = ReportGenerator()
        
        logger.info("Agent initialized successfully")
    
    def run_once(self, use_fallback=False):
        """
        Execute one complete cycle of the agent
        
        Args:
            use_fallback: If True, fetch CVEs from last 2 days (for testing)
        """
        logger.info("="*70)
        logger.info("Starting agent cycle...")
        logger.info("="*70)
        
        try:
            # Phase 1: Fetch CVEs
            logger.info("\n[PHASE 1] Fetching latest CVEs from NVD...")
            
            if use_fallback:
                cves = self.pipeline.fetch_recent_cves_fallback(days=2)
            else:
                cves = self.pipeline.fetch_latest_cves(minutes_ago=10)
            
            if not cves:
                logger.warning("No new CVEs found in this cycle")
                return
            
            logger.info(f"Fetched {len(cves)} new CVEs")
            
            # Phase 2: AI Filtering
            logger.info("\n[PHASE 2] Filtering for OT/ICS relevance using Qwen AI...")
            ot_cves = self.ai_agent.filter_cves(cves)
            
            if not ot_cves:
                logger.info("No OT-relevant threats detected")
                return
            
            logger.info(f"Identified {len(ot_cves)} OT-relevant threats")
            
            # Phase 3: Generate Report
            logger.info("\n[PHASE 3] Generating threat intelligence report...")
            report = self.report_gen.generate_report(ot_cves)
            
            # Save report
            filepath = self.report_gen.save_report(report, "output_sample.json")
            
            # Print summary
            logger.info("\n" + "="*70)
            logger.info("CYCLE COMPLETE")
            logger.info("="*70)
            logger.info(f"Total OT Threats: {len(ot_cves)}")
            logger.info(f"Report saved to: {filepath}")
            
            if 'severity_breakdown' in report:
                stats = report['severity_breakdown']
                logger.info(f"Critical: {stats['critical']}, High: {stats['high']}, " +
                          f"Medium: {stats['medium']}, Low: {stats['low']}")
            
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"Error in agent cycle: {e}", exc_info=True)
    
    def run_continuous(self, interval_minutes=10):
        """
        Run agent continuously at specified intervals
        
        Args:
            interval_minutes: Minutes between each check
        """
        logger.info(f"Starting continuous monitoring (every {interval_minutes} minutes)")
        logger.info("Press Ctrl+C to stop")
        
        # Run immediately
        self.run_once()
        
        # Schedule periodic runs
        schedule.every(interval_minutes).minutes.do(self.run_once)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nAgent stopped by user")


def main():
    """Main entry point with CLI arguments"""
    parser = argparse.ArgumentParser(
        description="OT Threat Intelligence Agent - Automated CVE monitoring for ICS/OT"
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously (default: run once)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Interval in minutes for continuous mode (default: 10)'
    )
    
    parser.add_argument(
        '--fallback',
        action='store_true',
        help='Use fallback mode to fetch CVEs from last 2 days (for testing)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='qwen2.5:latest',
        help='Qwen model to use (default: qwen2.5:latest)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Get API key
    nvd_api_key = os.getenv('NVD_API_KEY')
    if not nvd_api_key:
        logger.warning("NVD_API_KEY not found in environment. API rate limits will apply.")
        logger.warning("Get a free API key at: https://nvd.nist.gov/developers/request-an-api-key")
        response = input("Continue without API key? (y/n): ")
        if response.lower() != 'y':
            logger.info("Exiting. Please set NVD_API_KEY in .env file")
            return
    
    # Initialize agent
    agent = ThreatIntelligenceAgent(nvd_api_key, qwen_model=args.model)
    
    # Run agent
    if args.continuous:
        agent.run_continuous(interval_minutes=args.interval)
    else:
        agent.run_once(use_fallback=args.fallback)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          OT THREAT INTELLIGENCE AGENT v1.0                    ║
    ║          Automated CVE Monitoring for ICS/OT                  ║
    ║                                                               ║
    ║          Powered by NVD API + Qwen AI                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    main()
