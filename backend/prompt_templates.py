ALLERGENS = [
    "Gluten", "Egg", "Crustaceans", "Fish", "Peanut", "Soy",
    "Milk", "Tree nuts", "Celery", "Mustard"
]
NUTRIENTS = [
    "Energy", "Fat", "Carbohydrate", "Sugar", "Protein", "Sodium"
]

def build_llm_prompt(text: str) -> str:
    schema = {
        "allergens": {a: "present|absent|may_contain|unknown" for a in ALLERGENS},
        "nutrition_per_100g": {n: "value (with unit) or null" for n in NUTRIENTS},
        
    }

    return f"""
The text below describes a food product (possibly in Hungarian or English). Note: You will be receiveing text extracted
from a PDF, which may include formatting issues.
Some documents mark allergens with 'I'/'N' under columns
which represent Igen/Nem (Yes/No) or will put ✔/X under these columns.
For example, if a text containing an allergen is followed by N, that means it's absent. 
You need to interpret these correctly, according to the position in the table, which in your case may be
the position of these titles in the text.
Other documents may use checkboxes (☑,☒,☐) accompanied by words which may
represent title words like "does not contain"/ "contains"/ "not sure"/ "yes(Igen)"/ "no(Nem)". The words may be before
or after the checkbox symbols (mostly before). You need to interpret these correctly as well.
For example, if you encounter a word like "Gluten: ☑", it means Gluten is present.
But if you see "Gluten..... mentes ☒ tartalmaz ☐ előfordulhat ☐", it means Gluten is absent.
In this case, if the word "mentes" (meaning "free from") appears near the checkbox, it indicates absence.
When you encounter title words with checkboxes, treat ☑ and ☒ the same.
Extract the allergens and nutritional values
in valid JSON according to this schema:

{schema}

Rules:
- Return ONLY valid JSON.
- Allergens: use "present", "absent", "may_contain", or "no_data".
- Nutritional values: include numeric value and unit, or null.
- If the text is unclear, fill with null or no_data.
- ONLY return the JSON, nothing else. No explanations. No notes. Nothing extra.


Text:
{text[:6000]}
"""
