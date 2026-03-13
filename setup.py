import subprocess
import sys

def download_spacy_model():
    try:
        import spacy
        spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

download_spacy_model()
