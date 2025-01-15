Here’s a step-by-step guide to install and run Odoo on your Windows machine using your custom Odoo code in a ZIP file:

---

### Step 1: Install Prerequisites

1. **Install Python**:
   - Download and install Python 3.10 (compatible with your Odoo version) from the [official Python website](https://www.python.org/).
   - During installation, check **"Add Python to PATH"**.
   - OR use the script install_python.bat to install. Below is an example of the arguments for the script
     ```bash
     install_python.bat 3.10.11 "C:\Users\username\OneDrive\Desktop\softwares"
     ```

2. **Install PostgreSQL**:
   - Download and install PostgreSQL from the [official PostgreSQL website](https://www.postgresql.org/).
   - Note the username (`postgres`) and password you set during installation.
   - Or use the script install_pgsql.bat to install. Below is an example of the arguments for the script
     ```bash
     install_pgsql.bat 15.4 "C:\Users\username\OneDrive\Desktop\softwares"
     ```

3. **Install Node.js and Less Compiler**:
   - Download and install Node.js from the [official Node.js website](https://nodejs.org/).
   - Install the LESS compiler globally:
     ```bash
     npm install -g less less-plugin-clean-css
     ```
   - OR use the script install_nodejs.bat to install. Below is an example of the arguments for the script
     ```bash
     install_nodejs 9.5.1 "C:\Users\username\OneDrive\Desktop\softwares"
     ```

4. **Install Wkhtmltopdf**:
   - Download and install Wkhtmltopdf from [wkhtmltopdf.org](https://wkhtmltopdf.org/).
   - Use the version compatible with Odoo (e.g., `0.12.5`).

---

### Step 2: Execute installation script

1. **Execute install_odoo.bat**:
   - This script assumes you have the necessary prerequisites (Python, PostgreSQL, Node.js, and Wkhtmltopdf) installed and configured in your system's PATH.
  
2. **Start odoo**
   - Execute `start-odoo.bat`
