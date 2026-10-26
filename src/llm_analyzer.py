from pathlib import Path
import re

def extract_code_block(text: str) -> str:
    """Extrahiert Code aus Markdown-Blöcken, falls vorhanden, sonst Originaltext."""

    match = re.search(r"```(?:\w+)?\s*\n([\s\S]*?)\n```", text)

    if match:
        return match.group(1).strip()
    return text.strip()



def complete_code(
    client,
    model,
    raw_code: str, 
    language: str, 
    medium: str,
    level: str,
) -> str:
    
    system_prompt = f"""Du bist ein erfahrener Software-Entwickler für {language}.
    Deine Aufgabe ist es, unvollständige Source-Code-Ausschnitte aus 
    Lehrmaterialien syntaktisch zu vervollständigen und lauffähig zu machen.

    Kontext des Materials:
    - Quelle: {medium}
    - Zielgruppe/Level: {level}
    - Programmiersprache: {language}

    Regeln:
    1. Ergänze fehlende Imports/Includes, Variablen, Funktionssignaturen oder Blockabschlüsse, falls diese unvollständig sind.
    2. Verändere die bestehende Logik und Intention des Codes nicht.
    3. Gib den Code in einem einzigen Markdown-Codeblock (```{language.lower()} ... ```) zurück.
    4. Gib keinerlei Erklärungen, Begrüßungen oder Floskeln vor oder nach dem Codeblock aus."""

    user_prompt = f"Vervollständige und repariere folgenden {language}-Codeblock zu einer syntaktisch validen Einheit:\n\n```{language.lower()}\n{raw_code}\n```"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=4096  # Verhindert vorzeitigen Abbruch bei längeren Dateien
    )
    
    content = response.choices[0].message.content
    return extract_code_block(content)




# def complete_code(
#         client,
#         model,
#         raw_code: str, 
#         language: str, 
#         medium: str,
#         level: str,
# ) -> str:

#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     f"Du bist ein Software-Entwickler für {language}."
#                     "Deine Aufgabe ist es, Source Code zu vervollständigen"
#                     "ohne dabei die bestehende Logik zu verändern."

#                     "Der Source Code stammt dabei aus Lehrmaterialien, "
#                     f"die im folgenden Kontext stehen: Quelle = {medium}, Schwierigkeitsgrad = {level}"
#                     f"und in der Programmiersprache = {language} programmiert wurden."

#                     "Gib AUSSCHLIEßLICH den reinen Code zurück – keine Erklärungen, "
#                     "keine Begrüßung und KEINE Markdown-Codeblöcke zurück."
#                 ),
#             },
#             {
#                 "role": "user",
#                 "content": f"Vervollständige folgenden {language}-Code:\n\n{raw_code}",
#             },
#         ],
#         temperature=0.0,

#     )
    
#     content = response.choices[0].message.content.strip()

#     return extract_code_block(content)
