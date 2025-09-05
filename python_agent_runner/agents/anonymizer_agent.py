import re

class AnonymizerAgent:
    def __init__(self):
        self.mappings = {}
        self.placeholder_count = 0

    def _replace_match(self, match):
        """A helper method to be called by re.sub."""
        original_text = match.group(0)
        placeholder = f"[SENSITIVE_DATA_{self.placeholder_count}]"
        self.mappings[placeholder] = original_text
        self.placeholder_count += 1
        return placeholder

    def scrub(self, text):
        """
        Finds quoted text and replaces it with a generic placeholder.
        """
        self.mappings = {}
        self.placeholder_count = 0
        print("Anonymizer Agent: Scrubbing text...")
        # Now correctly calls the helper method via self
        scrubbed_text = re.sub(r'\"(.*?)\"', self._replace_match, text)
        print(f"Anonymizer Agent: Scrubbed text is: {scrubbed_text}")
        return scrubbed_text

    def de_anonymize(self, text):
        """
        Restores the original sensitive text from placeholders.
        """
        print("Anonymizer Agent: De-anonymizing text...")
        de_anonymized_text = text
        for placeholder, original in self.mappings.items():
            de_anonymized_text = de_anonymized_text.replace(placeholder, original)
        return de_anonymized_text
