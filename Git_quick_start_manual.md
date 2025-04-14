# 🧠 Git Quick Start Manual for Team Members

This guide will help you contribute to the project using Git and GitHub — no prior experience needed!

---

## ✅ 1. Clone the Repository

```bash
git clone https://github.com/tuchau1404/Aruco_Marker_car-
cd Aruco_Marker_car-
```

---

## ✅ 2. Switch to Your Assigned Branch

```bash
git checkout feature/aruco-detection
```

If the branch isn’t available locally:

```bash
git fetch
git checkout -b feature/aruco-detection origin/feature/aruco-detection
```

---

## ✅ 3. Make Changes

Edit or create files for your node, for example:

```bash
code .   # if using VS Code
```

---

## ✅ 4. Save Your Work (Commit)

```bash
git add .
git commit -m "Add ArUco marker detection logic"
```

---

## ✅ 5. Upload Your Changes (Push) (Stop at Step 5)

```bash
git push origin feature/aruco-detection
```

---

## ✅ 6. Create a Pull Request (PR)

1. Go to your repo on GitHub in a browser.
2. Click **"Compare & pull request"**.
3. Set:
   - **Base** = `dev`
   - **Compare** = `feature/aruco-detection`
4. Add a title and short description.
5. Click **Create Pull Request**.

---

## ✅ Common Git Commands

| Task                        | Command                                      |
|-----------------------------|----------------------------------------------|
| Check current branch        | `git branch`                                 |
| See file changes            | `git status`                                 |
| Temporarily save work       | `git stash`                                  |
| Restore saved work          | `git stash pop`                              |
| Update your branch          | `git pull origin feature/aruco-detection`    |

---

## ⚠️ Notes for ROS 2 Projects

- **Do not commit** folders like: `/build`, `/install`, `/log`
- Use `.gitignore` to prevent pushing unnecessary files
- Write clear and short commit messages

---

## 🆘 Need Help?

Contact the team lead or run:

```bash
git --help
```
