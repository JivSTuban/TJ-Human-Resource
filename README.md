<h1 align="center">
  <img src="./TJ_logo.png" alt="Project Logo" width="200" /><br />
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

- **Jiv Tuban** - Full-stack Developer
- **Josh Kyle Cervantes** - Designer & Front-end Tester
- **Justin Alexander Labajos** - Project Manager & Back-end Tester

## Project Resources

- [Entity Relationship Diagram (ERD)](https://lucid.app/lucidchart/013b6572-5ae9-4f4a-bb3d-d02daf6ee185/edit?viewport_loc=-4894%2C4653%2C2528%2C1520%2C0_0&invitationId=inv_4a4705f6-0406-42c7-bb19-8468e7325180) (Deprecated)
- [Figma Prototype](https://www.figma.com/design/vYqzDNNCFrjzlPUTO85SRz/TJ's?node-id=0-1&t=kUjXV1fHD6GGX0YA-1)
- [Gantt Chart](https://docs.google.com/spreadsheets/d/1PTAUDENq60aPlKM9Gkx5v6iif7RqV7ZHYX3kAwddXdo/edit#gid=187229779)
- [Project Requirements](https://docs.google.com/document/d/1L9y0qh8n7GNmuDfBt7LZExpDAC30pVNC1ANz6pzKzRE/edit)

## Getting Started

To get started with TJ's Human Resource System, follow these steps:

### MAC

1. **Clone the repository**  
   ```bash
   git clone https://github.com/JivSTuban/TJ-Human-Resource.git
   ```

2. **Go to the project directory**  
   ```bash
   cd TJ_api/TJ
   ```

3. **Install dependencies**  
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Set up the database**  

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

5. **Run the application**
    ```bash
    python3 manage.py runserver
    ```

### WINDOWS

1. **Clone the repository**  
   ```bash
   git clone https://github.com/JivSTuban/TJ-Human-Resource.git
   ```

2. **Go to the project directory**  
   ```bash
   cd TJ_api/TJ
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**  

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the application**
    ```bash
    python manage.py runserver
    ```

## Features

- Employee Management
- Goal Setting
- Time and Attendance Tracking
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
