from utils.gui_helpers import DataLoaderGUI
from app_state import AppState


def main():
    state = AppState()
    DataLoaderGUI(state)


if __name__ == "__main__":
    main()
