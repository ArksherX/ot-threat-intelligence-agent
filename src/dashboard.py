"""
Phase 4: Streamlit Dashboard
Live visualization of OT threat intelligence
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import time

# Page configuration
st.set_page_config(
    page_title="OT Threat Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3241;
    }
    .threat-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid;
        margin-bottom: 20px;
    }
    .critical { border-left-color: #dc2626; }
    .high { border-left-color: #ea580c; }
    .medium { border-left-color: #ca8a04; }
    .low { border-left-color: #16a34a; }
</style>
""", unsafe_allow_html=True)


def load_threats(filepath="data/output_sample.json"):
    """Load threats from JSON file"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading threats: {e}")
            return None
    return None


def get_severity_color(severity):
    """Get color for severity badge"""
    colors = {
        'CRITICAL': '#dc2626',
        'HIGH': '#ea580c',
        'MEDIUM': '#ca8a04',
        'LOW': '#16a34a',
        'NONE': '#6b7280'
    }
    return colors.get(severity, '#6b7280')


def get_severity_emoji(severity):
    """Get emoji for severity level"""
    emojis = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢',
        'NONE': '⚪'
    }
    return emojis.get(severity, '⚪')


def format_date(date_string):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except:
        return date_string


# Main header
st.title("🛡️ OT Threat Intelligence Dashboard")
st.markdown("**Real-time monitoring of OT/ICS vulnerabilities**")
st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.rerun()
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Refresh interval (seconds)", 10, 300, 30)
        st.info(f"Dashboard will refresh every {refresh_interval} seconds")
    
    st.markdown("---")
    
    # Filter controls
    st.header("🔍 Filters")
    severity_filter = st.multiselect(
        "Severity Level",
        ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        default=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    )
    
    min_cvss = st.slider("Minimum CVSS Score", 0.0, 10.0, 0.0, 0.1)
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    This dashboard displays OT/ICS vulnerabilities detected by the 
    Autonomous AI Agent.
    
    **Data Source:** NVD API  
    **AI Filter:** Qwen LLM  
    **Update Frequency:** Every 10 minutes
    """)

# Load threat data
data = load_threats()

if data is None:
    st.warning("⚠️ No data available. Please run the agent to fetch threats.")
    st.code("python run_agent.py", language="bash")
    st.stop()

# Display last updated time
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"**Last Updated:** {format_date(data.get('generated_at', 'Unknown'))}")
with col2:
    if st.button("📥 Download Report"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"ot_threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Filter threats
threats = data.get('threats', [])
filtered_threats = [
    t for t in threats 
    if t['severity'] in severity_filter and t['cvss_score'] >= min_cvss
]

# Metrics
st.subheader("📊 Threat Overview")
col1, col2, col3, col4, col5 = st.columns(5)

total_threats = len(filtered_threats)
critical = sum(1 for t in filtered_threats if t['severity'] == 'CRITICAL')
high = sum(1 for t in filtered_threats if t['severity'] == 'HIGH')
medium = sum(1 for t in filtered_threats if t['severity'] == 'MEDIUM')
low = sum(1 for t in filtered_threats if t['severity'] == 'LOW')

col1.metric("Total Threats", total_threats)
col2.metric("🔴 Critical", critical)
col3.metric("🟠 High", high)
col4.metric("🟡 Medium", medium)
col5.metric("🟢 Low", low)

st.markdown("---")

# Display threats
if filtered_threats:
    st.subheader(f"🎯 Detected Threats ({len(filtered_threats)})")
    
    # View toggle
    view_mode = st.radio(
        "View Mode:",
        ["Detailed Cards", "Table View"],
        horizontal=True
    )
    
    if view_mode == "Detailed Cards":
        # Card view
        for threat in filtered_threats:
            severity = threat['severity']
            severity_color = get_severity_color(severity)
            severity_emoji = get_severity_emoji(severity)
            
            with st.container():
                st.markdown(f"""
                <div class="threat-card {severity.lower()}">
                    <h3>{severity_emoji} {threat['cve_id']} - {severity}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**📄 Description:**")
                    st.write(threat['description'])
                    
                    st.markdown("**🤖 AI Impact Analysis:**")
                    st.info(threat['ai_insight'])
                    
                    # References
                    if threat.get('references'):
                        st.markdown("**🔗 References:**")
                        for ref in threat['references'][:3]:
                            st.markdown(f"- [{ref}]({ref})")
                
                with col2:
                    st.markdown("**📈 CVSS Score**")
                    st.markdown(f"<h1 style='color: {severity_color}; text-align: center;'>{threat['cvss_score']}</h1>", 
                              unsafe_allow_html=True)
                    
                    st.markdown("**📅 Published**")
                    st.text(format_date(threat['published_date']))
                    
                    st.markdown("**🔄 Last Modified**")
                    st.text(format_date(threat.get('last_modified', 'Unknown')))
                
                st.markdown("---")
    
    else:
        # Table view
        df = pd.DataFrame(filtered_threats)
        df['published_date'] = df['published_date'].apply(lambda x: x[:10] if isinstance(x, str) else x)
        
        display_df = df[['cve_id', 'severity', 'cvss_score', 'published_date', 'description']].copy()
        display_df.columns = ['CVE ID', 'Severity', 'CVSS', 'Published', 'Description']
        display_df['Description'] = display_df['Description'].str[:100] + '...'
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Detailed view on selection
        selected_cve = st.selectbox("Select CVE for details:", df['cve_id'].tolist())
        if selected_cve:
            threat = next(t for t in filtered_threats if t['cve_id'] == selected_cve)
            
            st.subheader(f"Details: {selected_cve}")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Description:**")
                st.write(threat['description'])
                st.markdown("**AI Impact Analysis:**")
                st.info(threat['ai_insight'])
            
            with col2:
                st.metric("CVSS Score", threat['cvss_score'])
                st.metric("Severity", threat['severity'])

else:
    st.info("✅ No threats match the current filters.")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.caption("🛡️ Powered by NVD API + Qwen AI | ControlPoint OT Security")
