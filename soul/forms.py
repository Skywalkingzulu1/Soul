"""Smart form filling — detect field types and fill intelligently.

Analyzes page forms, identifies field purposes (email, password, name, etc.),
and fills them with appropriate values using human-like typing.
"""

import asyncio
import random
import logging

logger = logging.getLogger(__name__)

# Field purpose detection patterns
FIELD_PATTERNS = {
    "first_name": ["first", "fname", "given", "vorname"],
    "last_name": ["last", "lname", "surname", "family", "nachname"],
    "full_name": ["name", "fullname", "full_name", "display"],
    "email": ["email", "e-mail", "mail", "correo", "desired"],
    "username": ["username", "user", "login", "handle", "screen"],
    "password": ["password", "pass", "pwd", "secret", "contrasena"],
    "confirm_password": ["confirm", "again", "repeat", "retype", "reenter"],
    "phone": ["phone", "mobile", "tel", "cell", "number"],
    "day": ["day", "dob_day", "birth_day", "dd"],
    "month": ["month", "dob_month", "birth_month", "mm"],
    "year": ["year", "dob_year", "birth_year", "yyyy", "yy"],
    "date_of_birth": ["birth", "dob", "birthday", "age"],
    "gender": ["gender", "sex"],
    "country": ["country", "nation", "region"],
    "address": ["address", "street", "addr"],
    "city": ["city", "town"],
    "zip": ["zip", "postal", "postcode"],
    "search": ["search", "query", "q", "find"],
    "code": ["code", "otp", "verification", "token", "pin"],
    "agree": ["agree", "accept", "terms", "consent", "tos"],
    "checkbox": ["check", "opt", "newsletter", "subscribe"],
}

def classify_field(field_info) -> None:
    """Determine what a field is for based on its attributes."""
    name = (field_info.get("name") or "").lower()
    placeholder = (field_info.get("placeholder") or "").lower()
    aria = (field_info.get("aria_label") or "").lower()
    label = (field_info.get("label") or "").lower()
    field_id = (field_info.get("id") or "").lower()
    field_type = (field_info.get("type") or "").lower()

    combined = f"{name} {placeholder} {aria} {label} {field_id}"

    # Type-based detection
    if field_type == "email":
        return "email"
    if field_type == "password":
        # Check if it's confirm password
        if any(w in combined for w in FIELD_PATTERNS["confirm_password"]):
            return "confirm_password"
        return "password"
    if field_type == "checkbox":
        return "checkbox"
    if field_type == "search":
        return "search"
    if field_type == "tel":
        return "phone"

    # Name-based detection
    for purpose, patterns in FIELD_PATTERNS.items():
        for pattern in patterns:
            if pattern in combined:
                return purpose

    return "unknown"


async def analyze_form(page) -> None:
    """Analyze all form fields on a page. Returns list of field descriptors."""
    fields = []

    # Get all visible inputs
    inputs = await page.query_selector_all(
        "input:visible, select:visible, textarea:visible"
    )

    for inp in inputs:
        try:
            field_type = await inp.get_attribute("type") or "text"
            if field_type in ("hidden", "submit", "button", "image"):
                continue

            info = {
                "type": field_type,
                "name": await inp.get_attribute("name") or "",
                "id": await inp.get_attribute("id") or "",
                "placeholder": await inp.get_attribute("placeholder") or "",
                "aria_label": await inp.get_attribute("aria-label") or "",
                "tag": await inp.evaluate("el => el.tagName.toLowerCase()"),
                "element": inp,
            }

            # Try to find associated label
            field_id = info["id"]
            if field_id:
                try:
                    label_el = await page.query_selector(f"label[for='{field_id}']")
                    if label_el:
                        info["label"] = await label_el.inner_text()
                except Exception:
                    pass

            if not info.get("label"):
                try:
                    parent = await inp.evaluate(
                        "el => { let l = el.closest('label'); return l ? l.innerText : ''; }"
                    )
                    info["label"] = parent or ""
                except Exception:
                    info["label"] = ""

            info["purpose"] = classify_field(info)
            fields.append(info)

        except Exception:
            continue

    # Get select dropdowns
    selects = await page.query_selector_all("select:visible")
    for sel in selects:
        try:
            info = {
                "type": "select",
                "name": await sel.get_attribute("name") or "",
                "id": await sel.get_attribute("id") or "",
                "aria_label": await sel.get_attribute("aria-label") or "",
                "tag": "select",
                "element": sel,
                "label": "",
            }
            info["purpose"] = classify_field(info)
            fields.append(info)
        except Exception:
            continue

    # Post-process to handle multiple sequential 'day' fields (Day, Month, Year)
    day_indices = [i for i, f in enumerate(fields) if f["purpose"] == "day"]
    if len(day_indices) >= 3:
        if day_indices[2] - day_indices[0] < 5:
            fields[day_indices[0]]["purpose"] = "day"
            fields[day_indices[1]]["purpose"] = "month"
            fields[day_indices[2]]["purpose"] = "year"
            logger.info(f"  [Smart Birthdate] Re-mapped sequential fields to Day/Month/Year")

    return fields


async def fill_form(page, fields, values, typing_delay=50) -> None:
    """Fill form fields with provided values and verification."""
    filled = 0

    for field in fields:
        purpose = field["purpose"]
        if purpose not in values:
            continue

        value = str(values[purpose])
        element = field["element"]
        field_type = field["type"]

        try:
            if field_type == "checkbox":
                if value.lower() in (True, "true", "yes", "1", "on"):
                    await element.check()
                    filled += 1
            elif field_type == "select":
                await element.select_option(value=value)
                filled += 1
            elif field_type == "radio":
                await element.click()
                filled += 1
            else:
                await element.click()
                await element.fill("")
                for char in value:
                    await element.type(char, delay=typing_delay + random.randint(-10, 20))
                
                # Verify
                actual_val = await element.evaluate("el => el.value")
                if actual_val == value or field_type == "password":
                    filled += 1
                    logger.info(f"  [Success] Verified {purpose}")

            await asyncio.sleep(random.uniform(0.2, 0.5))

        except Exception as e:
            logger.warning(f"  [Failure] Failed to fill {purpose}: {e}")

    return filled

async def click_next(page) -> None:
    """Click a Next/Continue/Submit button."""
    for text in ["Check", "Next", "Continue", "Submit", "Sign up", "Create account", "Register", "Done"]:
        try:
            btn = await page.get_by_role("button", name=text, exact=False).first
            if await btn.is_visible():
                logger.info(f"  [Action] Clicking button: {text}")
                await btn.click()
                return True
        except Exception: continue
    return False
