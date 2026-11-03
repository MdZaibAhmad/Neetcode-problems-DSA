# NeetCode Grind Ledger

All 973 problems from the NeetCode practice list, each linked to LeetCode, with
solved ticks, a starred revise list, and easy / medium / hard filters.

## Just open index.html

Double-click `index.html`. A card at the top asks where to keep your progress:

- **Create progress.json** — pick a spot, and from that moment every tick and
  star is written into that file.
- **Open an existing file…** — point it at a `progress.json` you already have
  and it loads your progress back out of it.

The page remembers which file you chose. On later visits Chrome asks you to
confirm write access once — the card shows a single **Reconnect progress.json**
button — and then it is reading and writing that same file again.

Between opening the page and clicking that button, your ticks are held in the
browser's own storage, so nothing is ever lost. Whichever copy is newer wins,
and the file is brought up to date immediately.

Needs Chrome or Edge on desktop, which is where the File System Access API
lives. Firefox and Safari fall back to browser storage plus Export / Import,
and the page says so.

## Or run it with the server — no clicks at all

```
python3 server.py
```

Open http://localhost:8765. The server owns `progress.json` in this folder and
writes it atomically on every change, so there is no permission prompt ever.
Pick another port with `python3 server.py 9000`.

## The file

```json
{
  "app": "neetcode-grind-ledger",
  "version": 1,
  "savedAt": "2026-08-26T05:20:14.755Z",
  "solved": ["two-sum", "valid-anagram"],
  "starred": ["trapping-rain-water"]
}
```

Plain JSON keyed by LeetCode slug — copy it between machines, keep it in a git
repo, or delete it to start over.

## What's in the box

- `index.html` — the whole app, no build step and no dependencies
- `server.py` — optional static server with a `/api/progress` read/write endpoint
- `progress.json` — created on your first save
