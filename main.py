# This Python file uses the following encoding: utf-8
import sys
import os
import math
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtPdf import QPdfDocument, QPdfDocumentRenderOptions
from PySide6.QtCore import Slot, QPoint, Signal, Qt
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QMouseEvent, QWheelEvent

import pdftools

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from mainwindow import Ui_MainWindow

ZOOM_MULTIPLIER = math.sqrt(2.0)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create PdfTools instance and initialize variables
        self.max_page = None
        self.nav_single = None
        self.pdf_version = None
        self.pdf_tools = pdftools.PdfTools()
        self.about_w = None
        self.filename = None
        self.pdf_reader = None
        self.pdf_producer = None
        self.pdf_author = None
        self.pdf_creator = None
        self.pdf_title = None
        self.pdf_subject = None
        self.pdf_date = None
        self.path = None
        self.pdf_document = QPdfDocument(self)
        self.zoom_mode_changed = Signal(QPdfView.ZoomMode)
        self.render_options = QPdfDocumentRenderOptions()
        # Load UI_MainWindow class, generated from the qt designer ui file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.statusBar().showMessage('No Document to show.', timeout=0)
        # Create actions for buttons
        self.ui.actionOpen.triggered.connect(self.action_load_file)
        self.ui.actionForward.triggered.connect(self.action_next_page)
        self.ui.actionBack.triggered.connect(self.action_previous_page)
        self.ui.actionZoomIn.triggered.connect(self.action_zoom_in)
        self.ui.actionZoomOut.triggered.connect(self.action_zoom_out)
        self.ui.actionactionFitZoom.triggered.connect(self.action_zoom_fit)
        self.ui.actionRotateLeft.triggered.connect(self.action_rotate_left)
        self.ui.actionRotateRight.triggered.connect(self.action_rotate_right)
        self.ui.actionDeletePage.triggered.connect(self.action_delete_page)
        self.ui.actionInfo_2.triggered.connect(self.pdf_info)
        self.ui.actionMergePdf.triggered.connect(self.action_append_file)
        self.ui.actionSave.triggered.connect(self.action_save_file)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionExport.triggered.connect(self.action_export_page)
        # Create actions for menu
        self.ui.actionOpen_2.triggered.connect(self.action_load_file)
        self.ui.actionNext_Page.triggered.connect(self.action_next_page)
        self.ui.actionPrevious_Page.triggered.connect(self.action_previous_page)
        self.ui.actionZoom_in.triggered.connect(self.action_zoom_in)
        self.ui.actionZoom_out.triggered.connect(self.action_zoom_out)
        self.ui.actionZoom_to_fit.triggered.connect(self.action_zoom_fit)
        self.ui.actionRotate_Left.triggered.connect(self.action_rotate_left)
        self.ui.actionRotate_Right.triggered.connect(self.action_rotate_right)
        self.ui.actionDelete_Page.triggered.connect(self.action_delete_page)
        self.ui.actionInfo.triggered.connect(self.pdf_info)
        self.ui.actionMerge_Files.triggered.connect(self.action_append_file)
        self.ui.actionExtract_Page.triggered.connect(self.action_export_page)
        self.ui.actionSplit_File.triggered.connect(self.action_split_file)
        self.ui.actionSave_As.triggered.connect(self.action_save_file)
        self.ui.actionAbout.triggered.connect(self.action_about)
        self.ui.actionQuit_PDF_Tool.triggered.connect(self.close)

        # Create single page view
        self.ui.pdfView.setDocument(self.pdf_document)
        # Create multi-page view
        self.ui.pagesView.setPageMode(QPdfView.PageMode.MultiPage)
        self.ui.pagesView.setPageSpacing(15)  # add padding between pages
        self.ui.pagesView.setDocument(self.pdf_document)
        # self.ui.pagesView.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        # self.ui.pagesView.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.ui.pagesView.setZoomMode(QPdfView.ZoomMode.Custom)
        self.ui.pagesView.setZoomFactor(0.39)
        # Get current page from multi-page view and change single page view
        nav_multi = self.ui.pagesView.pageNavigator()
        nav_multi.currentPageChanged.connect(self.set_current_page)
        # self.ui.pagesView.zoomModeChanged.connect(print('zoom mode changed'))

    @Slot()
    def action_about(self):
        """
        Display app info.
        :return: None
        """
        QMessageBox.about(
            self,
            "PDF-Tool",
            "<p>A PDF-Tool app built with:</p>"
            "<p>- PySide6</p>"
            "<p>- pypdf</p>"
            "<p>- Qt Designer</p>"
            "<p>- Python</p>",
        )
        return None

    @Slot()
    def action_load_file(self):
        """
        Open File Dialog and load PDF file. A copy of the original file is created and used for any operation.
        It can be saved if needed.
        :return: None
        """
        open_filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a PDF File",
            os.getcwd(),
            "PDF (*.pdf, *.PDF)"
        )
        # Create copy of file in temporary folder
        if open_filename:
            self.filename = self.pdf_tools.create_temporary_copy(open_filename)
            # Load pdf copy from temporary folder
            self.pdf_version = self.pdf_tools.load_pdf(self.filename)
        if self.filename:
            self.path = Path(self.filename)
            self.pdf_document.load(self.filename)
        else:
            self.statusBar().showMessage(f'No filename specified. Try again.')
            return
        self.statusBar().showMessage(f'Page {self.ui.pdfView.pageNavigator().currentPage() + 1} of '
                                     f'{self.pdf_document.pageCount()} pages.', timeout=0)
        # Extract document information
        self.pdf_title = self.pdf_document.metaData(QPdfDocument.MetaDataField.Title)
        self.pdf_creator = self.pdf_document.metaData(QPdfDocument.MetaDataField.Creator)
        self.pdf_author = self.pdf_document.metaData(QPdfDocument.MetaDataField.Author)
        self.pdf_producer = self.pdf_document.metaData(QPdfDocument.MetaDataField.Producer)
        self.pdf_subject = self.pdf_document.metaData(QPdfDocument.MetaDataField.Subject)

        return

    @Slot()
    def action_save_file(self):
        """
        Open save dialog and save PDF document.
        :return: None
        """
        save_filename = QFileDialog.getSaveFileName(
            self,
            "Save File",
            os.getcwd(),
            "PDF (*.pdf)"
        )
        pdf_meta_data = self.get_pdf_meta_data()
        if save_filename:
            save_file = self.pdf_tools.save_pdf(self.filename, save_filename[0], pdf_meta_data)
            self.statusBar().showMessage(save_file, timeout=5000)
        else:
            self.statusBar().showMessage("No File chosen.", timeout=5000)
        return

    @Slot()
    def action_delete_page(self):
        """
        Delete page from document.
        :return: None
        """
        if self.filename:
            pdf_meta_data = self.get_pdf_meta_data()
            page_number = self.ui.pdfView.pageNavigator().currentPage()
            page_delete = self.pdf_tools.delete_page(self.filename, page_number, pdf_meta_data)
            self.pdf_document.load(self.filename)
            self.ui.statusbar.showMessage(page_delete, timeout=5000)
        else:
            self.ui.statusbar.showMessage(f'No file available to delete from.', timeout=5000)
        return

    def action_export_page(self):
        """
        Export single page to separate file.
        :return: None
        """
        export_filename = QFileDialog.getSaveFileName(
            self,
            "Export Page",
            os.getcwd(),
            "PDF (*.pdf)"
        )
        pdf_meta_data = self.get_pdf_meta_data()
        current_page = self.ui.pdfView.pageNavigator().currentPage()
        if export_filename:
            export_file = self.pdf_tools.export_page(self.filename, export_filename[0], current_page, pdf_meta_data)
            self.statusBar().showMessage(export_file, timeout=5000)
        else:
            self.statusBar().showMessage("No File chosen.", timeout=5000)
        return

    @Slot()
    def action_append_file(self):
        """
        Append PDF file to currently opened file and save it to separate file.
        :return:
        """
        append_filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a PDF File",
            os.getcwd(),
            "PDF (*.pdf, *.PDF)"
        )
        # use filename in tmp folder for new merged file and load again
        # e.g. tmp_merged.pdf
        save_filename = QFileDialog.getSaveFileName(
            self,
            "Save Merged File",
            os.getcwd(),
            "PDF (*.pdf)"
        )
        if save_filename:
            append_file = self.pdf_tools.append_file(self.filename, append_filename, save_filename[0])
            self.pdf_document.load(append_file)
            self.statusBar().showMessage(f'Append File {append_filename} successfully.', timeout=5000)
        else:
            self.statusBar().showMessage("No File chosen.", timeout=5000)
        return

    @Slot()
    def action_split_file(self):
        """
        Split PDF file into separate pages and save them to separate files
        :return: None
        """
        split_folder = QFileDialog.getExistingDirectory()
        if split_folder:
            split_file = self.pdf_tools.split_file(split_folder)
            self.statusBar().showMessage(split_file, timeout=5000)
        else:
            self.statusBar().showMessage("No output folder chosen.", timeout=5000)
        return

    @Slot()
    def action_next_page(self):
        """
        Navigate to the next available page and update the statusbar.
        :return: None
        """
        nav = self.ui.pdfView.pageNavigator()
        if nav.currentPage() + 1 >= self.pdf_document.pageCount():
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()} reached. '
                                         f'End of document!')
        else:
            nav.jump(nav.currentPage() + 1, QPoint(), nav.currentZoom())
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()}')
        return

    @Slot()
    def action_previous_page(self):
        """
        Navigate to the previous available page and update the statusbar.
        :return: None
        """
        nav = self.ui.pdfView.pageNavigator()
        if nav.currentPage() + 1 <= 1:
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()} reached. '
                                         f'Start of document!')
        else:
            nav.jump(nav.currentPage() - 1, QPoint(), nav.currentZoom())
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()}')
        return

    @Slot()
    def action_rotate_left(self):
        """
        Rotate page left by 90 degrees and load document again.
        :return: None
        """
        if self.filename:
            page_number = self.ui.pdfView.pageNavigator().currentPage()
            self.pdf_tools.rotate_page(self.filename, page_number, degree=270)
            self.pdf_document.load(self.filename)
        else:
            self.ui.statusbar.showMessage(f'No file available to rotate.', timeout=5000)
        return

    @Slot()
    def action_rotate_right(self):
        """
        Rotate page right by 90 degrees and load document again.
        :return: None
        """
        if self.filename:
            page_number = self.ui.pdfView.pageNavigator().currentPage()
            self.pdf_tools.rotate_page(self.filename, page_number, degree=90)
            self.pdf_document.load(self.filename)
        else:
            self.ui.statusbar.showMessage(f'No file available to rotate.', timeout=5000)
        return

    @Slot()
    def action_zoom_in(self):
        """
        Zoom in and display zoom factor in statusbar.
        :return: None
        """
        nav = self.ui.pdfView.pageNavigator()
        self.ui.pdfView.setZoomMode(QPdfView.ZoomMode.Custom)
        new_factor = self.ui.pdfView.zoomFactor() * ZOOM_MULTIPLIER
        old_factor = self.ui.pdfView.zoomFactor()
        if new_factor > 4.1:
            self.statusBar().showMessage(f'Maximum Zoom factor {int(old_factor * 100)}% reached.', timeout=5000)
        else:
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()} - '
                                         f'Zoom {int(new_factor * 100)}%', timeout=0)
            self.ui.pdfView.setZoomFactor(new_factor)
        return

    @Slot()
    def action_zoom_out(self):
        """
        Zoom out and display zoom factor in statusbar.
        :return: None
        """
        nav = self.ui.pdfView.pageNavigator()
        self.ui.pdfView.setZoomMode(QPdfView.ZoomMode.Custom)
        new_factor = self.ui.pdfView.zoomFactor() / ZOOM_MULTIPLIER
        old_factor = self.ui.pdfView.zoomFactor()
        if new_factor < 0.125:
            self.statusBar().showMessage(f'Minimum Zoom factor {int(old_factor * 100)}% reached.', timeout=5000)
        else:
            self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()} - '
                                         f'Zoom {int(new_factor * 100)}%', timeout=0)
            self.ui.pdfView.setZoomFactor(new_factor)
        return

    @Slot()
    def action_zoom_fit(self):
        """
        Set zoom factor to fit the document to the screen and display the zoom factor in statusbar.
        :return: None
        """
        nav = self.ui.pdfView.pageNavigator()
        self.ui.pdfView.setZoomFactor(1)
        # Options for ZoomMode are: Custom, FitToWidth, FitInView
        self.ui.pdfView.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.statusBar().showMessage(f'Page {nav.currentPage() + 1} of {self.pdf_document.pageCount()} - '
                                     f'Zoom 100%', timeout=0)
        return None

    def get_pdf_meta_data(self):
        """
        Create PDF metadata variable.
        :return: PDF metadata
        """
        pdf_meta_data = {"/Title": self.pdf_title,
                         "/Author": self.pdf_author,
                         "/Creator": self.pdf_creator,
                         "/Subject": self.pdf_subject,
                         "/Producer": "pypdf",
                         }
        return pdf_meta_data

    @Slot()
    def pdf_info(self):
        """
        Display information about the document, like title, author, creator and subject.
        :return: None
        """
        messagebox_info = (f'<p>Document Title: {self.pdf_title}</p>'
                           f'<p>Document Subject: {self.pdf_subject}</p>'
                           f'<p>Document Author: {self.pdf_author}</p>'
                           f'<p>Document Creator: {self.pdf_creator}</p>'
                           f'<p>Document Producer: {self.pdf_producer}</p>'
                           f'<p>PDF-Version: {self.pdf_version}</p>')
        QMessageBox.information(self, "Document Info",
                                messagebox_info)
        return

    @Slot()
    def set_current_page(self):
        """
        Get current page in multi page view and set single page view to current page.
        :return: page
        """
        page = self.ui.pagesView.pageNavigator().currentPage()
        nav_single = self.ui.pdfView.pageNavigator()
        nav_single.jump(page, QPoint(), nav_single.currentZoom())
        # print(f'current page {page}')
        # print(f'zoom factor: {self.ui.pagesView.zoomFactor()}')
        self.statusBar().showMessage(f'Page {nav_single.currentPage() + 1} of {self.pdf_document.pageCount()}')
        return page

    @Slot()
    def mousePressEvent(self, event):
        """
        Jump to first or last page in view if current page is > 2 in multi page view or
        if current page is > max pages in multi page.
        MousePressEvent is set to work for first 30 % height in multi page view and
        last 25% height in multi page view.
        :param event:
        :return: None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.nav_single = self.ui.pdfView.pageNavigator()
            self.max_page = self.pdf_document.pageCount() - 1
            # print(f'left button pressed at position: x: {event.position().x()} y: {event.position().y()}')
            mouse_pos_x = event.position().x()
            mouse_pos_y = event.position().y()
            widget_width = self.ui.pagesView.width()
            widget_height = self.ui.pagesView.height()
            if mouse_pos_y < widget_height * 0.30 and self.nav_single.currentPage() < 2:
                self.nav_single.jump(0,QPoint(), self.nav_single.currentZoom())
                self.statusBar().showMessage(
                    f'Page {self.nav_single.currentPage() + 1} of {self.pdf_document.pageCount()}')
            if mouse_pos_y > widget_height * 0.75 and self.nav_single.currentPage() < self.max_page:
                self.nav_single.jump(self.max_page, QPoint(), self.nav_single.currentZoom())
                self.statusBar().showMessage(
                    f'Page {self.nav_single.currentPage() + 1} of {self.pdf_document.pageCount()}')
            # print(f'width: {widget_width}; height: {widget_height}')
            # print(f'frame with: {self.frameGeometry().width()}')
            # print(f'frame height: {self.frameGeometry().height()}')
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
