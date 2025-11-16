


A minimal and clean backend implementation for a music-streaming platform using **MySQL** and **Python**.
Built for DBMS learning and practical backend design.

---

## **Prerequisites**

Make sure you have:

* **Python 3.10+**
* **MySQL 8.0.4 or above**
* A **Unix-based system** (Linux or macOS)

---

## **Installation & Setup**

Clone the repository:

```bash
git clone https://github.com/me-is-mukul/DBMS-project.git
cd DBMS-project
```

---

## **1. Create the MySQL Database**

Open MySQL and create the database:

```sql
CREATE DATABASE oho;
```

Now import the schema + data:

```bash
mysql -u root -p oho < backup.sql
```

Enter your MySQL password when asked.
This may take a few seconds depending on system speed.

---

## **2. Configure Environment Variables**

In the project root:

```bash
touch .env
```

Open `.env` in any editor and add:

```env
PASSWORD="<YOUR MYSQL PASSWORD>"
```

Make sure it contains **only your password**, nothing else.

---

## **3. Install Python Dependencies**

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
---

## **4. Run the Project**

```bash
python main.py
```
