import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.map_utils import create_base_map

def create_community_reports(stakeholder):
    st.header("📱 Community Reporting & Citizen Science")
    
    # Introduction based on stakeholder
    if stakeholder == "Citizens":
        st.info("👥 **Citizen Portal:** Report environmental issues and contribute to city-wide monitoring.")
    elif stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Dashboard:** Review and respond to citizen reports for rapid issue resolution.")
    elif stakeholder == "Researchers":
        st.info("🔬 **Research Data:** Access community-contributed data for environmental studies.")
    
    # Main tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Submit Report", "🗺️ Report Map", "📊 Analytics", "✅ Response Tracking"])
    
    with tab1:
        st.subheader("Submit Environmental Report")
        
        # Report submission form
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Report Type:",
                ["Air Pollution", "Water Pollution", "Noise Pollution", "Waste Management", 
                 "Tree/Green Space", "Flooding", "Infrastructure", "Other"]
            )
            
            severity = st.selectbox(
                "Severity Level:",
                ["Low", "Medium", "High", "Critical"]
            )
            
            location_method = st.radio(
                "Location Input:",
                ["Use Current Location", "Enter Address", "Select on Map"]
            )
            
            if location_method == "Enter Address":
                address = st.text_input("Enter Address:")
            
        with col2:
            description = st.text_area(
                "Describe the Issue:",
                placeholder="Please provide detailed description of the environmental issue..."
            )
            
            # File upload for photos
            uploaded_files = st.file_uploader(
                "Upload Photos (optional):",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png']
            )
            
            contact_info = st.text_input(
                "Contact Information (optional):",
                placeholder="Email or phone number for follow-up"
            )
            
            anonymous = st.checkbox("Submit anonymously")
        
        # Location selection map
        if location_method == "Select on Map":
            st.subheader("📍 Select Report Location")
            location_map = create_base_map()
            
            # Add click handler instruction
            st.info("Click on the map to select the location of the issue")
            
            map_data = st_folium(location_map, width=700, height=400)
            
            if map_data['last_clicked']:
                selected_lat = map_data['last_clicked']['lat']
                selected_lon = map_data['last_clicked']['lng']
                st.success(f"Location selected: {selected_lat:.4f}, {selected_lon:.4f}")
        
        # Submit button
        if st.button("🚀 Submit Report", type="primary"):
            # Here you would normally save to database
            st.success("✅ Report submitted successfully! Reference ID: CR-2025-{:04d}".format(
                hash(str(datetime.now())) % 10000
            ))
            st.info("Your report has been forwarded to the relevant authorities. You will receive updates via the tracking system.")
    
    with tab2:
        st.subheader("🗺️ Community Reports Map")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            map_filter_type = st.selectbox(
                "Filter by Type:",
                ["All", "Air Pollution", "Water Pollution", "Waste", "Flooding", "Green Space"]
            )
        
        with col2:
            map_filter_status = st.selectbox(
                "Filter by Status:",
                ["All", "Open", "In Progress", "Resolved", "Closed"]
            )
        
        with col3:
            map_filter_time = st.selectbox(
                "Time Period:",
                ["Last 24 Hours", "Last Week", "Last Month", "All Time"]
            )
        
        # Community reports map
        reports_map = create_base_map()
        
        # Sample community reports data
        community_reports = [
            {'lat': 12.9716, 'lon': 77.5946, 'type': 'Air Pollution', 'severity': 'High', 'status': 'Open', 'description': 'Heavy smoke from construction site'},
            {'lat': 12.9698, 'lon': 77.7500, 'type': 'Water Pollution', 'severity': 'Critical', 'status': 'In Progress', 'description': 'Sewage overflow in residential area'},
            {'lat': 12.9352, 'lon': 77.6245, 'type': 'Waste', 'severity': 'Medium', 'status': 'Resolved', 'description': 'Illegal dumping near lake'},
            {'lat': 12.9833, 'lon': 77.6167, 'type': 'Noise Pollution', 'severity': 'High', 'status': 'Open', 'description': 'Construction noise beyond permitted hours'},
            {'lat': 13.0358, 'lon': 77.5970, 'type': 'Flooding', 'severity': 'Critical', 'status': 'In Progress', 'description': 'Poor drainage causing waterlogging'},
            {'lat': 12.8456, 'lon': 77.6636, 'type': 'Green Space', 'severity': 'Medium', 'status': 'Open', 'description': 'Unauthorized tree cutting'}
        ]
        
        # Add report markers to map
        for report in community_reports:
            # Color based on severity
            if report['severity'] == 'Critical':
                color = 'red'
            elif report['severity'] == 'High':
                color = 'orange'
            elif report['severity'] == 'Medium':
                color = 'yellow'
            else:
                color = 'green'
            
            # Icon based on status
            if report['status'] == 'Resolved':
                icon = 'check'
            elif report['status'] == 'In Progress':
                icon = 'cog'
            else:
                icon = 'exclamation'
            
            folium.Marker(
                location=[report['lat'], report['lon']],
                popup=f"""
                <b>Type:</b> {report['type']}<br>
                <b>Severity:</b> {report['severity']}<br>
                <b>Status:</b> {report['status']}<br>
                <b>Description:</b> {report['description']}
                """,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(reports_map)
        
        map_data = st_folium(reports_map, width=700, height=500)
    
    with tab3:
        st.subheader("📊 Community Reports Analytics")
        
        # Reports summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reports", "1,247", "+89")
        
        with col2:
            st.metric("Open Issues", "342", "+23")
        
        with col3:
            st.metric("Avg Response Time", "4.2 hrs", "-0.8 hrs")
        
        with col4:
            st.metric("Resolution Rate", "76%", "+5%")
        
        # Reports by type and status
        col1, col2 = st.columns(2)
        
        with col1:
            # Reports by type
            report_types_data = pd.DataFrame({
                'Type': ['Air Pollution', 'Water Pollution', 'Waste Management', 'Flooding', 'Noise Pollution', 'Green Space'],
                'Count': [234, 189, 167, 145, 123, 89],
                'Percentage': [28.1, 22.7, 20.1, 17.4, 14.8, 10.7]
            })
            
            fig = px.pie(report_types_data, values='Count', names='Type',
                        title='Reports by Type (Last 30 Days)')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Response time by department
            response_time_data = pd.DataFrame({
                'Department': ['BBMP', 'BWSSB', 'BESCOM', 'Traffic Police', 'Pollution Board'],
                'Avg Response (hrs)': [3.2, 5.1, 2.8, 1.9, 6.4],
                'Target (hrs)': [4.0, 6.0, 4.0, 2.0, 8.0]
            })
            
            fig = px.bar(response_time_data, x='Department', y=['Avg Response (hrs)', 'Target (hrs)'],
                        title='Response Time by Department',
                        barmode='group')
            st.plotly_chart(fig, width='stretch')
        
        # Trending issues
        st.subheader("📈 Trending Environmental Issues")
        
        trending_data = pd.DataFrame({
            'Issue': ['Construction Dust', 'Lake Pollution', 'Illegal Dumping', 'Traffic Noise', 'Sewage Overflow'],
            'Reports This Week': [45, 38, 32, 29, 25],
            'Change from Last Week': ['+18', '+12', '-5', '+8', '+15'],
            'Average Severity': [3.2, 4.1, 2.8, 2.5, 3.8],
            'Top Location': ['Whitefield', 'Bellandur', 'Electronic City', 'Silk Board', 'Koramangala']
        })
        
        st.dataframe(trending_data, width='stretch')
        
        # Geographic heat map of reports
        st.subheader("🔥 Report Density Heatmap")
        
        density_data = pd.DataFrame({
            'Area': ['Electronic City', 'Whitefield', 'Koramangala', 'Silk Board', 'Hebbal', 'BTM Layout', 'Indiranagar', 'Jayanagar'],
            'Report Density (per sq km)': [12.4, 10.8, 9.6, 15.2, 7.3, 8.9, 6.7, 5.4],
            'Population Density': [8500, 6200, 12000, 9800, 5400, 7800, 11200, 8900]
        })
        
        fig = px.scatter(density_data, x='Population Density', y='Report Density (per sq km)',
                        size='Report Density (per sq km)', text='Area',
                        title='Report Density vs Population Density',
                        labels={'Report Density (per sq km)': 'Reports per sq km'})
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("✅ Report Response Tracking")
        
        if stakeholder == "Citizens":
            # Citizen view - track their own reports
            st.info("Enter your reference ID to track report status")
            
            tracking_id = st.text_input("Report Reference ID:", placeholder="CR-2025-XXXX")
            
            if tracking_id:
                # Mock tracking data
                st.success("Report Found!")
                
                # Progress indicator
                progress_steps = ["Submitted", "Acknowledged", "Assigned", "In Progress", "Resolved"]
                current_step = 3  # In Progress
                
                for i, step in enumerate(progress_steps):
                    if i < current_step:
                        st.success(f"✅ {step}")
                    elif i == current_step:
                        st.info(f"🔄 {step} (Current)")
                    else:
                        st.write(f"⏳ {step}")
                
                # Report details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Report Type:** Air Pollution")
                    st.write("**Severity:** High")
                    st.write("**Location:** Electronic City")
                    st.write("**Submitted:** 2025-09-26 14:30")
                
                with col2:
                    st.write("**Assigned to:** BBMP Environmental Team")
                    st.write("**Expected Resolution:** 2025-09-30")
                    st.write("**Last Update:** Field inspection completed")
                    st.write("**Contact:** env.team@bbmp.gov.in")
        
        else:
            # Authority view - manage all reports
            st.subheader("📋 All Reports Management")
            
            # Filters for authorities
            col1, col2, col3 = st.columns(3)
            
            with col1:
                dept_filter = st.selectbox(
                    "Department:",
                    ["All", "BBMP", "BWSSB", "BESCOM", "Pollution Board"]
                )
            
            with col2:
                priority_filter = st.selectbox(
                    "Priority:",
                    ["All", "Critical", "High", "Medium", "Low"]
                )
            
            with col3:
                status_filter = st.selectbox(
                    "Status:",
                    ["All", "Open", "Assigned", "In Progress", "Resolved"]
                )
            
            # Reports management table
            management_df = pd.DataFrame({
                'ID': ['CR-2025-1234', 'CR-2025-1235', 'CR-2025-1236', 'CR-2025-1237', 'CR-2025-1238'],
                'Type': ['Air Pollution', 'Water Pollution', 'Waste', 'Flooding', 'Noise'],
                'Location': ['Electronic City', 'Bellandur', 'Whitefield', 'Silk Board', 'Koramangala'],
                'Priority': ['High', 'Critical', 'Medium', 'High', 'Low'],
                'Status': ['In Progress', 'Assigned', 'Open', 'In Progress', 'Resolved'],
                'Assigned To': ['ENV Team A', 'Water Dept', 'Unassigned', 'Drainage Team', 'Completed'],
                'Days Open': [3, 1, 7, 4, 0],
                'Action': ['View', 'View', 'Assign', 'View', 'Archive']
            })
            
            st.dataframe(management_df, width='stretch')
            
            # Bulk actions
            st.subheader("🔧 Bulk Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Export Selected"):
                    st.info("Reports exported to CSV")
            
            with col2:
                if st.button("📧 Send Updates"):
                    st.info("Update notifications sent to reporters")
            
            with col3:
                if st.button("📊 Generate Report"):
                    st.info("Weekly summary report generated")
