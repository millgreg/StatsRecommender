import pandas as pd
import spacy
import sys

def check_env():
    print(f"Python version: {sys.version}")
    print(f"Pandas version: {pd.__version__}")
    try:
        nlp = spacy.blank("en")
        print("SpaCy initialized successfully.")
    except Exception as e:
        print(f"SpaCy initialization failed: {e}")

if __name__ == "__main__":
    check_env()
