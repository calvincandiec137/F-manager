import os
import time
from tabulate import tabulate
import curses

def format_size(size_in_bytes):
    """Format file size into human-readable units."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def sizeofFolder(path):
    """Recursively calculate the size of a folder."""
    folderSize = 0
    listItems = os.listdir(path)
    for j in listItems:
        itemPath = os.path.join(path, j)
        if os.path.isfile(itemPath):
            folderSize += os.path.getsize(itemPath)
        elif os.path.isdir(itemPath):
            folderSize += sizeofFolder(itemPath)
    return folderSize

def fill_data_for_tabulate(current_dir):
    """Retrieve file and folder data for the current directory."""
    try:
        dirs = os.listdir(current_dir)
    except PermissionError:
        return [["Error: Permission Denied", "", ""]]

    data = []
    for i in dirs:
        path = os.path.join(current_dir, i)
        try:
            if os.path.isfile(path):
                fileName = os.path.basename(path)
                fileSize = os.path.getsize(path)
                sizeName = format_size(fileSize)
                fileDate = time.ctime(os.path.getmtime(path))
                data.append([fileName, sizeName, fileDate])
            elif os.path.isdir(path):
                fileName = f"/{os.path.basename(path)}"
                folderSize = sizeofFolder(path)
                sizeName = format_size(folderSize)
                fileDate = time.ctime(os.path.getmtime(path))
                data.append([fileName, sizeName, fileDate])
        except Exception as e:
            data.append([f"Error: {e}", "", ""])
    return data

def main(stdscr):
    """Main function to handle curses-based file navigation."""
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    curses.curs_set(0)

    # Starting directory
    current_dir = "/"
    cursor_row = 1

    while True:
        # Fill table data for current directory
        data = fill_data_for_tabulate(current_dir)
        rows = tabulate(data, headers=["File Name", "Size", "Date Modified"], tablefmt="grid").splitlines()

        # Display the table with highlighted row
        stdscr.clear()
        for i, row in enumerate(rows):
            if i == cursor_row:
                stdscr.addstr(row + "\n", curses.A_REVERSE)
            else:
                stdscr.addstr(row + "\n")
        
        # Display current directory at the bottom
        stdscr.addstr(curses.LINES - 1, 0, f"Current Directory: {current_dir} | Press 'q' to quit", curses.A_BOLD)

        stdscr.refresh()

        # Handle key inputs
        key = stdscr.getch()

        if key == curses.KEY_UP and cursor_row > 1:
            cursor_row -= 1
        elif key == curses.KEY_DOWN and cursor_row < len(rows) - 2:  # Avoid going below table
            cursor_row += 1
        elif key == ord('q'):  # Quit program
            break
        elif key == 10:  # ENTER key
            # Get the selected item name
            selected_item = data[cursor_row - 1][0]  # Adjust for header row
            if selected_item.startswith("/"):  # Indicates a folder
                new_path = os.path.join(current_dir, selected_item[1:])  # Remove '/' prefix
                if os.path.isdir(new_path):
                    current_dir = new_path  # Update the current directory
                    cursor_row = 1  # Reset cursor position
            else:
                stdscr.addstr(curses.LINES - 2, 0, f"Selected File: {selected_item}", curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()

    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)
