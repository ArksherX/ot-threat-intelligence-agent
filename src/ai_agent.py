"""
Phase 2: AI Agent
Uses Qwen LLM via Ollama to filter OT/ICS relevant CVEs
"""

import subprocess
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OTAgent:
    def __init__(self, model_name="qwen2.5:latest"):
        self.model_name = model_name
        self.ot_keywords = [
            'SCADA', 'PLC', 'HMI', 'ICS', 'OT', 'Industrial Control',
            'Siemens', 'Rockwell', 'Schneider', 'Allen-Bradley',
            'Modbus', 'DNP3', 'OPC', 'Profinet', 'EtherNet/IP',
            'RTU', 'DCS', 'Programmable Logic Controller',
            'SIMATIC', 'ControlLogix', 'CompactLogix', 'Modicon',
            'Industrial Automation', 'Process Control', 'Factory',
            'Manufacturing', 'Critical Infrastructure'
        ]
        self.verify_ollama()
    
    def verify_ollama(self):
        """Check if Ollama is installed and model is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if self.model_name.split(':')[0] not in result.stdout:
                logger.warning(f"Model {self.model_name} not found. Pulling...")
                subprocess.run(['ollama', 'pull', self.model_name], timeout=300)
            
            logger.info(f"Ollama verified with model: {self.model_name}")
        except FileNotFoundError:
            logger.error("Ollama not found! Install from https://ollama.com")
            raise Exception("Ollama is not installed")
        except Exception as e:
            logger.error(f"Error verifying Ollama: {e}")
    
    def query_qwen(self, prompt, max_retries=3):
        """
        Query Qwen model via Ollama CLI
        
        Args:
            prompt: The prompt to send to Qwen
            max_retries: Number of retry attempts
            
        Returns:
            Model response as string
        """
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    ['ollama', 'run', self.model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    logger.debug(f"Qwen response: {response[:100]}...")
                    return response
                else:
                    logger.warning(f"Qwen error (attempt {attempt + 1}): {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Qwen timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Qwen query error: {e}")
        
        return ""
    
    def simple_keyword_check(self, description):
        """
        Fallback keyword-based check for OT relevance
        
        Args:
            description: CVE description text
            
        Returns:
            Boolean indicating OT relevance
        """
        description_upper = description.upper()
        
        for keyword in self.ot_keywords:
            if keyword.upper() in description_upper:
                logger.debug(f"Keyword match found: {keyword}")
                return True
        
        return False
    
    def is_ot_relevant(self, cve_description):
        """
        Determine if CVE is OT/ICS relevant using Qwen LLM
        
        Args:
            cve_description: Description of the CVE
            
        Returns:
            Boolean indicating OT/ICS relevance
        """
        # First, do a quick keyword check
        if not self.simple_keyword_check(cve_description):
            logger.debug("No OT keywords found, skipping LLM check")
            return False
        
        # If keywords found, confirm with LLM
        prompt = f"""You are a cybersecurity expert specializing in Operational Technology (OT) and Industrial Control Systems (ICS).

Analyze the following CVE description and determine if it is relevant to OT/ICS environments such as factories, power plants, water treatment facilities, or critical infrastructure.

OT/ICS indicators include:
- Industrial control systems: SCADA, PLC, HMI, DCS, RTU
- Industrial vendors: Siemens, Rockwell Automation, Schneider Electric, Allen-Bradley, ABB, Honeywell
- Industrial protocols: Modbus, DNP3, OPC, Profinet, EtherNet/IP, BACnet
- Industrial software: FactoryTalk, TIA Portal, Unity Pro, WinCC

CVE Description:
{cve_description}

Answer with ONLY 'YES' if this CVE directly affects OT/ICS systems, or 'NO' if it only affects standard IT systems (like web browsers, office software, general operating systems).

Answer:"""

        response = self.query_qwen(prompt).upper()
        
        # Parse response
        if 'YES' in response:
            logger.info("LLM confirmed OT relevance")
            return True
        elif 'NO' in response:
            logger.info("LLM rejected as IT-only")
            return False
        else:
            # Fallback to keyword check if LLM response unclear
            logger.warning(f"Unclear LLM response: {response}")
            return self.simple_keyword_check(cve_description)
    
    def generate_factory_impact(self, cve_id, description, cvss_score):
        """
        Generate AI insight on factory/industrial impact
        
        Args:
            cve_id: CVE identifier
            description: CVE description
            cvss_score: CVSS severity score
            
        Returns:
            AI-generated impact analysis
        """
        severity_context = ""
        if cvss_score >= 9.0:
            severity_context = "CRITICAL severity"
        elif cvss_score >= 7.0:
            severity_context = "HIGH severity"
        elif cvss_score >= 4.0:
            severity_context = "MEDIUM severity"
        else:
            severity_context = "LOW severity"
        
        prompt = f"""You are an OT cybersecurity analyst. Provide a concise 2-3 sentence explanation of why this vulnerability is dangerous for industrial facilities like factories, power plants, or manufacturing sites.

Focus on real-world operational risks such as:
- Production shutdowns or equipment damage
- Safety hazards to workers
- Loss of process control or monitoring
- Environmental or regulatory impacts
- Financial losses from downtime

CVE ID: {cve_id}
Severity: {severity_context} (CVSS {cvss_score})
Description: {description}

Industrial Impact Analysis (2-3 sentences):"""

        impact = self.query_qwen(prompt)
        
        # Clean up response
        impact = impact.strip()
        
        # If response is empty or too short, generate generic impact
        if len(impact) < 50:
            impact = self._generate_generic_impact(cvss_score, description)
        
        return impact
    
    def _generate_generic_impact(self, cvss_score, description):
        """Generate generic impact statement based on severity"""
        if cvss_score >= 9.0:
            return f"This critical vulnerability could allow attackers to gain complete control of industrial systems, potentially causing severe operational disruption, safety incidents, or equipment damage. Immediate remediation is essential to protect critical infrastructure."
        elif cvss_score >= 7.0:
            return f"This high-severity vulnerability poses significant risk to industrial operations. Exploitation could result in unauthorized access to control systems, process manipulation, or service disruption affecting production and safety."
        else:
            return f"This vulnerability affects industrial control systems and should be addressed through proper patch management and security controls to maintain operational integrity."
    
    def filter_cves(self, cves):
        """
        Filter CVEs for OT relevance and generate insights
        
        Args:
            cves: List of CVE dictionaries from data pipeline
            
        Returns:
            List of OT-relevant CVEs with AI insights
        """
        ot_cves = []
        
        logger.info(f"Analyzing {len(cves)} CVEs for OT relevance...")
        
        for idx, cve in enumerate(cves, 1):
            logger.info(f"[{idx}/{len(cves)}] Analyzing {cve['cve_id']}...")
            
            try:
                if self.is_ot_relevant(cve['description']):
                    logger.info(f"  ✓ OT-RELEVANT: {cve['cve_id']}")
                    
                    # Generate factory impact insight
                    insight = self.generate_factory_impact(
                        cve['cve_id'],
                        cve['description'],
                        cve['cvss_score']
                    )
                    
                    cve['ai_insight'] = insight
                    cve['is_ot_relevant'] = True
                    ot_cves.append(cve)
                else:
                    logger.info(f"  ✗ IT-ONLY: {cve['cve_id']} - Discarded")
            
            except Exception as e:
                logger.error(f"Error processing {cve['cve_id']}: {e}")
                continue
        
        logger.info(f"Filtering complete: {len(ot_cves)}/{len(cves)} OT-relevant CVEs found")
        return ot_cves


if __name__ == "__main__":
    # Test the AI agent
    agent = OTAgent()
    
    # Test CVEs
    test_cves = [
        {
            'cve_id': 'CVE-TEST-001',
            'cvss_score': 9.8,
            'description': 'A critical vulnerability in Siemens SIMATIC S7-1200 PLC allows remote code execution through the Profinet protocol.'
        },
        {
            'cve_id': 'CVE-TEST-002',
            'cvss_score': 7.5,
            'description': 'A buffer overflow vulnerability in Google Chrome browser allows remote code execution.'
        },
        {
            'cve_id': 'CVE-TEST-003',
            'cvss_score': 8.1,
            'description': 'Authentication bypass in Rockwell Automation FactoryTalk View SCADA software allows unauthorized access.'
        }
    ]
    
    ot_filtered = agent.filter_cves(test_cves)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(ot_filtered)} OT-relevant CVEs")
    print(f"{'='*60}\n")
    
    for cve in ot_filtered:
        print(f"{cve['cve_id']} - CVSS: {cve['cvss_score']}")
        print(f"Impact: {cve['ai_insight']}\n")
