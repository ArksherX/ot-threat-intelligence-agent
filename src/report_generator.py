"""
Phase 3: Report Generator
Generates structured JSON reports of OT threats
"""

import json
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def get_severity(self, cvss_score):
        """
        Convert CVSS score to severity level
        
        Args:
            cvss_score: Numeric CVSS score (0-10)
            
        Returns:
            Severity level string
        """
        if cvss_score >= 9.0:
            return "CRITICAL"
        elif cvss_score >= 7.0:
            return "HIGH"
        elif cvss_score >= 4.0:
            return "MEDIUM"
        elif cvss_score > 0:
            return "LOW"
        else:
            return "NONE"
    
    def get_severity_stats(self, threats):
        """Calculate severity statistics"""
        stats = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for threat in threats:
            severity = threat.get('severity', 'NONE').lower()
            if severity in stats:
                stats[severity] += 1
        
        return stats
    
    def generate_report(self, ot_cves, include_stats=True):
        """
        Generate structured JSON report
        
        Args:
            ot_cves: List of OT-relevant CVEs with AI insights
            include_stats: Whether to include statistical summary
            
        Returns:
            Dictionary containing the report
        """
        report = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'report_version': '1.0',
            'total_threats': len(ot_cves),
            'threats': []
        }
        
        # Sort by CVSS score (highest first)
        sorted_cves = sorted(ot_cves, key=lambda x: x.get('cvss_score', 0), reverse=True)
        
        for cve in sorted_cves:
            threat = {
                'cve_id': cve['cve_id'],
                'cvss_score': cve.get('cvss_score', 0.0),
                'severity': self.get_severity(cve.get('cvss_score', 0.0)),
                'description': cve['description'],
                'ai_insight': cve.get('ai_insight', 'No insight generated'),
                'published_date': cve.get('published_date', 'Unknown'),
                'last_modified': cve.get('last_modified', 'Unknown'),
                'references': cve.get('references', [])
            }
            report['threats'].append(threat)
        
        # Add statistics
        if include_stats:
            stats = self.get_severity_stats(report['threats'])
            report['severity_breakdown'] = stats
        
        logger.info(f"Report generated with {report['total_threats']} threats")
        return report
    
    def save_report(self, report, filename="output_sample.json"):
        """
        Save report to JSON file
        
        Args:
            report: Report dictionary
            filename: Output filename
            
        Returns:
            Full filepath of saved report
        """
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report saved to {filepath}")
            logger.info(f"Total threats: {report['total_threats']}")
            
            if 'severity_breakdown' in report:
                stats = report['severity_breakdown']
                logger.info(f"Severity breakdown - Critical: {stats['critical']}, " +
                          f"High: {stats['high']}, Medium: {stats['medium']}, Low: {stats['low']}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
    
    def load_report(self, filename="output_sample.json"):
        """
        Load existing report from file
        
        Args:
            filename: Report filename to load
            
        Returns:
            Report dictionary or None
        """
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Report file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                report = json.load(f)
            logger.info(f"Report loaded from {filepath}")
            return report
        except Exception as e:
            logger.error(f"Error loading report: {e}")
            return None
    
    def generate_summary_report(self, report):
        """
        Generate a human-readable summary of the report
        
        Args:
            report: Report dictionary
            
        Returns:
            Formatted summary string
        """
        summary = []
        summary.append("="*70)
        summary.append("OT THREAT INTELLIGENCE REPORT")
        summary.append("="*70)
        summary.append(f"Generated: {report['generated_at']}")
        summary.append(f"Total Threats: {report['total_threats']}")
        
        if 'severity_breakdown' in report:
            stats = report['severity_breakdown']
            summary.append("\nSEVERITY BREAKDOWN:")
            summary.append(f"  Critical: {stats['critical']}")
            summary.append(f"  High:     {stats['high']}")
            summary.append(f"  Medium:   {stats['medium']}")
            summary.append(f"  Low:      {stats['low']}")
        
        summary.append("\n" + "="*70)
        summary.append("THREAT DETAILS")
        summary.append("="*70)
        
        for idx, threat in enumerate(report['threats'], 1):
            summary.append(f"\n[{idx}] {threat['cve_id']} - {threat['severity']}")
            summary.append(f"    CVSS Score: {threat['cvss_score']}")
            summary.append(f"    Published: {threat['published_date'][:10]}")
            summary.append(f"    Description: {threat['description'][:150]}...")
            summary.append(f"    Impact: {threat['ai_insight'][:200]}...")
        
        summary.append("\n" + "="*70)
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test the report generator
    generator = ReportGenerator()
    
    # Sample OT CVEs
    test_cves = [
        {
            'cve_id': 'CVE-2026-12345',
            'cvss_score': 9.8,
            'description': 'A critical vulnerability in Siemens SIMATIC S7-1200 PLC allows remote code execution through the Profinet protocol.',
            'ai_insight': 'This vulnerability poses severe risk to manufacturing facilities. Attackers could gain complete control of production line controllers, potentially causing equipment damage, production shutdowns, or safety incidents.',
            'published_date': '2026-01-26T08:15:00.000',
            'last_modified': '2026-01-26T08:15:00.000',
            'references': ['https://example.com/advisory']
        },
        {
            'cve_id': 'CVE-2026-67890',
            'cvss_score': 7.5,
            'description': 'Authentication bypass in Rockwell Automation FactoryTalk View HMI software.',
            'ai_insight': 'This HMI vulnerability could allow unauthorized operators to access and manipulate critical process controls, risking both production integrity and worker safety.',
            'published_date': '2026-01-26T09:45:00.000',
            'last_modified': '2026-01-26T09:45:00.000',
            'references': []
        }
    ]
    
    # Generate and save report
    report = generator.generate_report(test_cves)
    filepath = generator.save_report(report)
    
    # Generate summary
    print("\n" + generator.generate_summary_report(report))
