# Solar CRM - Complete Sales Management System

A comprehensive CRM system for solar sales companies with pipeline management, revenue forecasting, and analytics.

## Installation Instructions for PyCharm with SQLite3

### Prerequisites
- Python 3.14.2 or higher
- PyCharm (Community or Professional)
- Git (optional)

### Step-by-Step Installation

1. **Create a new project in PyCharm**
   - Open PyCharm
   - Click "New Project"
   - Name it "solar_crm"
   - Choose a location
   - Select "New environment using" → "Virtualenv"
   - Click "Create"

2. **Create the folder structure**
   
   Create these folders in your project root:

solar_crm/
├── apps/
│ ├── core/
│ └── leads/
│ └── api/
├── crm/
├── static/
│ ├── css/
│ └── js/
└── templates/
├── dashboard/
└── leads/


3. **Create all the files**

Create each file as shown in the structure and copy the code provided.

4. **Install requirements**

Open Terminal in PyCharm (bottom panel) and run:
```bash
pip install -r requirements.txt
