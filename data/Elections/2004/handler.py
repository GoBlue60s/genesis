from PySide6.QtWidgets import QApplication, QMainWindow, QAction
import logging

class Command:
    def execute(self):
        try:
            self._do_work()
        except Exception as e:
            # Handle the exception here (log it, clean up, etc.)
            logging.error(f"Error in Command: {e}")
            # Exception is handled, so control returns to the caller without propagating the exception

    def _do_work(self):
        # This method does the actual work and may raise exceptions
        # For example, raise an exception if a resource is not available
        raise Exception("Resource not available")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a menu
        menu = self.menuBar().addMenu("&File")

        # Create an action and connect it to a command
        action = QAction("Execute Command", self)
        action.triggered.connect(self.on_action_triggered)
        menu.addAction(action)

    def on_action_triggered(self):
        # Instantiate and execute the command
        command = Command()
        command.execute()

# Initialize and run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
