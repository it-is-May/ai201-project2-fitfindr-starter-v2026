"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    search_tokens = list(dict.fromkeys(_WORD_RE.findall((description or "").lower())))
    if not search_tokens:
        return []

    requested_size = _size_tokens(size) if size else set()

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if requested_size and not _size_matches(requested_size, listing.get("size")):
            continue

        searchable = " ".join(
            [
                listing.get("title") or "",
                listing.get("description") or "",
                listing.get("category") or "",
                " ".join(listing.get("style_tags") or []),
                listing.get("brand") or "",
            ]
        ).lower()
        score = sum(1 for token in search_tokens if token in searchable)
        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so ties keep their original data order.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


_WORD_RE = re.compile(r"[a-z0-9]+")
# Size tokens keep "." so "US 8" does not match "US 8.5".
_SIZE_TOKEN_RE = re.compile(r"[a-z0-9.]+")


def _size_tokens(size: str) -> set[str]:
    return set(_SIZE_TOKEN_RE.findall(size.lower()))


def _size_matches(requested: set[str], listing_size: str | None) -> bool:
    """True if every requested size token is a whole token of the listing's size.

    "S/M" -> {s, m}, "XL (oversized)" -> {xl, oversized}, "US 9" -> {us, 9}, so
    "s" matches "S/M" but not "US 9", and "l" matches "L/XL" but not "XL".
    "One Size" listings fit anyone and match every request.
    """
    if not listing_size:
        return False
    tokens = _size_tokens(listing_size)
    if {"one", "size"} <= tokens:
        return True
    return requested <= tokens


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item_text = _describe_listing(new_item)
    items = (wardrobe or {}).get("items", [])

    if not items:
        prompt = (
            "You are a thrift-fashion stylist. A shopper is considering buying "
            "this secondhand piece:\n\n"
            f"{item_text}\n\n"
            "They haven't told me what's in their wardrobe, so give general "
            "styling advice: versatile colors that pair well with it, and one or "
            "two outfit concepts built around it, including shoe and layering "
            "ideas. Keep it concise and practical."
        )
    else:
        wardrobe_text = "\n".join(f"- {_describe_wardrobe_item(i)}" for i in items)
        prompt = (
            "You are a thrift-fashion stylist. A shopper is considering buying "
            "this secondhand piece:\n\n"
            f"{item_text}\n\n"
            "Here is what they already own:\n\n"
            f"{wardrobe_text}\n\n"
            "Recommend 1-2 specific outfit combinations that pair the new piece "
            "with items from their wardrobe. Name the wardrobe pieces they "
            "already own exactly as listed, and only use pieces from that list "
            "(plus basics like shoes if none are listed). Briefly say why each "
            "outfit works."
        )

    response = (generate(prompt) or "").strip()
    return response or (
        f"Couldn't generate outfit ideas for \"{new_item.get('title', 'this item')}\" "
        "this time — try again."
    )


def _describe_listing(listing: dict) -> str:
    parts = [f"{listing.get('title', 'Untitled item')}"]
    if listing.get("category"):
        parts.append(f"category: {listing['category']}")
    if listing.get("colors"):
        parts.append(f"colors: {', '.join(listing['colors'])}")
    if listing.get("style_tags"):
        parts.append(f"style: {', '.join(listing['style_tags'])}")
    if listing.get("condition"):
        parts.append(f"condition: {listing['condition']}")
    if listing.get("description"):
        parts.append(f"details: {listing['description']}")
    return " | ".join(parts)


def _describe_wardrobe_item(item: dict) -> str:
    parts = [item.get("name", "Unnamed item")]
    if item.get("category"):
        parts.append(f"category: {item['category']}")
    if item.get("colors"):
        parts.append(f"colors: {', '.join(item['colors'])}")
    if item.get("style_tags"):
        parts.append(f"style: {', '.join(item['style_tags'])}")
    if item.get("notes"):
        parts.append(f"notes: {item['notes']}")
    return " | ".join(parts)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short social-media caption about the find, using the model.

    Calls `generate()`, so the wording varies between runs (see CACHE_ENABLED
    and TEMPERATURE in config.py if identical inputs give identical captions).

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption that reads like a real post, mentions
        the item, its price and its platform once each, and names the vibe.
        If `outfit` is empty or whitespace, or the model returns nothing, a
        descriptive fallback message is returned instead of raising or "".
    """
    new_item = new_item or {}
    title = new_item.get("title") or "this item"

    if not (outfit or "").strip():
        return (
            f"Couldn't create a fit card for \"{title}\" because there's no "
            "outfit suggestion to base it on."
        )

    price = new_item.get("price")
    price_text = f"${price:.2f}" if isinstance(price, (int, float)) else "price not listed"
    platform = new_item.get("platform") or "an unknown platform"

    prompt = (
        "Write a 2-4 sentence social media caption for a thrift find, the way "
        "someone would actually post it: casual, first person, specific about "
        "the vibe, not a product description. Mention the item, its price and "
        "the platform it was found on once each.\n\n"
        f"Item: {_describe_listing(new_item)}\n"
        f"Price: {price_text}\n"
        f"Platform: {platform}\n\n"
        f"Outfit it's styled in:\n{outfit.strip()}\n\n"
        "Return only the caption."
    )

    caption = (generate(prompt) or "").strip()
    return caption or (
        f"Couldn't generate a fit card for \"{title}\" this time — try again."
    )
