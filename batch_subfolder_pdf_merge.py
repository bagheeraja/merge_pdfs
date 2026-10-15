"""
Batch Subfolder PDF Merger (merge_pdf.py)

Exact Intended Function:
This script automates the process of combining multiple PDF documents grouped inside 
subdirectories. It prompts the user to select an input parent directory and a 
destination directory via native GUI dialogs, eliminating hardcoded paths. 

For every subfolder found within the input directory:
1. It gathers and sorts all PDF files chronologically/alphabetically.
2. It merges them into a single master PDF, embedding outline/bookmark items 
   named after each individual file's stem.
3. It replicates the subfolder structure in the destination directory and saves 
   the combined output (e.g., [SubfolderName]_combined.pdf).
4. It remembers user directory selections locally using a JSON configuration file.
"""

import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from pypdf import PdfWriter

CONFIG_FILE = "merge_config.json"


def load_config() -> dict:
  """Loads saved directory settings from a local configuration file."""
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    except Exception:
      return {}
  return {}


def save_config(config_data: dict):
  """Saves directory settings to a local configuration file."""
  try:
    with open(CONFIG_FILE, "w") as f:
      json.dump(config_data, f)
  except Exception as e:
    print(f"Failed to save config: {e}")


def select_input_folder(root: tk.Tk, initial_dir: str = "") -> str:
  """Opens a folder selection dialog for the parent directory containing categorized subfolders."""
  return filedialog.askdirectory(
      parent=root,
      title="Select Parent Input Folder (Containing Subfolders of PDFs)",
      initialdir=initial_dir,
  )


def select_destination_folder(root: tk.Tk, initial_dir: str = "") -> str:
  """Opens a folder selection dialog for where the mirrored output folders and combined PDFs will be saved."""
  return filedialog.askdirectory(
      parent=root,
      title="Select Destination Folder for Combined PDFs",
      initialdir=initial_dir,
  )


def show_info(title: str, message: str, parent_window=None):
  """Displays a pop-up information box safely without locking hidden parent windows."""
  if parent_window:
    parent_window.deiconify()
  messagebox.showinfo(title, message, parent=parent_window)
  if parent_window:
    parent_window.withdraw()


def merge_subfolder_pdfs_batch(
    root: tk.Tk, input_folder: str, output_folder: str
):
  """Scans each subfolder in the input directory, merges its PDFs into a single bookmarked file, and saves the output."""
  base_input_dir = Path(input_folder)
  base_output_dir = Path(output_folder)

  print(f"Scanning source directory: {base_input_dir.resolve()}")
  print(f"Saving outputs to: {base_output_dir.resolve()}\n")

  processed_subfolders = 0
  total_files_merged = 0

  # Loop through items inside the base input directory
  for sub_folder in sorted(base_input_dir.iterdir()):
    if sub_folder.is_dir():
      folder_name = sub_folder.name
      print(f"Processing Category/Folder: {folder_name}")

      # Find all PDFs in the subfolder, sorted chronologically/alphabetically
      pdf_files = sorted(sub_folder.glob("*.pdf"))

      if not pdf_files:
        print(f"  -> No PDF files found in {folder_name}, skipping.\n")
        continue

      writer = PdfWriter()

      # Add each PDF to the writer with an outline/bookmark item
      for pdf in pdf_files:
        item_name = pdf.stem
        print(f"  Adding: {item_name}")
        writer.append(str(pdf), outline_item=item_name)
        total_files_merged += 1

      # Create corresponding subfolder in the destination directory if it doesn't exist
      dest_sub_folder = base_output_dir / folder_name
      dest_sub_folder.mkdir(parents=True, exist_ok=True)

      # Define the output file path in the destination folder
      output_pdf = dest_sub_folder / f"{folder_name}_combined.pdf"

      # Write out the combined PDF to disk
      with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

      writer.close()
      print(f"  Successfully created: {output_pdf}\n")
      processed_subfolders += 1

  summary_msg = (
      f"PDF Batch Merging Complete!\n\n"
      f"• Subfolders Processed: {processed_subfolders}\n"
      f"• Total PDFs Merged: {total_files_merged}\n"
      f"• Saved To: {base_output_dir.resolve()}"
  )

  print(f"\n{summary_msg}")
  show_info("Merge Summary", summary_msg, root)


if __name__ == "__main__":
  root = None
  try:
    root = tk.Tk()
    root.withdraw()

    config = load_config()
    last_input_dir = config.get("last_input_dir", "")
    last_dest_dir = config.get("last_destination", "")

    # 1. Select input folder via GUI dialog
    input_folder = select_input_folder(root, initial_dir=last_input_dir)

    if input_folder:
      # 2. Select destination folder via GUI dialog
      dest_folder = select_destination_folder(
          root, initial_dir=last_dest_dir or input_folder
      )

      if dest_folder:
        # Save directories to config for future runs
        save_config({"last_input_dir": input_folder, "last_destination": dest_folder})

        # 3. Run the batch merge process
        merge_subfolder_pdfs_batch(root, input_folder, dest_folder)
      else:
        print("No destination folder selected. Exiting.")
    else:
        print("No input folder selected. Exiting.")

  except KeyboardInterrupt:
    print("\nProcess canceled by user. Exiting.")
  finally:
    if root:
      try:
        root.destroy()
      except Exception:
        pass