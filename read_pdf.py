import PyPDF2

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            print(f"\nPage {page_num + 1}:")
            print(page.extract_text())

if __name__ == "__main__":
    read_pdf("DEMANDE_DE_RETOUR.pdf") 