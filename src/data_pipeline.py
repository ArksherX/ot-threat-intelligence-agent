"""
Phase 1: Data Pipeline
Fetches latest CVEs from NVD API
"""

import requests
import time
from datetime import datetime, timedelta
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CVEPipeline:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache_file = "data/cve_cache.json"
        self.load_cache()
    
    def load_cache(self):
        """Load previously processed CVE IDs from cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.processed_cves = json.load(f)
                logger.info(f"Loaded {len(self.processed_cves)} cached CVE IDs")
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self.processed_cves = []
        else:
            self.processed_cves = []
    
    def save_cache(self):
        """Save processed CVE IDs to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.processed_cves, f, indent=2)
            logger.info(f"Cache saved with {len(self.processed_cves)} CVE IDs")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def fetch_latest_cves(self, minutes_ago=10):
        """
        Fetch CVEs published in the last N minutes
        
        Args:
            minutes_ago: Number of minutes to look back
            
        Returns:
            List of CVE dictionaries
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes_ago)
        
        # Format for NVD API (ISO 8601)
        params = {
            'pubStartDate': start_time.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'pubEndDate': end_time.strftime('%Y-%m-%dT%H:%M:%S.000')
        }
        
        headers = {'apiKey': self.api_key} if self.api_key else {}
        
        try:
            logger.info(f"Fetching CVEs from {start_time} to {end_time}")
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Respect rate limiting
            time.sleep(6)  # NVD allows 5 requests per 30 seconds with API key
            
            data = response.json()
            
            cves = []
            for item in data.get('vulnerabilities', []):
                cve_data = item.get('cve', {})
                cve_id = cve_data.get('id')
                
                # Skip if already processed
                if cve_id in self.processed_cves:
                    logger.debug(f"Skipping already processed {cve_id}")
                    continue
                
                # Extract CVSS score (prefer v3.1 > v3.0 > v2)
                metrics = cve_data.get('metrics', {})
                cvss_score = 0.0
                cvss_vector = "N/A"
                
                if 'cvssMetricV31' in metrics:
                    cvss_data = metrics['cvssMetricV31'][0]['cvssData']
                    cvss_score = cvss_data.get('baseScore', 0.0)
                    cvss_vector = cvss_data.get('vectorString', 'N/A')
                elif 'cvssMetricV30' in metrics:
                    cvss_data = metrics['cvssMetricV30'][0]['cvssData']
                    cvss_score = cvss_data.get('baseScore', 0.0)
                    cvss_vector = cvss_data.get('vectorString', 'N/A')
                elif 'cvssMetricV2' in metrics:
                    cvss_data = metrics['cvssMetricV2'][0]['cvssData']
                    cvss_score = cvss_data.get('baseScore', 0.0)
                    cvss_vector = cvss_data.get('vectorString', 'N/A')
                
                # Extract description (English)
                descriptions = cve_data.get('descriptions', [])
                description = "No description available"
                for desc in descriptions:
                    if desc.get('lang') == 'en':
                        description = desc.get('value', 'No description available')
                        break
                
                # Extract references
                references = cve_data.get('references', [])
                ref_urls = [ref.get('url') for ref in references[:3]]  # First 3 refs
                
                cve_obj = {
                    'cve_id': cve_id,
                    'cvss_score': cvss_score,
                    'cvss_vector': cvss_vector,
                    'description': description,
                    'published_date': cve_data.get('published', 'Unknown'),
                    'last_modified': cve_data.get('lastModified', 'Unknown'),
                    'references': ref_urls
                }
                
                cves.append(cve_obj)
                self.processed_cves.append(cve_id)
                logger.info(f"New CVE found: {cve_id} (CVSS: {cvss_score})")
            
            self.save_cache()
            logger.info(f"Fetched {len(cves)} new CVEs")
            return cves
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Error fetching CVEs: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching CVEs: {e}")
            return []
    
    def fetch_recent_cves_fallback(self, days=1):
        """
        Fallback method to fetch CVEs from the last N days
        Useful for initial testing or when real-time data is sparse
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of CVE dictionaries
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        params = {
            'pubStartDate': start_time.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'pubEndDate': end_time.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'resultsPerPage': 20  # Limit results
        }
        
        headers = {'apiKey': self.api_key} if self.api_key else {}
        
        try:
            logger.info(f"Fallback: Fetching CVEs from last {days} day(s)")
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            time.sleep(6)
            
            data = response.json()
            cves = []
            
            for item in data.get('vulnerabilities', []):
                cve_data = item.get('cve', {})
                cve_id = cve_data.get('id')
                
                if cve_id in self.processed_cves:
                    continue
                
                # Same extraction logic as above
                metrics = cve_data.get('metrics', {})
                cvss_score = 0.0
                
                if 'cvssMetricV31' in metrics:
                    cvss_score = metrics['cvssMetricV31'][0]['cvssData'].get('baseScore', 0.0)
                elif 'cvssMetricV30' in metrics:
                    cvss_score = metrics['cvssMetricV30'][0]['cvssData'].get('baseScore', 0.0)
                elif 'cvssMetricV2' in metrics:
                    cvss_score = metrics['cvssMetricV2'][0]['cvssData'].get('baseScore', 0.0)
                
                descriptions = cve_data.get('descriptions', [])
                description = "No description available"
                for desc in descriptions:
                    if desc.get('lang') == 'en':
                        description = desc.get('value', 'No description available')
                        break
                
                cves.append({
                    'cve_id': cve_id,
                    'cvss_score': cvss_score,
                    'description': description,
                    'published_date': cve_data.get('published', 'Unknown')
                })
                
                self.processed_cves.append(cve_id)
            
            self.save_cache()
            logger.info(f"Fallback fetched {len(cves)} CVEs")
            return cves
            
        except Exception as e:
            logger.error(f"Error in fallback fetch: {e}")
            return []


if __name__ == "__main__":
    # Test the pipeline
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('NVD_API_KEY')
    
    pipeline = CVEPipeline(api_key)
    
    # Try recent CVEs first (for testing)
    cves = pipeline.fetch_recent_cves_fallback(days=2)
    
    print(f"\nFetched {len(cves)} CVEs")
    for cve in cves[:3]:  # Show first 3
        print(f"\n{cve['cve_id']} - CVSS: {cve['cvss_score']}")
        print(f"Description: {cve['description'][:150]}...")
