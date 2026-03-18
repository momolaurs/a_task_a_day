# a task a day

This is a very straightforward productivity app for serial procrastinators. The idea is: you open it and complete one(1) task from the app, and then you are free. See you tomorrow. 

Steps:
You add a task that needs to be done to a list > from that list, you can complete the different tasks OR you can ask the **oracle**, and it will choose a task for you (once the oracle chooses, you cannot escape; you need to complete it[^1]) > you repeat everything again the next day

---

## Features

- Add, complete, and edit tasks
- Weighted random task picker (tasks older in the list are more likely to be selected)
- Storage using SQLite (tasks saved in `tasks.db`)
- Clean, interactive UI with Flet

---

## Libraries / Dependencies

The project uses the following Python libraries:

| Library | Purpose |
|---------|---------|
| `flet` | UI framework |
| `sqlite3` | Built-in Python module for database storage |
| `os` | For handling file paths and locating the database file |
| `datetime` | For timestamps and calculating task age |
| `random` | For weighted random task selection |

## Contact
For any issue, error, bug, or improvement idea feel free to contact the author, Laura Moset Estruch. 

Email: lauramosetestruch@gmail.com or momolaurs@gmail.com|| Linkedin: [HERE](https://www.linkedin.com/in/laura-moset-estruch-56b452237/)



[^1]There is actually nothing forcing you to complete it apart from your conscience, but that should be enough
