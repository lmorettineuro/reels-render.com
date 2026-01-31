import os
import requests
from flask import Flask, request, send_file
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile

app = Flask(__name__)

# Configuración básica
FONT_SIZE = 50
FONT_COLOR = 'white'
STROKE_COLOR = 'black'
STROKE_WIDTH = 2
FONT = 'Arial-Bold' # MoviePy buscará una fuente predeterminada o ImageMagick

def download_file(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

def wrap_text(text, width=20):
    """Rompe el texto en líneas de 'width' caracteres aprox"""
    import textwrap
    return "\n".join(textwrap.wrap(text, width=width))

@app.route('/render', methods=['POST'])
def render_video():
    data = request.json
    video_url = data.get('video_url')
    overlay_text = data.get('text', '')
    
    if not video_url:
        return {"error": "Falta video_url"}, 400

    # Archivos temporales
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.mp4")
    output_path = os.path.join(temp_dir, "output.mp4")

    try:
        # 1. Descargar video
        print(f"Descargando video: {video_url}")
        download_file(video_url, input_path)

        # 2. Procesar con MoviePy
        clip = VideoFileClip(input_path)
        
        # Preparar texto (centrado, con borde negro para legibilidad)
        # Nota: 'method="caption"' ajusta el tamaño automáticamente al cuadro
        # pero aquí usaremos texto simple centrado.
        wrapped_text = wrap_text(overlay_text, width=25)
        
        # Crear el clip de texto
        txt_clip = (TextClip(wrapped_text, fontsize=FONT_SIZE, color=FONT_COLOR, 
                             stroke_color=STROKE_COLOR, stroke_width=STROKE_WIDTH, font='Arial')
                    .set_position('center')
                    .set_duration(clip.duration))

        # Componer
        final = CompositeVideoClip([clip, txt_clip])
        
        # Escribir archivo (usamos codec libx264 para compatibilidad)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', 
                              temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"), 
                              remove_temp=True, fps=24)
        
        # 3. Devolver el archivo binario
        return send_file(output_path, mimetype='video/mp4')

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Limpieza (opcional, el contenedor se destruye eventualmente)
        clip.close()

if __name__ == '__main__':
    # Puerto necesario para Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
