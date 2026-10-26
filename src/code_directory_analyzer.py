import os
import re
from .markdown_code_extractor import MarkdownCodeExtractor


# Relevante Quellen für die Bearbeitung / spätere Bearbeitungen
# https://janakiev.com/blog/python-filesystem-analysis/
# https://medium.com/softtechas/how-to-do-eda-on-code-data-633411387e4f




class CodeDirectoryAnalyzer():
    def __init__(self, config=None):

        self.config = config or {}

        self.primary_code_map = self.config.get("primary_code", {})
        self.view_template_map = self.config.get("view_templates", {})
        self.config_map = self.config.get("configurations", {})

        self.all_supported_extensions = {
                    **self.primary_code_map,
                    **self.view_template_map,
                    **self.config_map
                }
        


    def _get_comment_syntax(self, programming_language: str):
        if  programming_language in [
            "HTML", "CSS", "JSON", "YAML",
            "TOML", "Certificate", "Key/Cert", "PublicKey", "Markdown"
            ]:
            return None
        
        elif programming_language in [
            "Python", "Shell", "Ruby", "Perl",
            "Config", "Env", "INI", "Batch", "PowerShell"
            ]:
            return "hash"
        
        elif programming_language in [
            "Java", "JavaScript", "TypeScript", 
            "JavaScript (React)", "TypeScript (React)",
            "Go", "Rust", "PHP", "C#", "Vue"
        ]:
            return "slash"

        elif programming_language in ["SQL"]:
            return "dash"
        return None


    def _classify_category(self, ext_lower: str) -> str:
            """Kategorisierung der einzelnen Dateien."""
            if ext_lower in self.primary_code_map:
                return "primary_code"
            
            elif ext_lower in self.view_template_map:
                return "view"
            
            elif ext_lower in self.config_map:
                return "configuration"
            
            elif ext_lower == ".md":
                return "documentation"
            
            return "unknown"




    def _count_lines(self, lines: list) -> int:
        return len(lines)
    
    def _count_normal_comment_lines(self, lines: list, comment_syntax: str) -> int:
            counter = 0
            if comment_syntax == "slash":
                for line in lines:
                    if line.strip().startswith("//"):
                        counter += 1
            elif comment_syntax == "hash":
                for line in lines:
                    if line.strip().startswith("#"):
                        counter += 1
            elif comment_syntax == "dash":
                for line in lines:
                    if line.strip().startswith("--"):
                        counter += 1
            return counter
    

    def _count_block_comment_lines(self, content: str, comment_syntax: str) -> int:
        counter = 0
        if comment_syntax == "slash":
            block_comments = re.findall(r"/\*.*?\*/", content, flags=re.DOTALL)
            for block in block_comments:
                counter += len(block.splitlines())
        return counter

    

    def _lines_of_code(self, lines: list, total_lines: int, comment_lines: int) -> int:
        empty_rows = sum(1 for line in lines if not line.strip())
        return max(0, total_lines - comment_lines - empty_rows)

    
    
    def _count_words_in_file(self, content: str) -> int:
        return len(re.findall(r"\w+", content))

    

    def _count_words_in_comment(self, content: str, comment_syntax: str) -> int:
            comment_text = ""
            if comment_syntax == "hash":
                comment_text = " ".join(re.findall(r"#.*", content))
            elif comment_syntax == "slash":
                slash = re.findall(r"//.*", content)
                block = re.findall(r"/\*.*?\*/", content, re.DOTALL)
                comment_text = " ".join(slash) + " " + " ".join(block)
            elif comment_syntax == "dash":
                comment_text = " ".join(re.findall(r"--.*", content))

            return len(re.findall(r"\w+", comment_text))

    

    def _count_words_in_code(self, content: str, comment_syntax: str) -> int:
        return max(0, self._count_words_in_file(content) 
                   - self._count_words_in_comment(content, comment_syntax))
    
    
    def _get_attributes_of_each_file(self, filepath: str, comment_syntax: str) -> dict:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            lines = content.splitlines()

            loc = self._count_lines(lines)
            ncl = self._count_normal_comment_lines(lines, comment_syntax) + self._count_block_comment_lines(content, comment_syntax)
            lloc = self._lines_of_code(lines, loc, ncl)

            return {
                "lines_of_code": loc,
                "logical_lines_of_code": lloc,
                "number_comment_line": ncl,
                "character_count_all": self._count_words_in_file(content),
                "character_count_code": self._count_words_in_code(content, comment_syntax),
                "character_count_comment": self._count_words_in_comment(content, comment_syntax)
            }
        except Exception as e:
            print(f"Fehler bei {filepath}: {e}")
            return {
                "lines_of_code": 0,
                "logical_lines_of_code": 0, 
                "number_comment_line": 0,
                "character_count_all": 0, 
                "character_count_code": 0, 
                "character_count_comment": 0
            }

        

    def analyze_directory(self, path_of_data: str) -> list:
        daten = []
        processed_files = set()
        extractor = MarkdownCodeExtractor()

        for dirpath, dirnames, filenames in os.walk(path_of_data):
        
            dirnames[:] = [
                d for d in dirnames 
                if d != "extracted_code" and not d.endswith("DS_Store") # or d.endswith("gitignore") or d.startswith("."))
            ]
            
            for file in filenames:
                if file.endswith("DS_Store"): # or file.endswith("gitignore") or file.startswith("."):
                    continue
                    
                abs_path = os.path.abspath(os.path.join(dirpath, file))
                if abs_path in processed_files:
                    continue
                processed_files.add(abs_path)
                
                _, ext = os.path.splitext(file)
                ext_lower = ext.lower()

                #### MARKDOWN DATEIEN ####
                if ext_lower == ".md":
                    try:
                        extracted_paths = extractor.extract_and_save(abs_path)
                    except Exception as e:
                        print(f"Extraktion fehlgeschlagen für {file}: {e}")
                        extracted_paths = []

                    for ext_path in extracted_paths:
                        ext_abs_path = os.path.abspath(ext_path)
                        processed_files.add(ext_abs_path)
                        
                        ext_file_name = os.path.basename(ext_abs_path)
                        _, ext_only = os.path.splitext(ext_file_name)
                        
                        language = self.all_supported_extensions.get(ext_only.lower(), ext_only)
                        comment_syntax = self._get_comment_syntax(language)
                        code_attribute = self._get_attributes_of_each_file(ext_abs_path, comment_syntax)
                        
                        try:
                            file_size_byte = os.path.getsize(ext_abs_path)
                        except OSError:
                            file_size_byte = 0

                        rel_path = os.path.relpath(abs_path, path_of_data)
                        name_hauptordner = rel_path.split(os.sep)[0] if rel_path else ""

                        datei_daten = {
                            "name_source": name_hauptordner,
                            "source_markdown": file,             # z.B. datei.md
                            "name_file": ext_file_name,          # z.B. datei_block_1.py
                            "id_file": ext_abs_path,             # .../doc/extracted_code/datei_block_1.py
                            "programming_language": f"{language}",
                            "file_size_byte": file_size_byte,
                            "file_size_mb": file_size_byte / (1024 * 1024),
                            "item_type": self._classify_category(ext_only),
                            **code_attribute
                        }
                        datei_daten.update(code_attribute)
                        daten.append(datei_daten)
                    
                    continue  # Die Original-Markdown-Datei selbst nicht zählen

                #### NORMALE CODE-DATEIEN ####
                language = self.all_supported_extensions.get(ext_lower, ext_lower)
                comment_syntax = self._get_comment_syntax(language)
                code_attribute = self._get_attributes_of_each_file(abs_path, comment_syntax)
                
                try:
                    file_size_byte = os.path.getsize(abs_path)
                except OSError:
                    file_size_byte = 0

                rel_path = os.path.relpath(abs_path, path_of_data)
                name_hauptordner = rel_path.split(os.sep)[0] if rel_path else ""

                datei_daten = {
                    "name_source": name_hauptordner,
                    "source_markdown": None,
                    "name_file": file,
                    "id_file": abs_path,
                    "programming_language": language,
                    "file_size_byte": file_size_byte,
                    "file_size_mb": file_size_byte / (1024 * 1024),
                    "item_type": self._classify_category(ext_lower), # hier war der eigentliche fehler
                    **code_attribute
                }
                datei_daten.update(code_attribute)
                daten.append(datei_daten)

        return daten