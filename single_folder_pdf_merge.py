"""
Single-Folder PDF Merger (merge_ord_single_folder.py)

Exact Intended Function:
This script combines all PDF documents located directly inside a single selected 
folder into one master combined PDF file. It eliminates hardcoded paths by prompting 
the user to select an input folder and a destination folder via native GUI dialogs.

Behavior:
1. It scans ONLY the top level of the selected input folder for PDF files (ignoring subfolders).
2. It sorts the discovered PDF files chronologically or alphabetically.
3. It merges them into a single output file named after the input folder 
   (e.g., [FolderName]_ord_combined.pdf) and saves it directly to the chosen destination folder.
4. It embeds outline/bookmark items for each individual file based on its filename stem.
5. It saves user directory choices locally in a configuration file for convenience in future runs.
"""

import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from pypdf import PdfWriter

CONFIG_FILE = "merge_single_config.json"


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
  """Opens a folder selection dialog for the target folder containing the PDFs to merge."""
  return filedialog.askdirectory(
      parent=root,
      title="Select Target Folder Containing PDFs to Merge",
      initialdir=initial_dir,
  )


def select_destination_folder(root: tk.Tk, initial_dir: str = "") -> str:
  """Opens a folder selection dialog for where the combined master PDF will be saved."""
  return filedialog.askdirectory(
      parent=root,
      title="Select Destination Folder for the Combined PDF",
      initialdir=initial_dir,
  )


def show_info(title: str, message: str, parent_window=None):
  """Displays a pop-up information box safely without locking hidden parent windows."""
  if parent_window:
    parent_window.deiconify()
  messagebox.showinfo(title, message, parent=parent_window)
  if parent_window:
    parent_window.withdraw()


def merge_single_folder_pdfs(root: tk.Tk, input_folder: str, output_folder: str):
  """Merges all flat PDFs in the input folder into a single bookmarked PDF saved to the output folder."""
  base_dir = Path(input_folder)
  dest_dir = Path(output_folder)

  print(f"Processing folder: {base_dir.resolve()}")
  print(f"Saving output to: {dest_dir.resolve()}\n")

  writer = PdfWriter()

  # .glob("*.pdf") ONLY looks for PDF files directly inside base_dir.
  # It ignores subfolders entirely.
  pdf_files = sorted(base_dir.glob("*.pdf"))

  if not pdf_files:
    print(f"No PDF files found directly in {base_dir.name}.")
    show_info("Merge Result", f"No PDF files found directly in:\n{base_dir.name}", root)
    return

  # Add each document to the writer with an outline/bookmark item
  for pdf in pdf_files:
    doc_name = pdf.stem
    print(f"  Adding: {doc_name}")
    writer.append(str(pdf), outline_item=doc_name)

  # Ensure destination directory exists
  dest_dir.mkdir(parents=True, exist_ok=True)

  # Define the output file path using the input folder's name
  output_pdf = dest_dir / f"{base_dir.name}_ord_combined.pdf"

  # Write out the combined PDF to disk
  with open(output_pdf, "wb") as output_file:
    writer.write(output_file)

  writer.close()
  
  success_msg = (
      f"PDF Merging Complete!\n\n"
      f"• Files Combined: {len(pdf_files)}\n"
      f"• Saved To: {output_pdf.resolve()}"
  )

  print(f"\nSuccessfully created: {output_pdf.name}")
  show_info("Merge Summary", success_msg, root)


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

        # 3. Run the single folder merge process
        merge_single_folder_pdfs(root, input_folder, dest_folder)
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