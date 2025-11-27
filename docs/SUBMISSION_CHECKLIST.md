# Submission Checklist
**CA-2 Advanced Programming Techniques**

Samuel Ogunlusi (20086108) & George M. Sherman (20079442)  
**Deadline: December 15, 2025, 23:59**

---

## Before You Submit - Go Through This List!

### 1. Code & Files

- [ ] All Python files present (app.py, models.py, routes.py, repository.py, utils.py, etc.)
- [ ] Templates folder with all 31 HTML files
- [ ] Static folder with CSS file
- [ ] Tests folder with all 4 test files + __init__.py
- [ ] requirements.txt has all dependencies (Flask, SQLAlchemy, email-validator, Werkzeug)
- [ ] **IMPORTANT:** No psycopg2-binary in requirements.txt (we're using SQLite, not PostgreSQL!)
- [ ] Database is SQLite (check app.py line ~28: should say `sqlite:///`)

### 2. Testing

- [ ] Run all tests: `python run_tests.py` - do they all pass?
- [ ] Run the app: `python main.py` - does it start without errors?
- [ ] Can you log in with admin/admin123?
- [ ] Try adding an employee - does it work?
- [ ] Test attendance tracking
- [ ] Test leave request submission and approval
- [ ] Check reports page loads
- [ ] Try exporting data to CSV

### 3. Documentation

- [ ] README.md is complete and makes sense
- [ ] ARCHITECTURE.md has the UML diagrams
- [ ] CA2_REPORT_TEMPLATE.md is filled out (remember: 800-1000 words!)
- [ ] Report includes screenshots (login, dashboard, employees page, attendance, reports, etc.)
- [ ] Week 1-9 concepts are mentioned and explained in the report
- [ ] All external resources attributed properly (mention Flask tutorials, Stack Overflow, GitHub Copilot usage, etc.)

### 4. Report Specifics

- [ ] Assignment Cover Sheet filled out completely (page 1)
- [ ] Both names and student IDs on cover sheet
- [ ] Word count is between 800-1000 words (not including screenshots/appendices)
- [ ] GitHub repository link included
- [ ] Video demonstration link included
- [ ] Report exported as PDF (not Word doc!)

### 5. GitHub Repository

- [ ] Repository is PUBLIC (not private!)
- [ ] Has multiple commits (not just one bulk commit at the end!)
- [ ] Commit messages are meaningful ("Added employee CRUD", not "update" x20)
- [ ] Both team members show up as contributors
- [ ] README.md is in the repo
- [ ] Repository link works when you click it

### 6. Video Demonstration (8-10 Minutes - STRICT!)

- [ ] Video is between 8-10 minutes (not 6, not 12 - they're strict about this!)
- [ ] Shows the application working (login, features, etc.)
- [ ] Code walkthrough (explain models.py, routes.py, key functions)
- [ ] Explain design decisions (why Flask? why MVC? why SQLite?)
- [ ] Show tests running
- [ ] Discuss Week 1-9 concepts implemented
- [ ] Video is uploaded and link works
- [ ] Video is accessible (not private, no download restrictions)

### 7. Folder Structure

Your main folder should be named **20086108** (Samuel's ID) and contain:

```
20086108/
├── app.py
├── main.py
├── models.py
├── routes.py
├── repository.py
├── utils.py
├── config.py
├── init_data.py
├── requirements.txt
├── run_tests.py
├── README.md
├── ARCHITECTURE.md
├── QUICK_START.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── ... (28 other templates)
├── static/
│   └── css/
│       └── style.css
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_utils.py
    ├── test_repository.py
    └── test_integration.py
```

### 8. Creating the ZIP File

- [ ] Main folder is named `20086108`
- [ ] Delete `workflowx.db` before zipping (they'll create their own when testing)
- [ ] Delete `__pycache__` folders if any
- [ ] Delete any backup files (.bak, ~, etc.)
- [ ] Zip the entire `20086108` folder
- [ ] Name the ZIP: `20086108.zip`
- [ ] Test the ZIP - extract it somewhere else and verify everything is there

### 9. Moodle Submission

**BOTH TEAM MEMBERS MUST SUBMIT INDIVIDUALLY!**

What to upload:
1. `20086108.zip` (the code)
2. `Report.pdf` (the report with cover sheet)

Both Samuel and George submit THE SAME FILES.

- [ ] Samuel submits both files
- [ ] George submits both files
- [ ] Check file names are correct
- [ ] Verify files aren't corrupted (download and open them after uploading)
- [ ] Submit BEFORE December 15, 2025, 23:59 (don't wait until the last minute!)

---

## Final Checks (Do This Right Before Submitting!)

- [ ] Run `python init_data.py` in a fresh folder to make sure database setup works
- [ ] Run `python run_tests.py` - all tests pass?
- [ ] Open the PDF report - does it look professional?
- [ ] Click all links in the report - do they work?
- [ ] Watch your video - is audio clear? Screen visible? Right length?
- [ ] Extract your ZIP file and run the app - does it work?

---

## Submission Sign-Off

- [ ] Samuel reviewed everything and is ready to submit
- [ ] George reviewed everything and is ready to submit
- [ ] We double-checked the folder name is `20086108`
- [ ] We're submitting BEFORE the deadline (not at 23:58!)

---

## Common Mistakes to Avoid!

❌ Submitting after deadline (2 marks penalty per day!)  
❌ Using PostgreSQL instead of SQLite  
❌ Report not between 800-1000 words  
❌ Video shorter than 8 minutes or longer than 10  
❌ Repository is private  
❌ Only one team member submits  
❌ Folder named wrong (must be `20086108`)  
❌ ZIP file corrupted or missing files  
❌ No assignment cover sheet  
❌ GitHub repo link doesn't work  

---

**Good luck! You've got this. 🚀**

Once you've checked everything off, you're ready to submit. Remember - both team members need to upload the same files individually on Moodle.
