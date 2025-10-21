#!/usr/bin/env python3
"""
MakkelijkPdf Command Line Interface
Batch conversie van PDF bestanden naar afbeeldingen
"""

import argparse
import os
import sys
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import time

# Voeg poppler pad toe aan PATH
poppler_path = r"C:\poppler\poppler-23.08.0\Library\bin"
if poppler_path not in os.environ["PATH"]:
    os.environ["PATH"] = poppler_path + os.pathsep + os.environ["PATH"]

def convert_pdf_to_images(input_path, output_dir, dpi=300, format='PNG', prefix=None):
    """
    Converteer een PDF bestand naar afbeeldingen
    
    Args:
        input_path (str): Pad naar PDF bestand
        output_dir (str): Output directory
        dpi (int): DPI voor conversie
        format (str): Output formaat (PNG, JPG, TIFF)
        prefix (str): Prefix voor output bestanden
    """
    try:
        print(f"Converteer {input_path}...")
        
        # Lees PDF
        pages = convert_from_path(input_path, dpi=dpi, poppler_path=poppler_path)
        total_pages = len(pages)
        
        # Bepaal bestandsnaam prefix
        if prefix is None:
            prefix = Path(input_path).stem
        
        print(f"Gevonden {total_pages} pagina('s)")
        
        # Converteer elke pagina
        for i, page in enumerate(pages):
            print(f"Converteer pagina {i+1}/{total_pages}...", end=" ")
            
            # Bepaal output bestandsnaam
            if total_pages == 1:
                output_filename = f"{prefix}.{format.lower()}"
            else:
                output_filename = f"{prefix}_pagina_{i+1:03d}.{format.lower()}"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Sla afbeelding op
            if format.upper() in ['JPG', 'JPEG']:
                # Converteer naar RGB voor JPG
                if page.mode == 'RGBA':
                    page = page.convert('RGB')
                page.save(output_path, 'JPEG', quality=95)
            else:
                page.save(output_path, format.upper())
            
            print("✓")
        
        print(f"Conversie voltooid! {total_pages} pagina('s) opgeslagen in {output_dir}")
        return True
        
    except Exception as e:
        print(f"Fout bij conversie van {input_path}: {str(e)}")
        return False

def batch_convert(input_dir, output_dir, dpi=300, format='PNG', recursive=False):
    """
    Batch conversie van alle PDF bestanden in een directory
    
    Args:
        input_dir (str): Input directory met PDF bestanden
        output_dir (str): Output directory
        dpi (int): DPI voor conversie
        format (str): Output formaat
        recursive (bool): Recursief zoeken in subdirectories
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Input directory bestaat niet: {input_dir}")
        return
    
    # Maak output directory aan
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Zoek PDF bestanden
    if recursive:
        pdf_files = list(input_path.rglob("*.pdf"))
    else:
        pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Geen PDF bestanden gevonden in {input_dir}")
        return
    
    print(f"Gevonden {len(pdf_files)} PDF bestand(en)")
    
    # Converteer elk PDF bestand
    success_count = 0
    start_time = time.time()
    
    for pdf_file in pdf_files:
        # Behoud directory structuur in output
        relative_path = pdf_file.relative_to(input_path)
        file_output_dir = output_path / relative_path.parent
        file_output_dir.mkdir(parents=True, exist_ok=True)
        
        if convert_pdf_to_images(str(pdf_file), str(file_output_dir), dpi, format):
            success_count += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nBatch conversie voltooid!")
    print(f"Succesvol geconverteerd: {success_count}/{len(pdf_files)} bestanden")
    print(f"Tijd: {duration:.2f} seconden")

def main():
    parser = argparse.ArgumentParser(
        description="MakkelijkPdf CLI - Converteer PDF bestanden naar afbeeldingen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Voorbeelden:
  %(prog)s document.pdf -o output/
  %(prog)s -i input/ -o output/ -f JPG -d 150
  %(prog)s -i input/ -o output/ -r --format PNG
        """
    )
    
    # Input opties
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'input_file',
        nargs='?',
        help='PDF bestand om te converteren'
    )
    input_group.add_argument(
        '-i', '--input-dir',
        help='Directory met PDF bestanden voor batch conversie'
    )
    
    # Output opties
    parser.add_argument(
        '-o', '--output-dir',
        required=True,
        help='Output directory voor afbeeldingen'
    )
    
    # Conversie opties
    parser.add_argument(
        '-d', '--dpi',
        type=int,
        default=300,
        help='DPI voor conversie (standaard: 300)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['PNG', 'JPG', 'JPEG', 'TIFF'],
        default='PNG',
        help='Output formaat (standaard: PNG)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursief zoeken in subdirectories'
    )
    
    args = parser.parse_args()
    
    # Valideer argumenten
    if args.input_file and not os.path.exists(args.input_file):
        print(f"Input bestand bestaat niet: {args.input_file}")
        sys.exit(1)
    
    if args.input_dir and not os.path.exists(args.input_dir):
        print(f"Input directory bestaat niet: {args.input_dir}")
        sys.exit(1)
    
    # Start conversie
    if args.input_file:
        # Enkel bestand conversie
        convert_pdf_to_images(
            args.input_file,
            args.output_dir,
            args.dpi,
            args.format
        )
    else:
        # Batch conversie
        batch_convert(
            args.input_dir,
            args.output_dir,
            args.dpi,
            args.format,
            args.recursive
        )

if __name__ == "__main__":
    main()
