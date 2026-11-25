# Tonight on your Windows PC (about 60–90 minutes)

Every command below goes into **PowerShell**. To open it: press the **Windows key**, type `PowerShell`, press **Enter**. To paste: **right-click** in the window or press **Ctrl+V**, then press **Enter**. Run one block at a time and wait for it to finish.

When a step says **"close and reopen PowerShell"**, type `exit`, press Enter, and open it again the same way. That reloads newly installed programs.

---

## Step 1. Replace the Alpaca keys (5 min, browser)
The old keys were pasted into a chat, so treat them as exposed.
1. Go to app.alpaca.markets and log in.
2. Make sure the account switcher at the top left says **Paper**.
3. In the **API Keys** box on the right of the home page, click **Regenerate**.
4. Copy the new **Key** and **Secret** into your password manager now. The secret is shown only once.

## Step 2. Install the tools (15 min)
Paste each line, press Enter, and type `Y` then Enter if it asks to agree to terms.
```powershell
winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.12 -e --source winget
```
If PowerShell says `winget` is not recognized: open the **Microsoft Store**, search **App Installer**, click **Update** or **Get**, then try again.

Close and reopen PowerShell, then install Claude Code:
```powershell
irm https://claude.ai/install.ps1 | iex
```
Close and reopen PowerShell, then check all three. Each should print a version number:
```powershell
git --version
py --version
claude --version
```
If any says "not recognized", close and reopen PowerShell once more. If it still fails, copy the exact message to Claude.

## Step 3. Set your Git identity (2 min)
1. In the browser on github.com (logged in as **jon-swill**), click your profile picture (top right) → **Settings** → **Emails**.
2. Tick **Keep my email addresses private**. Copy the address shown that ends in `@users.noreply.github.com`.
3. Back in PowerShell, paste these, replacing the email with the one you copied:
```powershell
git config --global user.name "Jonathan Swill"
git config --global user.email "PASTE-YOUR-NOREPLY-ADDRESS"
git config --global init.defaultBranch main
```

## Step 4. Create the empty repo on GitHub (3 min, browser)
Go to **github.com/new** and set:
- **Owner:** `jon-swill`
- **Repository name:** `family-desk`
- **Private**
- **Add README:** Off · **Add .gitignore:** None · **Add license:** None (the kit already has its own `.gitignore`)

Click **Create repository**. Leave that page open.

## Step 5. Unpack the kit into a code folder (5 min)
Keep code out of OneDrive, because OneDrive would sync your `.env` keys to the cloud. Make a folder and find the zip:
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\code" | Out-Null
Get-ChildItem "$env:USERPROFILE\Desktop", "$env:USERPROFILE\OneDrive\Desktop", "$env:USERPROFILE\Downloads" -Filter "family-desk-starter-v2.zip" -ErrorAction SilentlyContinue | Select-Object FullName
```
It prints the full path of the zip. Copy that path (select it with the mouse, then right-click) into the next command in place of `PASTE-ZIP-PATH`, keeping the quotes:
```powershell
Expand-Archive -Path "PASTE-ZIP-PATH" -DestinationPath "$env:USERPROFILE\code\family-desk"
cd "$env:USERPROFILE\code\family-desk"
dir
```
You should see `CLAUDE.md`, `README.md`, `TONIGHT.md` and a `docs` folder. Use **v2** of the zip; delete the older `family-desk-starter.zip` from your Desktop.

## Step 6. Connect it to GitHub, with a guard (5 min)
```powershell
git init
git remote add origin https://github.com/jon-swill/family-desk.git
```
Now add the guard that blocks this repo from ever pushing anywhere except your account. Paste this whole block at once:
```powershell
$hook = @'
#!/bin/sh
case "$2" in
  https://github.com/jon-swill/*|git@github.com:jon-swill/*) exit 0 ;;
  *) echo "BLOCKED: family-desk may only push to github.com/jon-swill"; exit 1 ;;
esac
'@
[IO.File]::WriteAllText("$PWD\.git\hooks\pre-push", $hook.Replace("`r`n", "`n"))
```
First commit and push:
```powershell
git add -A
git commit -m "Starter kit v2: PRD, RETRO, research, compliance, skills"
git push -u origin main
```
A browser window opens asking you to sign in to GitHub. Sign in as **jon-swill** and click **Authorize**. Refresh the GitHub repo page; your files should be there.

## Step 7. Python environment and your keys (5 min)
```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```
If asked to confirm the execution-policy change, type `Y` and press Enter. Your prompt now starts with `(.venv)`.

Create the keys file:
```powershell
notepad .env
```
Notepad asks **"Do you want to create a new file?"** Click **Yes**. Type these four lines, using your **new** paper key and secret from Step 1:
```
APCA_API_KEY_ID=your-new-paper-key
APCA_API_SECRET_KEY=your-new-paper-secret
APCA_PAPER=true
SEC_USER_AGENT=Jonathan Swill your-personal-email
```
Press **Ctrl+S**, then close Notepad. Check that Git ignores the file:
```powershell
git check-ignore .env
```
It must print `.env`. If it prints nothing, stop and tell Claude before doing anything else.

## Step 8. Start Claude Code (5 min)
```powershell
claude
```
- If asked whether to trust the folder, choose **Yes**.
- If asked to log in, a browser opens: sign in with your **personal** Claude account.
- Type `/status` and press Enter to confirm it shows your personal account.

## Step 9. Plan and start Phase 1 (rest of the evening)
In Claude Code, paste:
```
Read CLAUDE.md, docs/HANDOFF.md and docs/MASTER_BRIEF.md. Then use the phase-plan skill to plan Phase 1 exactly as defined in docs/HANDOFF.md under "Phase 1 definition".
```
When the plan is written, paste:
```
Use the plan-review skill on the Phase 1 plan.
```
If the review says **READY**, type:
```
/run-phase
```
It works one task at a time, commits locally, never pushes, and stops to ask you before anything involving keys, money or the cloud. Push its work yourself when you're ready, with `git push`.

To stop for the night, press **Ctrl+C** twice. To pick up later:
```powershell
cd "$env:USERPROFILE\code\family-desk"
.\.venv\Scripts\Activate.ps1
claude --continue
```
