import sqlite3
import os
from PyPDF2 import PdfReader
import json

#path

PDF_FOLDER ="data/industrial-safety-pdfs"
SOURCES_JSON ="data/sources.json"
DB_PATH ="chunks.db"
vector_counter = 0

# mapping from url to folder

url_to_file = {
    "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32023R1230": "CELEX_32023R1230_EN_TXT.pdf",
    "https://literature.rockwellautomation.com/idc/groups/literature/documents/sp/oem-sp123_-en-p.pdf": "oem-sp123_-en-p.pdf",
    "https://www.osha.gov/sites/default/files/publications/osha3170.pdf": "osha3170.pdf",
    "https://www.sick.com/media/docs/8/78/678/special_information_guide_for_safe_machinery_en_im0014678.pdf": "special_information_guide_for_safe_machinery_en_im0014678.pdf",
    "https://www.sick.com/media/docs/6/06/606/special_information_safety_guide_for_the_americas_en_im0032606.pdf": "special_information_safety_guide_for_the_americas_en_im0032606.pdf",
    "https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/safebk-rm002_-en-p.pdf": "safebk-rm002_-en-p.pdf",
    "https://search.abb.com/library/Download.aspx?DocumentID=2TLC172003B02002": "EN_ISO_13849-1_2TLC172003B02002.pdf",
    "https://www.dguv.de/medien/ifa/en/pra/softwa/sistema/kochbuch/sistema_cookbook1_end.pdf": "sistema_cookbook1_end.pdf",
    "https://www.dguv.de/medien/ifa/en/pub/rep/pdf/reports-2019/report0217e/rep0217e.pdf": "rep0217e.pdf",
    "https://publikationen.dguv.de/widgets/pdf/download/article/4894": "4894.pdf",
    "https://www.emerson.com/documents/automation/brochure-machine-safety-guide-pneumatic-solutions-en-7073434.pdf": "brochure-machine-safety-guide-pneumatic-solutions-en-7073434.pdf",
    "https://www.eaton.com/content/dam/eaton/markets/machinebuilding/service-and-support/documents/eaton-safety-manual-pu05907001z-en-us.pdf": "eaton-safety-manual-pu05907001z-en-us.pdf",
    "https://www-group.slac.stanford.edu/esh/eshmanual/references/toolsGuideMachineGuardOptions.pdf": "toolsGuideMachineGuardOptions.pdf",
    "https://www.osha.gov/sites/default/files/2020-05/Machine%20Guarding%20Checklist.pdf": "oshaMachine Guarding Checklist.pdf",
    "https://www.osha.gov/sites/default/files/publications/osha3157.pdf": "osha3157.pdf",
    "https://www.certifico.com/component/attachments/download/11114": "getting_started11114.pdf",
    "https://www.dguv.de/medien/ifa/en/pub/rep/pdf/rep07/biar0208/rep22008e.pdf": "rep22008e.pdf",
    "https://www.rae.ca/wp-content/uploads/GuidelinesForSafeMachinery.pdf": "GuidelinesForSafeMachinery.pdf",
    "https://www.lcautomation.com/wb_documents/pilz/sil%20or%20pl%2C%20what%20is%20the%20difference.pdf": "sil or pl, what is the difference.pdf",
    "https://www.libertyelectricproducts.com/downloads/Schmersal-Machine-Guarding-Safety-Products.pdf": "Schmersal-Machine-Guarding-Safety-Products.pdf"
}


#connect to sqllite

conn=sqlite3.connect(DB_PATH)
c=conn.cursor()

#create Table

c.execute('''
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    pdf_title TEXT,
    pdf_url TEXT,
    chunk_text TEXT,
    chunk_len INTEGER,
    vector_index INTEGER
)
''')

conn.commit()

# load souces.json
with open(SOURCES_JSON,'r',encoding='utf-8') as f:
    sources=json.load(f)

# function to split Text in to Chunks

def split_into_chunks(text, chunk_size=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
      
    return chunks

#process PDFs

for src in sources:
    filename = url_to_file[src['url']]
    pdf_path=os.path.join(PDF_FOLDER,filename)
    if not os.path.exists(pdf_path):
        print(f"{pdf_path} not found!")
        continue
    reader=PdfReader(pdf_path)
    full_text=""
    for page in reader.pages:
        full_text+= page.extract_text()+"\n"
    chunks=split_into_chunks(full_text)
    #print(len(chunks))
    for chunk in chunks:
        c.execute("INSERT INTO chunks(pdf_title,pdf_url,chunk_text,chunk_len,vector_index) VALUES(?,?,?,?,?)",
                  (src['title'],src['url'],chunk,len(chunk.split()),vector_counter))
        vector_counter += 1
conn.commit()
conn.close()
print("PDF chunked and saved to SQLite")