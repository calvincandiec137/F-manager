import os
import time
from tabulate import tabulate
import curses
import traceback
import logging

# Set up logging
logging.basicConfig(filename='file_manager.log', level=logging.DEBUG)

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def sizeofFolder(path):
    try:
        folderSize = 0
        for root, dirs, files in os.walk(path):
            try:
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        folderSize += os.path.getsize(fp)
                    except (PermissionError, OSError) as e:
                        logging.debug(f"Cannot access file {fp}: {e}")
                        continue
            except (PermissionError, OSError) as e:
                logging.debug(f"Cannot access directory {root}: {e}")
                continue
        return folderSize
    except Exception as e:
        logging.error(f"Error in sizeofFolder: {e}")
        return 0

def fill_data_for_tabulate(current_dir):
    try:
        dirs = os.listdir(current_dir)
        data = []
        for i in dirs:
            if i.startswith('.'):  # Skip hidden files
                continue
            try:
                path = os.path.join(current_dir, i)
                if os.path.isfile(path):
                    try:
                        fileName = os.path.basename(path)
                        fileSize = os.path.getsize(path)
                        sizeName = format_size(fileSize)
                        fileDate = time.ctime(os.path.getmtime(path))
                        data.append([fileName, sizeName, fileDate])
                    except (PermissionError, OSError) as e:
                        logging.debug(f"Cannot access file {path}: {e}")
                        data.append([i, "Permission Denied", "Unknown"])
                else:
                    fileName = f"/{os.path.basename(path)}"
                    try:
                        folderSize = sizeofFolder(path)
                        sizeName = format_size(folderSize)
                        fileDate = time.ctime(os.path.getmtime(path))
                        data.append([fileName, sizeName, fileDate])
                    except (PermissionError, OSError) as e:
                        logging.debug(f"Cannot access directory {path}: {e}")
                        data.append([fileName, "Permission Denied", "Unknown"])
            except Exception as e:
                logging.error(f"Error processing {i}: {e}")
                continue
        return data
    except Exception as e:
        logging.error(f"Error in fill_data_for_tabulate: {e}")
        return [["Error", str(e), ""]]

def main(stdscr):
    try:
        curses.cbreak()
        stdscr.keypad(True)
        curses.curs_set(0)
        
        path = os.getcwd()
        current_dir = path
        cursor_row = 3
        
        while True:
            try:
                stdscr.clear()
                data = fill_data_for_tabulate(current_dir)
                rows = tabulate(data, headers=["File Name", "Size", "Date of Creation"], 
                              tablefmt="grid").splitlines()
                
                # Show current path at top
                stdscr.addstr(0, 0, f"Current path: {current_dir}\n")
                
                for i, row in enumerate(rows):
                    if i == cursor_row:
                        stdscr.addstr(f"{row}\n", curses.A_REVERSE)
                    else:
                        stdscr.addstr(f"{row}\n")
                
                stdscr.refresh()
                
                key = stdscr.getch()
                if key == curses.KEY_UP and cursor_row > 3:
                    cursor_row -= 2
                elif key == curses.KEY_DOWN and cursor_row < len(rows) - 2:
                    cursor_row += 2
                elif key == ord('q'):
                    break
                elif key == curses.KEY_LEFT:
                    parent_dir = os.path.dirname(current_dir)
                    if os.access(parent_dir, os.R_OK):
                        current_dir = parent_dir
                        cursor_row = 3
                elif key == 10:  # Enter key
                    data_index = (cursor_row - 3) // 2
                    if 0 <= data_index < len(data):
                        selected_entry = data[data_index][0]
                        if selected_entry.startswith("/"):
                            new_path = os.path.join(current_dir, selected_entry.lstrip('/'))
                            if os.access(new_path, os.R_OK):
                                current_dir = new_path
                                cursor_row = 3
                        else:
                            full_path = os.path.join(current_dir, selected_entry)
                            os.system(f"xdg-open '{full_path}'")
                            
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                stdscr.addstr(0, 0, f"Error: {str(e)}")
                stdscr.refresh()
                stdscr.getch()
                
    except Exception as e:
        curses.endwin()
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    curses.wrapper(main)