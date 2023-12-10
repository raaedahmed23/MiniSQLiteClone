import sys
import os
from lib.settings.Settings import Settings


class OutputFormat:
    @staticmethod
    def splash_screen():
        print(Settings.line("*", 70))
        print(f"----------Welcome to {Settings.get_db_name()} CLI----------")
        # print(Settings.line("-", 80))
        print("\nUse command 'create db;' to initialize the database")
        print("\nFor supported commands use: \"help;\".")
        # print(Settings.line("-", 80))
        print(Settings.line("*", 70))

    @staticmethod
    def disable_stdout():
        sys.stdout = open(os.devnull, 'w')

    @staticmethod
    def enable_stdout():
        sys.stdout = sys.__stdout__
