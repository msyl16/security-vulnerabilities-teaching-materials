import pandas as pd
import os
import json
import subprocess



def semgrep_results(paths: list, semgrep_command: list) -> list:
    # Tatsächliche Pfade
    existing_files = [
        p 
        for p in paths
        if os.path.isfile(p)
    ]

    print(f"Bereit zum Scannen: {len(existing_files)} von {len(paths)} Dateien.")

    if not existing_files:
        print("Keine gültigen Dateien gefunden!")
        return []
    

    # Timeout nicht nötig
    full_cmd = semgrep_command + existing_files # [
    #     "--timeout",
    #     "10",  # Max 10 Sekunden pro Datei
    #     "--max-target-bytes",
    #     "1500000",  # Keine Dateien über 1.5 MB
    # ] + existing_files

    # Scan
    run_scan = subprocess.run(full_cmd, capture_output=True, text=True)

    # JSON Teil parsen
    if not run_scan.stdout.strip():
        if run_scan.stderr:
            print(f"Semgrep stderr: {run_scan.stderr}")
        return []

    try:
        output_data = json.loads(run_scan.stdout)
        return output_data.get("results", [])
    except json.JSONDecodeError:
        print("Output von Semgrep konnte als JSON nicht gelesen werden.")
        print(run_scan.stdout[:500])
        return []


def semgrep_results_to_dataframe(results: list) -> pd.DataFrame:
    """
    Ergebnisse aus Semgrep werden strukturiert,
    sodass Ergebnisse in ein DataFrame übertragen werden können.
    """
    processed_data = []

    for item in results:

        ## Dictionaries in Dictionaries
        extra = item.get("extra", {})
        metadata = extra.get("metadata", {})
        start = item.get("start", {})
        end = item.get("end", {})

        entry = {
            # Direkter Zugriff 
            "check_id": item.get("check_id"),
            "path": item.get("path"),
            "severity": extra.get("severity"),
            "message": extra.get("message"),
            
            # start und end
            "start_line": start.get("line"),
            "start_col": start.get("col"),
            "end_line": end.get("line"),
            "end_col": end.get("col"),
            
            # extra 
            "lines": extra.get("lines"),
            "fingerprint": extra.get("fingerprint"),
            
            # metadata
            "category": metadata.get("category"),
            "cwe": metadata.get("cwe"),
            "owasp": metadata.get("owasp"),
            "technology": metadata.get("technology"),
            "confidence": metadata.get("confidence"),
            "impact": metadata.get("impact"),
            "likelihood": metadata.get("likelihood"),
            "vulnerability_class": metadata.get("vulnerability_class"),
            "references": metadata.get("references"),
        }
        
        processed_data.append(entry)

    # Umwandlung in ein DataFrame
    return pd.DataFrame(processed_data)




# def preprocessing_json_format_to_dataframe(results_from_semgrep: dict):

#     ### All relevant attributes of semgrep result
#     check_id = results_from_semgrep["check_id"]
#     path = results_from_semgrep["path"]
#     start_line = results_from_semgrep["start"]["line"]
#     start_col = results_from_semgrep["start"]["col"]
#     start_offset = results_from_semgrep["start"]["offset"]
#     end_line = results_from_semgrep["end"]["line"]
#     end_col = results_from_semgrep["end"]["col"]
#     end_offset = results_from_semgrep["end"]["offset"]

#     message = results_from_semgrep["extra"]["message"]
#     category = results_from_semgrep["extra"]["metadata"]["category"]
#     cwe = results_from_semgrep["extra"]["metadata"]["cwe"]
#     owasp = results_from_semgrep["extra"]["metadata"]["owasp"]
#     references = results_from_semgrep["extra"]["metadata"]["references"]
#     technology = results_from_semgrep["extra"]["metadata"]["technology"]
#     subcategory = results_from_semgrep["extra"]["metadata"]["subcategory"]
#     likelihood = results_from_semgrep["extra"]["metadata"]["likelihood"]
#     impact = results_from_semgrep["extra"]["metadata"]["impact"]
#     confidence = results_from_semgrep["extra"]["metadata"]["confidence"]
#     license = results_from_semgrep["extra"]["metadata"]["license"]
#     vulnerability_class = results_from_semgrep["extra"]["metadata"]["vulnerability_class"]
#     source = results_from_semgrep["extra"]["metadata"]["source"]
#     shortlink = results_from_semgrep["extra"]["metadata"]["shortlink"]
#     severity = results_from_semgrep["extra"]["severity"]
#     fingerprint = results_from_semgrep["extra"]["fingerprint"]
#     lines = results_from_semgrep["extra"]["lines"]
#     validation_state = results_from_semgrep["extra"]["validation_state"]
#     engine_kind = results_from_semgrep["extra"]["engine_kind"]