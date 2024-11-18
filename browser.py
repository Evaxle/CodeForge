import sys
import os
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QDialog,
    QPushButton, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QFileDialog, QWidget, QTabWidget, QAction, QToolBar, QMenu, QCheckBox, QColorDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 300)

        # Layouts
        self.layout = QVBoxLayout(self)

        # Theme color settings
        self.color_button = QPushButton("Choose Theme Color")
        self.color_button.clicked.connect(self.choose_color)
        self.layout.addWidget(self.color_button)

        # Ad-blocking toggle
        self.adblock_checkbox = QCheckBox("Enable Ad Blocking")
        self.layout.addWidget(self.adblock_checkbox)

        # Safe browsing toggle
        self.safe_browsing_checkbox = QCheckBox("Enable Safe Browsing")
        self.layout.addWidget(self.safe_browsing_checkbox)

        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        self.layout.addWidget(self.apply_button)

        self.chosen_color = "#ffffff"  # Default white theme

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.chosen_color = color.name()

    def apply_settings(self):
        self.close()


class DownloadManager(QDialog):
    def __init__(self, parent=None):
        super(DownloadManager, self).__init__(parent)
        self.setWindowTitle("Download Manager")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout(self)

        # Tree widget to display download history
        self.download_history = QTreeWidget()
        self.download_history.setHeaderLabels(["File Name", "Status", "Path"])
        self.layout.addWidget(self.download_history)

        # Buttons for actions
        button_layout = QHBoxLayout()
        self.set_download_path_button = QPushButton("Set Download Folder")
        self.set_download_path_button.clicked.connect(self.set_download_folder)
        button_layout.addWidget(self.set_download_path_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_download_history)
        button_layout.addWidget(self.clear_history_button)

        self.layout.addLayout(button_layout)

        self.default_download_path = os.path.expanduser("~/Downloads")

    def set_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.default_download_path)
        if folder:
            self.default_download_path = folder

    def add_download(self, file_name, status, file_path):
        # Add a new download entry to the tree widget
        item = QTreeWidgetItem([file_name, status, file_path])
        self.download_history.addTopLevelItem(item)

    def clear_download_history(self):
        self.download_history.clear()


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Set window title and size
        self.setWindowTitle("CodeForge")
        self.setGeometry(100, 100, 1200, 800)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_current_tab)

        # Add the first tab
        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')

        # Add the tab widget to the main layout
        main_layout.addWidget(self.tab_widget)

        # Search bar below the tabs
        search_bar_layout = QHBoxLayout()
        self.URLBar = QLineEdit()
        self.URLBar.setPlaceholderText("Enter URL and press Enter...")
        self.URLBar.returnPressed.connect(self.load_url)
        search_bar_layout.addWidget(self.URLBar)
        main_layout.addLayout(search_bar_layout)

        # Add toolbar with navigation buttons
        self.navigation_bar = QToolBar('Navigation Toolbar')
        self.addToolBar(Qt.LeftToolBarArea, self.navigation_bar)

        # Navigation buttons
        back_button = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_button.triggered.connect(self.current_browser_back)
        self.navigation_bar.addAction(back_button)

        refresh_button = QAction(QIcon.fromTheme("view-refresh"), "Refresh", self)
        refresh_button.triggered.connect(self.current_browser_reload)
        self.navigation_bar.addAction(refresh_button)

        next_button = QAction(QIcon.fromTheme("go-next"), "Next", self)
        next_button.triggered.connect(self.current_browser_forward)
        self.navigation_bar.addAction(next_button)

        home_button = QAction(QIcon.fromTheme("home"), "Home", self)
        home_button.triggered.connect(self.go_to_home)
        self.navigation_bar.addAction(home_button)

        # Settings button
        settings_button = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        settings_button.triggered.connect(self.open_settings)
        self.navigation_bar.addAction(settings_button)

        # Download Manager button
        self.download_manager_button = QAction(QIcon.fromTheme("folder-download"), "Download Manager", self)
        self.download_manager_button.triggered.connect(self.open_download_manager)
        self.navigation_bar.addAction(self.download_manager_button)

        # Show the main window
        self.show()

        # Create managers
        self.download_manager = DownloadManager(self)
        self.settings_dialog = SettingsDialog(self)

        # Update URL bar when tab changes
        self.tab_widget.currentChanged.connect(self.update_url_bar)

    def add_new_tab(self, url: QUrl, label: str):
        browser = QWebEngineView()
        browser.setUrl(url)

        # Handle downloads
        browser.page().profile().downloadRequested.connect(self.handle_download)

        browser.urlChanged.connect(lambda q: self.update_title_and_icon(q, browser))

        i = self.tab_widget.addTab(browser, label)
        self.tab_widget.setCurrentIndex(i)

    def update_title_and_icon(self, q, browser):
        index = self.tab_widget.indexOf(browser)
        title = browser.page().title()
        favicon = browser.icon()
        self.tab_widget.setTabText(index, title)
        self.tab_widget.setTabIcon(index, favicon)

    def current_browser_back(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()

    def current_browser_reload(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()

    def current_browser_forward(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.forward()

    def go_to_home(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl('https://www.google.com/'))

    def load_url(self):
        url = QUrl(self.URLBar.text())
        if url.scheme() == '':
            url.setScheme('https://')
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(url)

    def close_current_tab(self, i):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(i)

    def handle_download(self, download: QWebEngineDownloadItem):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", os.path.join(self.download_manager.default_download_path, download.suggestedFileName()))
        if file_path:
            download.setPath(file_path)
            download.accept()
            self.download_manager.add_download(download.suggestedFileName(), "Downloading", file_path)
            download.finished.connect(lambda: self.download_manager.add_download(download.suggestedFileName(), "Completed", file_path))

    def open_download_manager(self):
        self.download_manager.show()

    def open_settings(self):
        self.settings_dialog.exec_()

    def update_url_bar(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            self.URLBar.setText(current_browser.url().toString())
            self.URLBar.setCursorPosition(0)


app = QApplication(sys.argv)
app.setApplicationName('CodeForge')
QApplication.setStyle('Fusion')
window = Window()
app.exec_()
