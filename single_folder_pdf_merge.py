"""
Single-Folder PDF Merger (single_folder_pdf_merge.py)

Exact Intended Function:
This script combines all PDF documents located directly inside a single selected 
folder into one master combined PDF file. It eliminates hardcoded paths by prompting 
the user to select an input folder and a destination folder via native GUI dialogs, 
and allows the user to custom-name the final output file.

Behavior:
1. It scans ONLY the top level of the selected input folder for PDF files (ignoring subfolders).
2. It sorts the discovered PDF files chronologically or alphabetically.
3. It prompts the user with a dialog box to specify a custom name for the combined output file.
4. It merges them into the custom-named PDF file and saves it directly to the chosen destination folder.
5. It embeds outline/bookmark items for each individual file based on its filename stem.
6. It saves user directory choices locally in a configuration file for convenience in future runs.
"""

import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
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


def prompt_output_filename(root: tk.Tk, default_name: str) -> str:
  """Prompts the user to enter a custom filename for the combined output PDF."""
  if root:
    root.deiconify()
  
  filename = simpledialog.askstring(
      "Output Filename",
      "Enter the desired filename for the combined PDF\n(with or without .pdf extension):",
      initialvalue=default_name,
      parent=root
  )
  
  if root:
    root.withdraw()
    
  return filename.strip() if filename else ""


def show_info(title: str, message: str, parent_window=None):
  """Displays a pop-up information box safely without locking hidden parent windows."""
  if parent_window:
    parent_window.deiconify()
  messagebox.showinfo(title, message, parent=parent_window)
  if parent_window:
    parent_window.withdraw()


def merge_single_folder_pdfs(root: tk.Tk, input_folder: str, output_folder: str, custom_filename: str):
  """Merges all flat PDFs in the input folder into a single bookmarked PDF with a custom filename."""
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

  # Normalize custom filename (ensure it ends with .pdf)
  if not custom_filename.lower().endswith(".pdf"):
    custom_filename += ".pdf"

  output_pdf = dest_dir / custom_filename

  # Write out the combined PDF to disk
  with open(output_pdf, "wb") as output_file:
    writer.write(output_file)

  writer.close()
  
  success_msg = (
      f"PDF Merging Complete!\n\n"
      f"• Files Combined: {len(pdf_files)}\n"
      f"• Saved As: {output_pdf.name}\n"
      f"• Saved To: {dest_dir.resolve()}"
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

        # 3. Prompt user for custom output filename (pre-filled with folder name)
        default_filename = f"{Path(input_folder).name}_combined.pdf"
        custom_filename = prompt_output_filename(root, default_filename)

        if custom_filename:
          # 4. Run the single folder merge process
          merge_single_folder_pdfs(root, input_folder, dest_folder, custom_filename)
        else:
          print("Output filename not provided. Exiting.")
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