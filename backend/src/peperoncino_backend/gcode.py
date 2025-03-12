from vpype_cli.cli import cli
import sys
from contextlib import redirect_stdout, redirect_stderr
import io
import os
from pathlib import Path

def convert_svg_to_gcode(input_svg, output_gcode, profile="gcodemm"):
    """
    Converte un file SVG in G-code utilizzando l'API cli di vpype.
    
    Args:
        input_svg (str): Percorso del file SVG di input
        output_gcode (str): Percorso del file G-code di output
        profile (str): Profilo gcode da utilizzare (es. "marlin", "grbl")
    
    Returns:
        str: Contenuto del file G-code generato, o None in caso di errore
    """
    # Costruisci il comando come lista di argomenti
    cmd_args = ["vpype", "read", input_svg, "gwrite", "-p", profile, output_gcode]
    
    # Reindirizza stdout e stderr per catturare l'output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Salva gli argomenti originali e imposta quelli nuovi
    original_argv = sys.argv.copy()
    sys.argv = cmd_args
    
    gcode_content = None
    try:
        # Esegui il comando vpype
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            cli(standalone_mode=False)
        
        # Verifica se il file di output è stato creato
        if os.path.exists(output_gcode):
            # Leggi il contenuto del file G-code
            with open(output_gcode, 'r') as f:
                gcode_content = f.readlines()
        else:
            print(f"Errore: File di output '{output_gcode}' non creato")
    
    except Exception as e:
        print(f"Errore durante la conversione: {str(e)}")
        stderr_output = stderr_capture.getvalue()
        if "inverted across the y-axis" in stderr_output and os.path.exists(output_gcode):
            print("Avviso: Il profilo G-code ha l'asse Y invertito (non è un errore critico)")
            # Leggi il contenuto del file G-code anche se c'è un avviso sull'asse Y
            with open(output_gcode, 'r') as f:
                gcode_content = f.readlines()
        else:
            print(f"Errore: {stderr_output}")
    
    finally:
        # Ripristina gli argomenti originali
        sys.argv = original_argv
    return gcode_content
