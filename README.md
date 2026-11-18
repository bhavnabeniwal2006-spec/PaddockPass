# 🏎️ Paddock Pass

**Paddock Pass** is a Formula 1 informational website developed using Python and Flask. It provides users with information about F1 drivers, teams and circuits through a simple and user-friendly interface.

## ✨ Features

- **Home Page:** Introduction to the world of Formula 1.
- **Drivers Section:** Explore Formula 1 drivers.
- **Driver Profiles:** View individual driver information and photographs.
- **Teams Section:** Explore Formula 1 teams.
- **Circuits Section:** Discover Formula 1 racing circuits.
- **User Registration:** Create a personal account.
- **User Login and Logout:** Securely access and exit an account.
- **Favourite Drivers:** Save and manage favourite drivers.

## 🛠️ Technologies Used

- Python
- Flask
- HTML
- CSS
- SQLite
- VS Code

## 📁 Project Structure

```text
Paddock-Pass/
│
├── web.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── drivers.html
│   ├── driver.html
│   ├── explore.html
│   ├── login.html
│   ├── signup.html
│   └── favourites.html
│
└── static/
    ├── css/
    └── images/
        └── drivers/
```

## ▶️ How to Run the Project

1. Install Python on your computer.
2. Download or clone this repository.
3. Open the project folder in VS Code.
4. Open the terminal.
5. Install the required package:

```bash
pip install -r requirements.txt
```

6. Run the application:

```bash
python web.py
```

7. Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## 🗄️ Database

SQLite is used to store user account information and favourite drivers. The application creates the required database tables when it starts.

## 🎓 Project Information

Developed as a BCA academic mini-project.

**Project Name:** Paddock Pass  
**Domain:** Formula 1 Information Website  
**Backend:** Python Flask

---

*Explore the world of Formula 1 with Paddock Pass!*
