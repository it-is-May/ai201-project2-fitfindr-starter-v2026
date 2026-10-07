# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is an AI agent that takes a user query, searches fashion listings, 
and builds outfit recommendations using saved wardrobe items and fit cards.

Key listing fields identified from `data/listings.json`:
- `id`, `title`, `price`, `size`, `brand`, `color`, `platform`, `description`

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches `data/listings.json` by matching description keywords against titles, descriptions, categories, style tags, and brands, with optional size and inclusive maximum price filters.
- **Inputs:** `description` (str), `size` (str or None — matched case-insensitively against tokenized size sets to handle dual sizes like "S/M" while avoiding substring traps like "s" matching "US 9"; "One Size" matches all queries), `max_price` (float or None)
- **Returns:** A list of matching listing dictionaries (containing fields like `id`, `title`, `price`, `size`, `platform`, `brand`, etc.) sorted by relevance score.
- **When it has nothing:** An empty list `[]`.

### `suggest_outfit`

- **What it does:** Uses the AI model to suggest 1-2 outfit combinations pairing the thrifted item with pieces from the user's wardrobe, or provides general styling advice if the wardrobe is empty.
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Returns:** A non-empty string containing outfit suggestions or styling advice.
- **When it has nothing:** A string containing general styling advice for the item.

### `create_fit_card`

- **What it does:** Uses the AI model to generate a 2-4 sentence social media caption mentioning the item, its price, platform, and overall style vibe.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A string containing the formatted 2-4 sentence caption.
- **When it has nothing:** A descriptive fallback message string explaining that a fit card could not be generated.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list `[]`, set a helpful message in `session["error"]` suggesting what parameter the user could loosen and return early. Otherwise, store the first result in `session["selected_item"]` and continue to `suggest_outfit` and `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query is parsed using pattern matching / string splitting to extract keywords for `description`, size preferences for `size`, and dollar amounts for `max_price`.

**What moves through the session:** 
- `query` (str) — initial natural language request
- `parsed` (dict) — structured query parameters (`description`, `size`, `max_price`)
- `search_results` (list of listing dicts) — matches returned by `search_listings`
- `selected_item` (listing dict or None) — top listing chosen for outfit recommendations
- `wardrobe` (dict with items list) — user's owned clothing pieces
- `outfit_suggestion` (str or None) — styling ideas returned by `suggest_outfit`
- `fit_card` (str or None) — social caption generated by `create_fit_card`
- `error` (str or None) — status or error message if search returned empty or execution halted

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
Found:   Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit:  Hey bestie! As your thrift stylist, I am *obsessed* with this find—a Y2K baby tee with a butterfly print is an absolute staple for the current vintage revival. Because it’s fitted and cropped, it’s going to give you that iconic early 2000s silhouette, and since it runs a little small, it’ll hug you in all the right places.

Here are two killer ways to style your new piece using items already in your closet:

### Look 1: The Ultimate Y2K Streetwear Vibe
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Why it works:** This is the ultimate proportion-play outfit! The fitted, cropped nature of the baby tee balances out the voluminous silhouette of your high-waisted, baggy dark-wash jeans. Throwing on the slightly cropped vintage black denim jacket adds a cool-girl textural contrast while keeping the Y2K energy alive, and the chunky white sneakers tie the whole streetwear aesthetic together seamlessly.

### Look 2: Soft Contrast Crossover
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Wide-leg khaki trousers
* **Outerwear:** Black cropped zip hoodie (worn open or layered over)
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt, Black crossbody bag

**Why it works:** This outfit leans into that cool juxtaposition between sweet and edgy. The delicate, pastel butterfly print on the baby tee softens up the structured, minimalist wide-leg khaki trousers. Adding the black combat boots and the black cropped zip hoodie grounds the look with a touch of grunge, creating a really effortless, high-low style moment.

Both of these are total wins–definitely add this baby tee to your cart!

Fit card: found the ultimate early 2000s butterfly tee on depop for $18 and I honestly might never take it off. the pink and purple print is giving major nostalgic princess vibes and it fits like a literal glove.

2 model calls this session, 1003 prompt + 463 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('jeans size M'))"
[{'id': 'lst_001', 'title': "Vintage Levi's 501 Jeans — Medium Wash", 'description': 'Classic 501s in a perfect medium wash. Some light fading at the knees which adds to the vintage look. No rips or stains.', 'category': 'bottoms', 'style_tags': ['vintage', 'classic', 'denim', 'streetwear'], 'size': 'W30 L30', 'condition': 'good', 'price': 38.0, 'colors': ['blue', 'indigo'], 'brand': "Levi's", 'platform': 'depop'}, {'id': 'lst_009', 'title': 'Platform Mary Janes — Black Patent', 'description': 'Patent leather platform Mary Janes. 1.5 inch platform. Some light scuffing on the toe box but nothing major. UK size 5.', 'category': 'shoes', 'style_tags': ['y2k', 'goth', 'platform', '90s'], 'size': 'US 7', 'condition': 'good', 'price': 55.0, 'colors': ['black'], 'brand': 'Demonia', 'platform': 'depop'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_019', 'title': 'Platform Sneakers — White Chunky Sole', 'description': 'White chunky platform sneakers. Very late 90s / early 2000s energy. Velcro straps. True to size. Some sole yellowing.', 'category': 'shoes', 'style_tags': ['y2k', 'platform', '90s', 'streetwear'], 'size': 'US 8', 'condition': 'good', 'price': 48.0, 'colors': ['white'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_027', 'title': 'Oversized College Crewneck — Faded Red', 'description': 'Classic college-style crewneck in a beautifully faded red. No school name — just a plain athletic crewneck. Roomy fit.', 'category': 'tops', 'style_tags': ['vintage', 'athletic', 'oversized', 'classic'], 'size': 'XL', 'condition': 'good', 'price': 21.0, 'colors': ['red', 'faded red'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_031', 'title': 'Baggy Carpenter Jeans — Dark Wash', 'description': 'Baggy carpenter jeans with hammer loop on the side. Dark wash. Sits at the waist. Major 90s workwear vibes.', 'category': 'bottoms', 'style_tags': ['90s', 'vintage', 'streetwear', 'baggy', 'workwear'], 'size': 'W32', 'condition': 'good', 'price': 36.0, 'colors': ['dark blue', 'indigo'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_034', 'title': 'Bucket Hat — Reversible, Brown Plaid', 'description': 'Reversible bucket hat — plaid on one side, solid tan on the other. Unstructured brim. One size fits most.', 'category': 'accessories', 'style_tags': ['90s', 'streetwear', 'vintage', 'accessories'], 'size': 'One Size', 'condition': 'excellent', 'price': 14.0, 'colors': ['brown', 'tan', 'plaid'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_035', 'title': 'Low-Top Canvas Sneakers — Off-White', 'description': 'Classic low-top canvas sneakers in off-white. Very minimal. Some light yellowing on the sole edges from age. Size 9.', 'category': 'shoes', 'style_tags': ['classic', 'minimal', 'streetwear', 'basics'], 'size': 'US 9', 'condition': 'good', 'price': 20.0, 'colors': ['off-white', 'cream'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_037', 'title': 'Straight Leg Black Jeans — Faded', 'description': 'Faded black straight-leg jeans. Sits at the hips, classic fit. Slightly cropped length. No rips, just natural fading.', 'category': 'bottoms', 'style_tags': ['vintage', 'classic', 'grunge', 'denim'], 'size': 'W28', 'condition': 'good', 'price': 30.0, 'colors': ['black', 'faded black'], 'brand': "Levi's", 'platform': 'thredUp'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey! As your thrift stylist, I give these Vintage Levi's 501 Jeans a resounding **yes**. 501s are the holy grail of denim—they have that rigid, straight-leg fit that only gets better with time, and the light fading at the knees gives them instant character without feeling thrashed. 

Since you already own some great basics and streetwear staples, these jeans will slot right into your rotation. Here are two ways to style your new piece using items straight from your closet:

### Look 1: Off-Duty Streetwear
* **Top:** Oversized grey crewneck sweatshirt
* **Bottoms:** Vintage Levi's 501 Jeans — Medium Wash
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Why it works:** 
This is the ultimate effortless, high-low vintage formula. Because your grey crewneck is *really* oversized and drops below the hip, pairing it with the straight-leg cut of the 501s creates that coveted relaxed, skate-inspired silhouette. Tossing on the chunky white sneakers ties the sporty vibe together, while the black crossbody bag keeps it practical and pulled-together for everyday errands.

### Look 2: Edgy Casual
* **Top:** White ribbed tank top
* **Outerwear:** Vintage black denim jacket
* **Bottoms:** Vintage Levi's 501 Jeans — Medium Wash
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt

**Why it works:**
You can never go wrong with a double-denim moment, especially when mixing black and medium-wash indigo. Tucking the fitted white ribbed tank into the 501s and cinching it with your brown leather belt creates a clean, defined waistline. Layering your slightly cropped vintage black denim jacket over top plays with proportions against the straight-leg jeans, and grounding the whole fit with black combat boots adds a subtle grunge edge.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found these vintage Levi's 501s on depop for $38 and I am never taking them off. They have that exact broken-in medium wash with the best slight fading at the knees. Just threw them on with my favorite white sneakers and the fit is unreal.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to build `_parse_query` in `agent.py` using regex to extract `description`, `size`, and `max_price` from plain-language user search queries.
- *What came back:* The generated function extracted prices and sizes correctly, but its description parser kept filler words like "looking", "for", and "under", causing `search_listings` to fail on fuzzy string matching.
- *What I changed:* I added a `_STOPWORDS` set to filter out conversational filler words and query noise before constructing `parsed["description"]`, ensuring clean search terms reached `search_listings`.

**Moment 2**

- *What I asked for:* I asked Claude to implement `create_fit_card` in `tools.py` using the Gemini model to turn the outfit suggestion and selected listing into a short 2-4 sentence social media caption.
- *What came back:* The model prompt returned long, overly formal paragraphs and occasionally failed when listing fields like `brand` were missing or `None`.
- *What I changed:* I tuned the prompt to strictly request a 2-4 sentence caption and added fallback handling if the model response was empty or unavailable, ensuring the tool always returns a string without throwing an exception.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
