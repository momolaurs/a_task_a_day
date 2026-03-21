# a task a day

This is a very straightforward productivity app for serial procrastinators. The idea is: you open it and complete one(1) task from the app, and then you are free. See you tomorrow. 

Steps:
You add a task that needs to be done to a list > from that list, you can complete the different tasks OR you can ask the **oracle**, and it will choose a task for you (once the oracle chooses, you cannot escape; you need to complete it[^1]) > you repeat everything again the next day

---

## Features

- Add, complete, and edit tasks
- Use the oracle: a weighted random task picker
- Storage using SQLite (tasks saved in `tasks.db`)
- Clean, interactive UI with Flet

---

## How the Oracle works

Each task is selected randomly, but older tasks are more likely to be picked.

### Probability formula


P(i) = w_i / Σ(w_j)


Where:
- `P(i)` = probability of selecting task i
- `w_i` = weight of task i
- `Σ(w_j)` = sum of all task weights

### Example

- Task A: 0 days old → weight = 1  
- Task B: 2 days old → weight = 3  
- Task C: 5 days old → weight = 6  

Total weight = 10

Probabilities:
- Task A → 1 / 10  
- Task B → 3 / 10  
- Task C → 6 / 10  


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
