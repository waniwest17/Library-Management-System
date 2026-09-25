# Library-Management-System
📚 Library Management System with Automated Fine Calculation

A lightweight, database-backed Library Management System built with Python and SQLite. The system helps manage books, library members, borrowing and returning, overdue fines, and library reports through a simple command-line interface (CLI).

📌 Project Overview

Small libraries often rely on physical registers or spreadsheets to manage books, members, and due dates. This can make it difficult to track available books, overdue loans, member borrowing history, and fines.

This project provides a simple solution by automating core library operations and reducing manual effort and errors.

✨ Features

* 📖 Add, search, and delete books
* 👤 Register and manage library members
* 📚 Issue books to members
* 🔄 Return borrowed books
* 📅 Automatic due-date calculation
* 💰 Automatic fine calculation for overdue books
* 📊 Generate library reports
* 🔎 Search books by title, author, genre, or ISBN
* 📋 View member borrowing history
* ⚠️ View overdue books
* 📈 View most-issued books
* 💾 Persistent data storage using SQLite

🛠️ Technologies Used

* Python 3
* SQLite3 — database storage
* datetime — date, due-date, and fine calculations
* Object-Oriented Programming (OOP)
* Command-Line Interface (CLI)

🏗️ System Architecture

The system is organized around three core classes:

Book

Handles book information and book-related database operations.

Member

Handles member information and member-related operations.

Library

Handles the main library logic, including:

* Issuing books
* Returning books
* Fine calculation
* Reports
* Interaction between books and members

The SQLite database stores books, members, and issue/return transactions.

🗄️ Database

The project uses SQLite, so no external database server is required.

The issues table connects books and members using foreign keys and stores information such as:

* Issue date
* Due date
* Return date
* Fine

This allows the system to maintain borrowing history and generate reports.

💰 Automated Fine Calculation

The system automatically calculates fines when a book is returned after its due date.

The project assumes:

* 📅 Loan period: 14 days
* 💵 A fixed daily fine rate
* 👥 The same rules apply to all members

Fine calculation uses Python’s datetime module to compare the due date with the actual return date.

📊 Reports

The system can generate reports such as:

Overdue Books

Shows books that have not been returned by their due date.

Most-Issued Books

Shows which books have been borrowed most frequently.

Member Borrowing History

Shows the borrowing history associated with an individual member.

📁 Project Structure

Library-Management-System/
│
├── main.py
├── library.py
├── book.py
├── member.py
├── library.db
├── README.md
└── requirements.txt

The exact filenames may differ depending on the final source-code implementation.

🚀 Getting Started

1. Clone the repository

git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git

2. Navigate to the project directory

cd Library-Management-System

3. Run the application

python main.py

The application will open a command-line menu through which you can manage books, members, borrowing, returns, fines, and reports.

🖥️ Example Operations

A typical workflow is:

1. Add Book
2. Search Book
3. Register Member
4. Issue Book
5. Return Book
6. View Overdue Books
7. View Most-Issued Books
8. View Member History
9. Exit

🎯 Project Goals

The main goals of the project are to:

* Maintain a searchable book catalog
* Register and manage library members
* Automate book issuing and returning
* Automatically calculate due dates and fines
* Generate useful library reports
* Reduce manual record keeping
* Demonstrate database-backed application development using Python

📦 Deliverables

The final project includes:

* 💻 Python source code
* 🗄️ SQLite database
* 📖 Project documentation
* 📊 Library reports and functionality demonstrated through the CLI

⚠️ Project Assumptions

* Each book title can have multiple physical copies, tracked as a count rather than individually barcoded copies.
* The standard loan period is 14 days.
* A fixed daily fine rate is used.
* The system is designed for a single user on a single terminal.
* Books and member information are entered manually.
* No external ISBN or library database API is used.

🔮 Future Improvements

Possible future versions could include:

* 🌐 Web-based interface
* 🖥️ Graphical user interface (GUI)
* 🔐 User authentication
* 📱 Mobile-friendly interface
* 📧 Automated overdue notifications
* 📚 Individual barcode/QR-code tracking
* ☁️ Cloud database support
* 📊 More advanced analytics and dashboards

👥 Team

Team Name: vILLNZ

Team Lead: Wani Innocent

Project: Library Management System with Automated Fine Calculation

📚 References

* Python Documentation
* Python sqlite3 Documentation
* Python datetime Documentation
* SQLite Documentation
* Koha Library Management System

⸻

📄 License

This project was developed as an academic project for educational purposes.
