🌍 Online Geospatial Dashboard for Climate-Resilient Bengaluru
A real-time decision-support platform integrating NASA Earth observation data with local city datasets to address Bengaluru's critical urban challenges.

🔹 Project Overview
Bengaluru, a rapidly growing metropolis, faces significant threats from shrinking green spaces, urban heat islands, and water scarcity. Current city planning lacks real-time, data-driven insights, hindering proactive measures.

This project addresses this gap by creating an online geospatial dashboard that provides actionable intelligence for urban planners, policymakers, and citizens. By fusing satellite data with on-the-ground reports, we aim to foster climate-resilient urban development and improve public well-being.

🔹 Key Features
🌡️ Urban Heat Island Mapping: Uses MODIS and Landsat thermal data combined with vegetation indices (NDVI) to pinpoint overheated neighborhoods.

💧 Water Body & Flood Risk Monitor: Tracks lake health, water quality, and identifies flood-prone areas using precipitation and topographical data.

🌬️ Air Quality & Growth Corridors: Overlays aerosol and NO 
2
​
  datasets to identify pollution hotspots in key growth areas.

🏙️ Urban Growth Analyzer: Utilizes VIIRS night-time lights and Harmonized Landsat Sentinel (HLS) data to analyze unplanned sprawl.

📱 Community Participation: Integrates a citizen science module for residents to report local issues, providing crucial ground-level data.

🔹 Technology Stack
This project leverages open-source geospatial libraries and a cloud-based architecture to process and visualize large-scale datasets efficiently.

Front-end: React.js, Mapbox GL JS / Leaflet

Back-end: Python (Django/Flask), GeoDjango

Geospatial Stack: PostGIS, GDAL/OGR, Rasterio

Data Sources:

NASA Earth Observations: MODIS, Landsat, VIIRS, TROPOMI, GRACE, GPM

Local Datasets: BBMP, BDA, BWSSB, BESCOM

Deployment: AWS / Google Cloud Platform

🔹 Getting Started
For information on how to set up the development environment, please refer to the CONTRIBUTING.md file.

# Clone the repository
git clone [https://github.com/your-username/bengaluru-geodashboard.git](https://github.com/your-username/bengaluru-geodashboard.git)

# Navigate to the project directory
cd bengaluru-geodashboard

# Install dependencies (detailed steps in CONTRIBUTING.md)
pip install -r requirements.txt
npm install

🔹 Expected Impact
Climate-Resilient Planning: Helps city leaders to make data-driven decisions on green infrastructure and sustainable urban design.

Improved Public Health: Identifies areas needing intervention to reduce heat stress and air pollution.

Citizen Empowerment: Provides transparent access to crucial environmental data, empowering communities to participate in city planning.

🔹 License
This project is licensed under the MIT License. See the LICENSE file for details.

🔹 Contact
For questions or collaborations, please open an issue or contact stusanthosh5195@gmail.com.
