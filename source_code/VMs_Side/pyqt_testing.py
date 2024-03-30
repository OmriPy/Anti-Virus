from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListView, QPushButton
from PyQt6.QtCore import QStringListModel

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('List View Example')
        self.setGeometry(100, 100, 300, 200)

        # Create a main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a list view
        self.list_view = QListView()

        # Create a model to hold the data
        self.model = QStringListModel()

        # Add data to the model
        self.data = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        self.model.setStringList(self.data)

        # Set the model for the list view
        self.list_view.setModel(self.model)

        # Add the list view to the layout
        layout.addWidget(self.list_view)

        button = QPushButton('click me')
        button.clicked.connect(self.change_data)
        layout.addWidget(button)

        self.show()
    
    def change_data(self):
        self.data.append('hii')
        self.model.setStringList(self.data)

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    app.exec()
