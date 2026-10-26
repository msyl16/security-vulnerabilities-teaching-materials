import os 
import re

class MarkdownCodeExtractor():
    
    def __init__(self, custom_languages=None):

        if custom_languages == None:
            self.custom_languages = {
                "python": "py",
                "py": "py",
                "javascript": "js",
                "js": "js",
                "css": "css",
                "html": "html",
                "json": "json",
                "bash": "sh",
                "sh": "sh"
            }
        else:
            self.custom_languages = custom_languages

        

        self.code_block_pattern = re.compile(r"```(\w+)\n(.*?)\n```", re.DOTALL) # Pattern to extract code block

    def _get_file_extension(self, programming_language):
        # Einfache Fehlerbehebung mit .txt, falls Sprache nicht im Dictionary enthalten
        return self.custom_languages.get(programming_language.lower(), "txt") ## self.custom_languages[programming_language.lower()]


    
    def _read_file_content(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()



    def _write_code_to_file(self, filepath: str, code: str) -> bool:
        try: 
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
                return True
        except IOError as e:
            print(f"Fehler beim Schreiben von {filepath}: {e}")
            return False


    
    def _get_path_info(self, filepath) -> tuple:
        abs_path = os.path.abspath(filepath)
        directory = os.path.dirname(abs_path)

        filename_with_ext = os.path.basename(abs_path)
        filename = os.path.splitext(filename_with_ext)[0]

        return directory, filename


    # def _generate_file_path(self, directory, base_name, index, extension):
    #     """Generate new "path-name" for extracted code from markdown file."""
    #     target_directory = self.output_dir if self.output_dir else directory
    #     os.makedirs(target_directory, exist_ok=True)

    #     filename = f"{base_name}_{index}_code.{extension}"
    #     return os.path.join(target_directory, filename)
    

    ## Nur als TEST gedacht
    def test_suche(self, text) -> None:
        count_matches = 0

        for match in self.code_block_pattern.finditer(text):
            count_matches += 1
            language = match.group(1)
            code_len = len(match.group(2))
            print(f"Programming Language: {language}, Length of Code: {code_len}.")
        print(f"File has {count_matches} matches.")
    

    def extract_and_save(self, md_filepath: str) -> list:
        """
        Extrahiert alle Codeblöcke und speichert sie in:
        <ordner_der_md_datei>/extracted_code/<dateiname>_block_<nr>.<ext>
        """
        if not os.path.exists(md_filepath):
            raise FileNotFoundError(f"Markdown-Datei existiert nicht: {md_filepath}")

        # Pfade ermitteln
        abs_path = os.path.abspath(md_filepath)
        doc_dir = os.path.dirname(abs_path)
        base_name, _ = os.path.splitext(os.path.basename(abs_path))

        # Neuer Zielordner direkt im selben Verzeichnis: /.../src/doc/extracted_code/
        target_dir = os.path.join(doc_dir, "extracted_code")
        os.makedirs(target_dir, exist_ok=True)

        content = self._read_file_content(abs_path)
        saved_files = []
        code_block_counter = 0

        for match in self.code_block_pattern.finditer(content):
            code_block_counter += 1
            language = match.group(1)
            code_content = match.group(2)

            extension = self._get_file_extension(language)
            file_name = f"{base_name}_block_{code_block_counter}.{extension}"
            target_file_path = os.path.join(target_dir, file_name)

            if self._write_code_to_file(target_file_path, code_content):
                saved_files.append(target_file_path)

        return saved_files