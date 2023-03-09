from bs4 import BeautifulSoup
import re
import os

def clean_html_text(html_text):
    cleantext = BeautifulSoup(html_text, "html.parser")
    text = cleantext.get_text()
    final_text = re.sub(r'\W+', " ", text)
    return final_text

def write_clean_html_text_files(source_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for filename in os.listdir(source_folder):
        if filename.endswith(".html"):
            with open(os.path.join(source_folder, filename), "r") as f:
                html_text = f.read()
    
            clean_text = clean_html_text(html_text)

            with open(os.path.join(dest_folder, os.path.splitext(filename)[0] + ".txt"), "w", encoding='utf-8') as f:
                f.write(clean_text)

    print('done')