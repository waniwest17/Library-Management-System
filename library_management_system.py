"""Library Management System."""

import sqlite3
from datetime import datetime, timedelta

DB_NAME = "library.db"
FINE_PER_DAY = 5
LOAN_PERIOD_DAYS = 14


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            isbn TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            join_date TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            fine REAL DEFAULT 0,
            FOREIGN KEY (isbn) REFERENCES books (isbn),
            FOREIGN KEY (member_id) REFERENCES members (member_id)
        )
        """
    )

    conn.commit()
    conn.close()


def get_conn():
    return sqlite3.connect(DB_NAME)


class Book:
    def __init__(self, isbn, title, author, genre, total_copies):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.genre = genre
        self.total_copies = total_copies

    def save(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO books (isbn, title, author, genre, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (self.isbn, self.title, self.author, self.genre, self.total_copies, self.total_copies),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def search(keyword):
        conn = get_conn()
        cur = conn.cursor()
        like = f"%{keyword}%"
        cur.execute(
            """
            SELECT isbn, title, author, genre, total_copies, available_copies
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            """,
            (like, like, like),
        )
        results = cur.fetchall()
        conn.close()
        return results

    @staticmethod
    def all_books():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT isbn, title, author, genre, total_copies, available_copies FROM books")
        results = cur.fetchall()
        conn.close()
        return results

    @staticmethod
    def delete(isbn):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
        conn.commit()
        deleted = cur.rowcount
        conn.close()
        return deleted > 0

    @staticmethod
    def update_availability(isbn, delta):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE books SET available_copies = available_copies + ? WHERE isbn = ?",
            (delta, isbn),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def exists(isbn):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT available_copies FROM books WHERE isbn = ?", (isbn,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None


class Member:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO members (name, email, join_date)
            VALUES (?, ?, ?)
            """,
            (self.name, self.email, datetime.now().strftime("%Y-%m-%d")),
        )
        conn.commit()
        member_id = cur.lastrowid
        conn.close()
        return member_id

    @staticmethod
    def all_members():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT member_id, name, email, join_date FROM members")
        results = cur.fetchall()
        conn.close()
        return results

    @staticmethod
    def exists(member_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
        row = cur.fetchone()
        conn.close()
        return row is not None


class Library:
    @staticmethod
    def issue_book(isbn, member_id):
        available = Book.exists(isbn)
        if available is None:
            return False, "Book not found."
        if available <= 0:
            return False, "No copies available."
        if not Member.exists(member_id):
            return False, "Member not found."

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO issues (isbn, member_id, issue_date, due_date)
            VALUES (?, ?, ?, ?)
            """,
            (isbn, member_id, issue_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d")),
        )
        conn.commit()
        conn.close()

        Book.update_availability(isbn, -1)
        return True, f"Book issued. Due date: {due_date.strftime('%Y-%m-%d')}"

    @staticmethod
    def return_book(issue_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT isbn, due_date, return_date FROM issues WHERE issue_id = ?", (issue_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return False, "Issue record not found."
        if row[2] is not None:
            conn.close()
            return False, "Book already returned."

        isbn, due_date_str, _ = row
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        return_date = datetime.now()

        fine = 0
        if return_date > due_date:
            days_late = (return_date - due_date).days
            fine = days_late * FINE_PER_DAY

        cur.execute(
            "UPDATE issues SET return_date = ?, fine = ? WHERE issue_id = ?",
            (return_date.strftime("%Y-%m-%d"), fine, issue_id),
        )
        conn.commit()
        conn.close()

        Book.update_availability(isbn, 1)

        message = "Book returned."
        if fine > 0:
            message += f" Fine: Rs.{fine}"
        return True, message

    @staticmethod
    def overdue_list():
        conn = get_conn()
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            """
            SELECT i.issue_id, b.title, m.name, i.due_date
            FROM issues i
            JOIN books b ON i.isbn = b.isbn
            JOIN members m ON i.member_id = m.member_id
            WHERE i.return_date IS NULL AND i.due_date < ?
            """,
            (today,),
        )
        results = cur.fetchall()
        conn.close()
        return results

    @staticmethod
    def most_issued_books(limit=5):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT b.title, COUNT(*) as times_issued
            FROM issues i
            JOIN books b ON i.isbn = b.isbn
            GROUP BY i.isbn
            ORDER BY times_issued DESC
            LIMIT ?
            """,
            (limit,),
        )
        results = cur.fetchall()
        conn.close()
        return results

    @staticmethod
    def member_history(member_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT b.title, i.issue_date, i.due_date, i.return_date, i.fine
            FROM issues i
            JOIN books b ON i.isbn = b.isbn
            WHERE i.member_id = ?
            ORDER BY i.issue_date DESC
            """,
            (member_id,),
        )
        results = cur.fetchall()
        conn.close()
        return results


def print_table(rows, headers):
    if not rows:
        print("  (no records found)")
        return

    widths = [
        max(len(str(header)), max((len(str(row[i])) for row in rows), default=0))
        for i, header in enumerate(headers)
    ]
    header_line = " | ".join(str(header).ljust(widths[i]) for i, header in enumerate(headers))
    print("  " + header_line)
    print("  " + "-" * len(header_line))
    for row in rows:
        print("  " + " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)))


def read_int(prompt_message):
    while True:
        try:
            return int(input(prompt_message).strip())
        except ValueError:
            print("Invalid number.")


def add_book_menu():
    print("\n-- Add Book --")
    isbn = input("ISBN: ").strip()
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    genre = input("Genre: ").strip()

    try:
        copies = int(input("Number of copies: ").strip())
    except ValueError:
        print("Invalid number.")
        return

    book = Book(isbn, title, author, genre, copies)
    try:
        book.save()
        print(f"Added '{title}' with {copies} copies.")
    except sqlite3.IntegrityError:
        print("A book with this ISBN already exists.")


def search_book_menu():
    keyword = input("\nSearch keyword (title/author/isbn): ").strip()
    results = Book.search(keyword)
    print_table(results, ["ISBN", "Title", "Author", "Genre", "Total", "Available"])


def list_books_menu():
    results = Book.all_books()
    print("\n-- All Books --")
    print_table(results, ["ISBN", "Title", "Author", "Genre", "Total", "Available"])


def delete_book_menu():
    isbn = input("\nISBN to delete: ").strip()
    if Book.delete(isbn):
        print("Book deleted.")
    else:
        print("No such book.")


def add_member_menu():
    print("\n-- Register Member --")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    member = Member(name, email)
    member_id = member.save()
    print(f"Registered. Member ID: {member_id}")


def list_members_menu():
    results = Member.all_members()
    print("\n-- All Members --")
    print_table(results, ["ID", "Name", "Email", "Joined"])


def issue_book_menu():
    print("\n-- Issue Book --")
    isbn = input("Book ISBN: ").strip()
    member_id = read_int("Member ID: ")
    _, message = Library.issue_book(isbn, member_id)
    print(message)


def return_book_menu():
    print("\n-- Return Book --")
    issue_id = read_int("Issue ID: ")
    _, message = Library.return_book(issue_id)
    print(message)


def overdue_menu():
    results = Library.overdue_list()
    print("\n-- Overdue Books --")
    print_table(results, ["Issue ID", "Title", "Member", "Due Date"])


def most_issued_menu():
    results = Library.most_issued_books()
    print("\n-- Most Issued Books --")
    print_table(results, ["Title", "Times Issued"])


def member_history_menu():
    member_id = read_int("\nMember ID: ")
    results = Library.member_history(member_id)
    print(f"\n-- History for Member {member_id} --")
    print_table(results, ["Title", "Issue Date", "Due Date", "Return Date", "Fine"])



def main():
    init_db()
    actions = {
        "1": add_book_menu,
        "2": search_book_menu,
        "3": list_books_menu,
        "4": delete_book_menu,
        "5": add_member_menu,
        "6": list_members_menu,
        "7": issue_book_menu,
        "8": return_book_menu,
        "9": overdue_menu,
        "10": most_issued_menu,
        "11": member_history_menu,
    }

    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
