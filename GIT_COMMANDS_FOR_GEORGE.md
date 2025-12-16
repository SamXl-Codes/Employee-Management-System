# Git Commands Guide for George Sherman
## WorkFlowX Employee Management System - Collaboration Workflow

---

## **1. INITIAL SETUP (First Time Only)**

### STEP 1: Add George as Collaborator on GitHub (SAMUEL MUST DO THIS FIRST!)
```
1. Go to: https://github.com/SamXl-Codes/Employee-Management-System
2. Click "Settings" tab
3. Click "Collaborators" in left sidebar
4. Click "Add people" button
5. Enter George's GitHub username or email
6. Send invitation
7. George must check his email and ACCEPT the invitation
```

### STEP 2: Clone the Repository (George's Computer)
```powershell
# Navigate to where you want the project
cd D:\Projects

# Clone the repository
git clone https://github.com/SamXl-Codes/Employee-Management-System.git

# Navigate into the project folder
cd Employee-Management-System
```

### STEP 3: Configure Git Identity (George's Computer)

#### METHOD 1: Using PowerShell (Recommended for Windows)
```powershell
# Set your name
git config --global user.name "George Sherman"

# Set your email (use the same email as your GitHub account)
git config --global user.email "george.sherman@email.com"

# Verify configuration
git config --list
```

#### METHOD 2: If git config doesn't work, edit the file directly
```powershell
# Open Git config file in Notepad
notepad $env:USERPROFILE\.gitconfig
```

Then add these lines to the file:
```
[user]
    name = George Sherman
    email = george.sherman@email.com
```

Save and close Notepad.

#### METHOD 3: If Git is not installed
```powershell
# Download Git for Windows from: https://git-scm.com/download/win
# Install with default settings
# Restart PowerShell after installation
# Then try METHOD 1 again
```

### STEP 4: Verify Git is Working
```powershell
# Check Git version
git --version

# Check your identity
git config user.name
git config user.email

# Should show:
# George Sherman
# george.sherman@email.com
```

---

## **2. DAILY WORKFLOW COMMANDS**

### Check Current Status
```bash
# See what files have changed
git status

# See which branch you're on
git branch

# See all branches (local and remote)
git branch -a
```

### Get Latest Changes from GitHub
```bash
# Always do this BEFORE starting work
git pull origin main

# Or pull from deployment branch
git pull origin deployment-railway
```

### View Commit History
```bash
# See recent commits
git log --oneline -10

# See detailed commit history
git log

# See commits with file changes
git log --stat

# See who made what changes
git log --pretty=format:"%h - %an, %ar : %s"
```

---

## **3. MAKING CHANGES**

### After Editing Files
```bash
# See what you changed
git status

# See detailed changes in files
git diff

# Add specific file
git add app.py

# Add all changed files
git add .

# Add files in specific folder
git add templates/
```

### Commit Your Changes
```bash
# Commit with message
git commit -m "Add employee search feature"

# Commit with detailed message
git commit -m "Fix dark mode bug in leave requests

- Updated CSS for better contrast
- Fixed table header visibility
- Tested across all browsers"
```

### Push to GitHub
```bash
# Push to main branch
git push origin main

# Push to deployment branch
git push origin deployment-railway

# Force push (CAREFUL - only if you know what you're doing)
git push origin main --force
```

---

## **4. BRANCH MANAGEMENT**

### Working with Branches
```bash
# See current branch
git branch

# Create new branch
git checkout -b feature-attendance-report

# Switch to existing branch
git checkout main

# Switch to deployment branch
git checkout deployment-railway

# Delete branch (after merging)
git branch -d feature-attendance-report
```

### Merging Branches
```bash
# Switch to main branch first
git checkout main

# Merge your feature branch into main
git merge feature-attendance-report

# Push merged changes
git push origin main
```

---

## **5. UNDOING CHANGES**

### Discard Local Changes (Before Commit)
```bash
# Discard changes in specific file
git checkout -- app.py

# Discard all local changes
git reset --hard

# Unstage file (keep changes)
git reset HEAD app.py
```

### Undo Last Commit (Keep Changes)
```bash
# Undo commit but keep files changed
git reset --soft HEAD~1

# Undo commit and unstage files
git reset HEAD~1
```

### View What Changed in Last Commit
```bash
# See files changed
git show --name-only

# See full diff
git show
```

---

## **6. COLLABORATION COMMANDS**

### Check Remote Repository
```bash
# See remote URL
git remote -v

# Fetch latest from GitHub (doesn't merge)
git fetch origin

# See what's different between local and remote
git diff main origin/main
```

### Sync with Samuel's Changes
```bash
# Fetch and merge Samuel's latest changes
git pull origin main

# If there are conflicts, Git will tell you which files
# Edit those files, then:
git add .
git commit -m "Merge Samuel's changes"
git push origin main
```

---

## **7. CHECKING PROJECT DETAILS**

### See File Changes
```bash
# See what files changed in last 5 commits
git log --name-only -5

# See who changed a specific file
git log -- app.py

# See changes in specific file
git diff app.py

# Compare file between branches
git diff main deployment-railway -- app.py
```

### See Contributors
```bash
# See who contributed
git shortlog -sn

# See detailed contributions
git log --pretty=format:"%h %an %s" --graph
```

---

## **8. BEFORE RECORDING VIDEO**

### Verify Everything is Committed
```bash
# Should show "nothing to commit, working tree clean"
git status

# See last 10 commits
git log --oneline -10

# Count total commits
git rev-list --count main

# See all branches
git branch -a
```

### Tag Important Version (Optional)
```bash
# Create tag for submission version
git tag -a v1.0-submission -m "CA2 Final Submission Version"

# Push tag to GitHub
git push origin v1.0-submission

# List all tags
git tag
```

---

## **9. TROUBLESHOOTING**

### If Git Commands Don't Work
```powershell
# Check if Git is installed
git --version

# If not found, download from: https://git-scm.com/download/win

# After installing, restart PowerShell and try again
```

### If "git config" Says Permission Denied
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell icon → "Run as administrator"
# Then try git config commands again
```

### If Git Config File is Locked
```powershell
# Check if file exists
Test-Path $env:USERPROFILE\.gitconfig

# Delete and recreate
Remove-Item $env:USERPROFILE\.gitconfig -Force
git config --global user.name "George Sherman"
git config --global user.email "george.sherman@email.com"
```

### If Push is Rejected (Permission Denied)
```
This means Samuel hasn't added you as collaborator yet!

Samuel needs to:
1. Go to GitHub repo settings
2. Add you as collaborator
3. You must accept the email invitation
4. Then you can push
```

### If GitHub Asks for Login Every Time
```powershell
# Store credentials (Windows)
git config --global credential.helper wincred

# Or use GitHub CLI
# Download from: https://cli.github.com/
gh auth login
```

### If You Get Merge Conflicts
```bash
# Git will show which files have conflicts
# Open those files, look for:
# <<<<<<< HEAD
# your changes
# =======
# Samuel's changes
# >>>>>>> branch-name

# Edit the file to keep what you want
# Then:
git add conflicted_file.py
git commit -m "Resolve merge conflict"
git push
```

### If Git Says "Your branch is behind"
```bash
# Pull the latest changes first
git pull origin main

# Then push your changes
git push origin main
```

### If You Accidentally Commit to Wrong Branch
```bash
# On wrong branch, copy the commit hash
git log --oneline -1

# Switch to correct branch
git checkout main

# Apply that commit here
git cherry-pick <commit-hash>

# Push to correct branch
git push origin main
```

---

## **10. USEFUL SHORTCUTS**

### Quick Status Check
```bash
# Short status format
git status -s

# Show branch and status
git status -sb
```

### Pretty Commit History
```bash
# Graphical branch view
git log --graph --oneline --all

# Detailed with dates
git log --pretty=format:"%h %ad | %s%d [%an]" --date=short
```

### Compare Changes
```bash
# See uncommitted changes
git diff

# See staged changes
git diff --cached

# See changes between commits
git diff HEAD~1 HEAD
```

---

## **IMPORTANT NOTES FOR COLLABORATION:**

### ✅ DO:
- Always `git pull` before starting work
- Commit frequently with clear messages
- Push your changes daily so Samuel can see progress
- Communicate before making major changes
- Test locally before pushing

### ❌ DON'T:
- Don't force push unless absolutely necessary
- Don't commit large binary files (databases, videos, etc.)
- Don't commit passwords or API keys
- Don't delete branches without checking with Samuel
- Don't work on same file simultaneously without coordination

---

## **SPECIFIC WORKFLOW FOR THIS PROJECT:**

### 1. Start Your Work Session
```bash
cd Employee-Management-System
git checkout main
git pull origin main
git status
```

### 2. Make Your Changes
```bash
# Edit files in VS Code
# Test locally (python main.py)
```

### 3. Commit and Push
```bash
git status
git add .
git commit -m "Descriptive message about what you changed"
git push origin main
```

### 4. Deploy to Railway (If Needed)
```bash
git checkout deployment-railway
git merge main
git push origin deployment-railway
git checkout main
```

---

## **QUICK REFERENCE CHEAT SHEET:**

| Command | What It Does |
|---------|-------------|
| `git clone <url>` | Download repository |
| `git pull` | Get latest changes |
| `git status` | See what changed |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Save changes locally |
| `git push` | Upload to GitHub |
| `git log` | See commit history |
| `git branch` | See branches |
| `git checkout <branch>` | Switch branch |
| `git diff` | See file changes |
| `git reset --hard` | Discard all changes |

---

**Repository URL:** https://github.com/SamXl-Codes/Employee-Management-System
**Main Branch:** main
**Deployment Branch:** deployment-railway
**Live App:** https://employee-management-system-production-bf41.up.railway.app/

---

**Questions? Ask Samuel or check:** https://git-scm.com/doc
