from flask import Flask, request, send_file, render_template
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar los datos del CSV
data_path = "index.csv"
if os.path.exists(data_path):
    data = pd.read_csv(data_path, encoding="latin1")
else:
    data = None
    print(f"Error: El archivo {data_path} no se encuentra.")

# Ruta principal para mostrar el formulario
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para generar la credencial
@app.route("/generar-credencial", methods=["POST"])
def generar_credencial():
    if data is None:
        return "No se puede generar la credencial porque no se cargaron los datos del archivo CSV.", 500

    dni = request.form.get("dni")

    # Validar que el DNI no esté vacío
    if not dni:
        return "El campo DNI es obligatorio. Por favor, inténtelo nuevamente.", 400

    # Buscar al empleado por DNI
    empleado = data[data["Nro. de Documento 1"].astype(str) == dni]

    if empleado.empty:
        return "No se encontró al empleado con ese DNI. Por favor, verifique e intente nuevamente.", 404

    # Extraer información del empleado
    nombre = empleado.iloc[0]["Apellido y Nombre"]
    familiares = empleado.iloc[0]["Familiares"]

    # Generar el PDF con estilo mejorado
    pdf = FPDF(format=(105, 148))  # Tamaño personalizado (A6)
    pdf.add_page()

    # Fondo de color claro
    pdf.set_fill_color(255, 255, 255)  # AliceBlue
    pdf.rect(0, 0, 105, 148, 'F')

    # Agregar logo
    logo_path = "logo2.jpg"  # Ruta al logo de la empresa
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=36, y=-4 , w=35)  # Ajustar posición y tamaño del logo
    else:
        print(f"Advertencia: No se encontró el archivo del logo en {logo_path}")

    # Título principal
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_text_color(51, 51, 51)  # Gris oscuro
    pdf.cell(0, 10, "IMSA - Credencial para la Pileta", ln=True, align='C')
    pdf.ln(10)

 
    # Información del empleado
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Apellido y Nombre: {nombre}", ln=True, align='L')
    pdf.cell(0, 10, f"DNI: {dni}", ln=True, align='L')
    pdf.cell(0, 10, f"Cantidad de familiares: {familiares}", ln=True, align='L')
    pdf.ln(10)

    # Mensaje de invitación
    pdf.set_text_color(255, 107, 107)  # Coral
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, "Pileta SPIQYP - Válido hasta el 28/02/25", ln=True, align='C')

    # Footer
    pdf.set_font("Arial", style="I", size=8)
    pdf.set_text_color(136, 136, 136)  # Gris claro
    pdf.ln(10)
    pdf.cell(0, 10, "Equipo de RRHH", ln=True, align='C')

    # Guardar el PDF como bytes
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_output)

    # Enviar el PDF como respuesta
    return send_file(pdf_buffer, as_attachment=True, download_name=f"credencial_{dni}.pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Obtiene el puerto de la variable de entorno o usa 5000 por defecto
    app.run(host="0.0.0.0", port=port)
