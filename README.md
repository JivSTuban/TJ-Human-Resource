<h1 align="center">
  <img src="./TJ_api/TJ/static/img/TJ_logo.png" alt="Project Logo" width="200" /><br />
  <span style="font-size: 2em; font-weight: bold;">Human Resource System</span>
</h1>

## Table of Contents

- [Project Overview](#project-overview)
- [Team Members](#team-members)
- [Project Resources](#project-resources)
- [Getting Started](#getting-started)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [License](#license)

## Project Overview

TJ's Human Resource System is a comprehensive application designed to streamline HR processes and enhance employee management. Our system aims to provide an efficient and user-friendly interface for both managers and employees.

## Team Members

- **Jiv Tuban** - Tech Lead
- **Josh Kyle Cervantes** - Designer & Developer
- **Justin Alexander Labajos** - Project Manager & Developer

## Project Resources

- [Entity Relationship Diagram (ERD)](https://mermaid.live/view#pako:eNqlVk1v2zAM_SuGzy3QFQs25FagWIF1hwJDL0MAgbGYWJ0tGhLdLWv630f5I_Fnmm4-GJYeRT49UaRf4oQ0xssY3a2BrYN8ZSN5brEAxzlajvb7y0t6ib7SOlpGKfjaIAwb5NGjEwjzIqNdA99o7dD7ymS_b00Oq6txs_yOIJvDbpjRarAJzll8Q3ieB2k7gl5rCEpO1Z2jshCLNWZkt14xzRg-oMuN94Zs628k00s9Ex4jQ6Ojh_vj1DO4JAUXWcgxeryPVvGHq6tVXBu8tu6CqOf5YcMZ9r2Eh_E3Rxp94kzBwrbvSx_YKnH75X4QvT2z8xh4dogsFK4Xiy6FFk8M78YEDyiVlt0Jgz-mUCE1Q4CxUNUBnccTczBZRfPjVJwiJYvKlvlaPAqbT12j4BZqVbqKddc7as6hu04DY_VStFGpcTgR19HGZKgK4HRKXODS9_be8nmi9RyXjXGeVZViwmgxqWsGsyZrkr2AjYxXEn-zmUQgYfOM04vKAl0pJ9MXgk3eiPFExqKeQCtSGW2NnRAKvP9FTge-159HmVBVj9OZcPpSBMJDQY-0S1RhMN5vQlLukCe3kziUT62AJ8Cy0D3weP2Ote70ft5kHV6qq2UfoZLPzrhDJg_I1mX333geUjH4ULwrQi4uxmGFkuOB_BUgMg2mqyMW1T3Zd23tP44r9Ja3999e8xkJpPq0PWdwmRJyDhOepzug0-ln7-hEvRrQ99Vpee9yONcOpJa3Ia9GRS0hy6EthWTo9ab4Is6FCBgt_ygVj1XMKea4ipfyqcH9DL6CnbCm7zubxEt2JV7EosU2jZcbyLyM6nNs_nFakwLsD6K8MXr9C4QQum0)
- [Figma Prototype](https://www.figma.com/design/vYqzDNNCFrjzlPUTO85SRz/TJ's?node-id=0-1&t=kUjXV1fHD6GGX0YA-1)
- [Gantt Chart](https://docs.google.com/spreadsheets/d/1PTAUDENq60aPlKM9Gkx5v6iif7RqV7ZHYX3kAwddXdo/edit?gid=187229779#gid=187229779)
- [Project Requirements](https://docs.google.com/document/d/1L9y0qh8n7GNmuDfBt7LZExpDAC30pVNC1ANz6pzKzRE/edit)

## Getting Started

To get started with TJ's Human Resource System:

#### INSTALL CMAKE INTO YOUR SYSTEM 🛠️

<details>
<summary>🍎 macOS Installation</summary>

```bash
brew install cmake
```
</details>

<details>
<summary>🪟 Windows Installation</summary>

Download the CMake Installer from the [CMake official download page](https://cmake.org/download/).
Run the Installer and follow the instructions.
Add CMake to System Path during the installation process.
</details>

and then:

<details>
<summary>🍎 macOS Setup Instructions</summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/JivSTuban/TJ-Human-Resource.git
   ```

2. **Go to the TJ_api folder directory, create and run virtual environment**

   ```bash
   cd TJ_api
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   cd TJ
   pip3 install -r requirements.txt
   ```

4. **Set up the database**

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

   OPTIONAL: **Create Super User**

   ```bash
   python3 manage.py createsuperuser
   ```

5. **Run the application**
   ```bash
   python3 manage.py runserver
   ```
</details>

<details>
<summary>🪟 Windows Setup Instructions</summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/JivSTuban/TJ-Human-Resource.git
   ```

2. **Go to the TJ_api folder directory, create and run virtual environment**

   ```bash
   cd TJ_api
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   cd TJ
   pip install -r requirements.txt
   ```

4. **Set up the database**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

   OPTIONAL: **Create Super User**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the application**
   ```bash
   python manage.py runserver
   ```
</details>

## Features

- Employee Management
- Goal Setting
- Time and Attendance Tracking (Manual and Face Recognition)
- User Profile Management
- Goal Setting and Tracking
- Leave Management
- Jobs and Departments Management
- Employee Panel
- Manager Panel

## Technologies Used

- Frontend: HTML, CSS, BOOTSTRAP, JAVASCRIPT, DJANGO-TEMPLATES
- Backend: DJANGO
- Database: SQLITE
- Other tools: CRISPY, DJANGO-FILTER, PILLOW, RUFF

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
