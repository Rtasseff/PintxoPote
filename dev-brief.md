# PintxoPote · Dev Brief (AI‑gen Coding)

## 1. Project Overview
| Item | Decision |
|------|----------|
| **Working name** | PintxoPote |
| **Primary goal** | Record notes on pintxo bars while visiting, look them up on‑street, optionally share with a few friends |
| **Intended users** | You + 3 friends (initial), public read‑only later |
| **Privacy / Edit rights** | Content may be public, but editing rights stay with owner via admin token |
| **Long‑term vision** | Personal tool first; could later be opened to tourists |

---

## 2. Core Features (MVP)
| Feature | Details |
|---------|---------|
| Entry form | All fields shown, single **Save** button |
| Search / filter priority | 1️⃣ Name search (live)<br>2️⃣ Caña price filter<br>3️⃣ Tag<br>4️⃣ Street<br>5️⃣ Price range |
| Views | Home: Searchable / sortable **list** for MVP; map view slated for v2<br> Bar: Single scrolling panel showing (in order) Name, Address, Notes, other fileds, srolling Photos<br> Add Bar: Simple form to add a Bar showing all visible properties and denoting requiered fields |
| Connectivity | Assume online |
| Sharing | One public URL (read‑only) |
| Quick actions | Quick Note & Quick Photo buttons (append, never overwrite) |
| PWA | Installable icon via manifest & service‑worker |

---

## 3. Data Model
| Field | Type | Required | Visible |
|-------|------|----------|---------|
| id | UUID (auto) | ✓ | — |
| Name | Text | ✓ | ✓ |
| Address | Text | ✓ | ✓ |
| Latitude | Float | auto | — |
| Longitude | Float | auto | — |
| Map Link | URL |  | ✓ |
| Specialties | Text |  | ✓ |
| Price Range | Enum €/€€/€€€ |  | ✓ |
| Caña Price | Decimal (€) |  | ✓ |
| Crowd Level | Enum quiet/medium/crowded |  | ✓ |
| Last Visited | Date |  | ✓ |
| Tags | Pre‑defined list |  | ✓ |
| Notes | Long text | ✓ | ✓ |
| Photos | List of URLs |  | ✓ |

*Storage:* SQLite    *Visit history:* simple overwrite    *Tag list:* predefined config.

---

## 4. User Flows (MVP)
| Flow | Interaction |
|------|-------------|
| **Add** | Floating “＋” on list → form → Save |
| **Edit** | Detail → Edit → fields pre‑filled |
| **Quick Note / Photo** | Buttons on detail append text or image |
| **Search** | Global bar on list |
| **Filter** | Icon opens slide‑in panel (caña slider, tag chips, etc.) |
| **Share** | Public app URL; each detail view shareable |

---

## 5. User Story (MVP)
### Primary Use-Case 
1) Opens app to find Home view with list of bars.
2) Filter, sort and/or search list to navigate to a specific bar.
3) Select Bar and be directed to Bar view.
4) Review Bar name, address, notes and other fields by scrolling.
5) Further scrolling to view Bar photos. 
6) (if NOT read-only) Select a Quick Note action to easily append aditional info to existing Note field for this Bar. Save and redirect to Bar view.
7) (if NOT read-only) Select a Quick Photo action to use the devices native controls to snap or select a new photo to add to list of existing Photos. Save and redirect to Bar view.
8) (if NOT read-only) Select Edit button to edit any field for this Bar. Save and redirect to Bar view.
9) Back button to navigate back to Home view with list having the same sort and/or filter options as before navigating to bar in step 3. 

### Add Bar
1) Open app to find Home view with list of bars.
2) Select floating "+" to be directed to Add Bar view.
3) Fill in form and save to open Bar view for newly added. 

---

## 6. Tech Stack & Deployment
| Layer | Choice |
|-------|--------|
| Backend | **Django** + SQLite |
| Front‑end | HTMX + Tailwind (no build) |
| Photo storage | `/static/uploads` |
| Auth | Admin token via env var |
| Hosting | Railway (auto‑deploy on push) |
| PWA | manifest.json + minimal SW |

---

## 7. AI‑gen Coding & Repo Workflow
| Topic | Decision |
|-------|----------|
| Repo | GitHub (private) |
| Branch model | `main` + feature branches | 
| AI tools | Claude Code (generate) + Copilot (edit) |
| Context | Paste dev‑brief into Claude prompts |
| Tests | Required for logical features |
| Commits | Conventional Commits; PRs approved by owner |
| Env | `python -m venv`, requirements.txt |
| CI/CD | Auto‑deploy to Railway on push to `main` |
| Secrets | Stored as Railway env vars (ADMIN_TOKEN, etc.) |