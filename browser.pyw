import sys
from PyQt5.QtCore import QUrl, Qt, QMimeData
from PyQt5.QtGui import QIcon, QDrag
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Tab(QTabBar):
    def __init__(self, parent=None):
        super(Tab, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-tab'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-tab'):
            data = event.mimeData().data('application/x-tab')
            tab_data = data.data().decode('utf-8').split(';')
            url = QUrl(tab_data[1])  # Correctly access URL
            label = tab_data[0]
            self.parent().add_new_tab(url, label)
            event.acceptProposedAction()


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

        # Customize tab widget to use custom tab bar
        self.tab_widget.setTabBar(Tab(self.tab_widget))

        # Add the first tab
        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')

        # Add the tab widget to the main layout
        main_layout.addWidget(self.tab_widget)

        # Set up the navigation toolbar
        self.navigation_bar = QToolBar('Navigation Toolbar')
        self.addToolBar(self.navigation_bar)

        # Add navigation buttons with built-in icons
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

        self.navigation_bar.addSeparator()

        # URL bar
        self.URLBar = QLineEdit()
        self.URLBar.setPlaceholderText("Enter URL and press Enter...")
        self.URLBar.returnPressed.connect(self.load_url)
        self.navigation_bar.addWidget(self.URLBar)

        # New tab button
        new_tab_button = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        new_tab_button.triggered.connect(self.new_tab)
        self.navigation_bar.addAction(new_tab_button)

        # Show the main window
        self.show()

        # Update URL bar when tab changes
        self.tab_widget.currentChanged.connect(self.update_url_bar)

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        # Set the overall style for the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QToolBar {
                background-color: #1E1E1E;
                border: none;
            }
            QTabWidget {
                background-color: #3C3C3C;
                color: #FFFFFF;
                font-size: 14px;
            }
            QTabBar::tab {
                background: #4C4C4C;
                border: 1px solid #5C5C5C;
                padding: 10px;
                margin-right: 2px;
                color: #FFFFFF;
            }
            QTabBar::tab:selected {
                background: #6C6C6C;
            }
            QLineEdit {
                background-color: #5C5C5C;
                color: #FFFFFF;
                padding: 5px;
                border: 1px solid #6C6C6C;
            }
            QLineEdit::placeholder {
                color: #AAAAAA;
            }
        """)

    def add_new_tab(self, url: QUrl, label: str):
        # Create a new QWebEngineView
        browser = QWebEngineView()
        browser.setUrl(url)

        # Add the new tab to the tab widget
        i = self.tab_widget.addTab(browser, label)
        self.tab_widget.setCurrentIndex(i)

        # Update the URL bar when the URL changes
        browser.urlChanged.connect(lambda q: self.update_title(q, i))

        # Make the tab draggable
        self.tab_widget.tabBar().setMovable(True)

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

    def new_tab(self):
        self.add_new_tab(QUrl('https://www.google.com'), 'New Tab')

    def close_current_tab(self, i):
        if self.tab_widget.count() > 1:  # Prevent closing the last tab
            self.tab_widget.removeTab(i)

    def update_title(self, q, i):
        title = q.toString() if q.toString() else 'Untitled'
        self.tab_widget.setTabText(i, title)

    def update_url_bar(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            self.URLBar.setText(current_browser.url().toString())
            self.URLBar.setCursorPosition(0)

app = QApplication(sys.argv)
app.setApplicationName('CodeForge')

# Set application style
QApplication.setStyle('Fusion')

# Create and style the application
window = Window()
app.exec_()
