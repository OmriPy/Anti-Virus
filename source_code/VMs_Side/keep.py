def show_entry_screen(self):
    # Create Entry page
    self.entry_screen = Screen('Client', self)
    self.entry_screen.center()

    # Add label for Entry page
    entry_label = Label('Welcome!')
    self.entry_screen.add_widget(entry_label)

    # Create 'Connect to server' button
    connect_button = Button('Connect to Server', MainApp.connect_to_server)
    self.entry_screen.add_widget(connect_button)

    # Create Exit button
    self.exit_button = Button('Exit', MainApp.exit)
    self.entry_screen.add_widget(self.exit_button)

    # Add frame to main layout
    self.main_layout.addWidget(self.entry_screen)