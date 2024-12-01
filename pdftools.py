from pypdf import PdfReader, PdfWriter
import tempfile
import shutil
import os


class PdfTools:
    """
    Class to handle pdf files and operations. Relies on pypdf for PDF manipulation.
    """
    def __init__(self):
        super().__init__()
        self.pdf_version = None
        self.obj = None
        self.annotation = None
        self.save_writer = None
        self.temp_copy_path = None
        self.temp_dir = None
        self.temp = None
        self.number_of_pages = None
        self.reader = None
        self.current_folder = os.getcwd()
        self.writer = None
        self.temp_folder = tempfile.TemporaryDirectory()

    @staticmethod
    def append_file(filename1, filename2, save_filename):
        """
        Append file1 to file2 and save new file to given filename.
        :param filename1:
        :param filename2:
        :param save_filename:
        :return: saved filename
        """
        input1 = PdfReader(filename1)
        input2 = PdfReader(filename2)
        merger = PdfWriter()
        merger.append(input1)
        merger.append(input2)
        # write merged file to temp folder and load again
        # new_save_filename = os.path.join(self.temp_folder.name, 'temp_merged.pdf')
        
        with open(save_filename, "wb") as fp:
            merger.write(fp)
        return save_filename

    def create_temporary_copy(self, path):
        """
        Create a temporary copy of the document for manipulation.
        :param path:
        :return: str: temporary copy path
        """
        if self.temp_copy_path:
            self.temp_copy_path = os.path.join(self.temp_folder.name, 'temp_file2.pdf')
        else:
            self.temp_copy_path = os.path.join(self.temp_folder.name, 'temp_file1.pdf')
        shutil.copy2(path, self.temp_copy_path)
        return self.temp_copy_path

    def load_pdf(self, filename):
        """
        Load PDF document in pypdf reader for later manipulation.
        :param filename:
        :return:
        """
        if self.reader:
            del self.reader
        self.reader = PdfReader(filename)
        self.number_of_pages = len(self.reader.pages)
        self.pdf_version = self.reader.pdf_header.replace('%PDF-', '')
        for page in self.reader.pages:
            self.get_annotations(page)
        return self.pdf_version

    def get_annotations(self, page):
        if "/Annots" in page:
            for annot in page["/Annots"]:
                self.obj = annot.get_object()
                self.annotation = {"subtype": self.obj["/Subtype"], "location": self.obj["/Rect"]}
            return self.obj

    def delete_page(self, filename, skip_page, pdf_meta) -> str:
        """
        Delete page from document. PdfWriter.pages emulates a list of PageObject. To remove a page or pages
        you remove a page from the list (through the del operator).
        :param filename:
        :param skip_page:
        :param pdf_meta:
        :return: Info about operation.
        """
        self.writer = PdfWriter()
        self.writer.append_pages_from_reader(self.reader)
        self.writer.add_metadata(pdf_meta)
        if skip_page >= 0 or skip_page <= len(self.reader.pages):
            del self.writer.pages[skip_page]
            with open(filename, "wb") as fp:
                self.writer.write(fp)
            self.load_pdf(filename)  # load updated file
        else:
            return f'Page {skip_page + 1} not available.'
        return f'Page {skip_page + 1} deleted from document.'

    def export_page(self, filename, export_name, page, pdf_meta) -> str:
        """
        Export single page to file
        :param filename:
        :param export_name:
        :param page:
        :param pdf_meta:
        :return: Success/fail message.
        """
        page_to_export = self.reader.pages[page]
        export_pdf = PdfWriter()
        export_pdf.add_page(page_to_export)
        export_pdf.add_metadata(pdf_meta)
        try:
            with open(export_name, "wb") as fp:
                export_pdf.write(fp)
            return f'Page {page} has been exported.'
        except FileNotFoundError as e:
            return f'No export name selected. {e}'

    def rotate_page(self, filename, page, degree):
        """
        Rotate PDF page by multiple of 90 degrees. Negative values for left rotation, positive values for
        right rotation.

        Reads the entire document and writes it in new document, rotates single page.
        This procedure is required to update views in single and multi-page mode.
        :param filename:
        :param page:
        :param degree:
        :return: filename
        """
        if filename:
            self.load_pdf(filename)
        else:
            return f'No file chosen.'
        self.writer = PdfWriter()
        # add all pages from reader to new file and rotate one page
        self.writer.append_pages_from_reader(self.reader)
        self.writer.pages[page].rotate(degree)
        with open(filename, "wb") as fp:
            self.writer.write(fp)
        return filename

    def save_pdf(self, filename, save_filename, pdf_meta) -> str:
        """
        Save PDF document with changes.
        :param filename:
        :param save_filename:
        :param pdf_meta:
        :return: Message about success or failure.
        """
        self.save_writer = PdfWriter()
        self.save_writer.append_pages_from_reader(PdfReader(filename))
        self.save_writer.add_metadata(pdf_meta)
        try:
            with open(save_filename, "wb") as fp:
                self.save_writer.write(fp)
        except FileNotFoundError as e:
            return f'File not specified. Try again. {e}'
        return f'Saving file successful.'

    def split_file(self, folder) -> str:
        """
        Split document into single pages.
        :param folder:
        :return: Message about success or failure.
        """
        if self.reader:
            for page in range(len(self.reader.pages)):
                filename = os.path.join(folder, f'Page_{page}.pdf')
                self.writer = PdfWriter()
                self.writer.add_page(self.reader.pages[page])
                with open(filename, 'wb') as fp:
                    self.writer.write(fp)
        else:
            return f'No document to split.'
        return f'Document split completed.'
