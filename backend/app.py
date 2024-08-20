from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

app = Flask(__name__)

# Function to generate QR code
def generate_qr_code(data, file_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

# Define base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_certificate(name, event_name, details):
    # Create a blank white image for the certificate
    width, height = 1200, 800
    certificate = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(certificate)

    # Set up fonts
    title_font = ImageFont.truetype("arial.ttf", 70)
    name_font = ImageFont.truetype("arial.ttf", 50)
    event_font = ImageFont.truetype("arial.ttf", 40)

    # Add title
    title_text = "Certificate of Appreciation"
    title_width, title_height = draw.textbbox((0, 0), title_text, font=title_font)[2:4]
    title_position = ((width - title_width) / 2, 150)
    draw.text(title_position, title_text, font=title_font, fill="black")

    # Add recipient's name
    name_width, name_height = draw.textbbox((0, 0), name, font=name_font)[2:4]
    name_position = ((width - name_width) / 2, 300)
    draw.text(name_position, name, font=name_font, fill="black")

    # Add event name
    event_text = f"For participating in {event_name}"
    event_width, event_height = draw.textbbox((0, 0), event_text, font=event_font)[2:4]
    event_position = ((width - event_width) / 2, 400)
    draw.text(event_position, event_text, font=event_font, fill="black")

    # Generate the QR code
    qr_code_path = os.path.join(BASE_DIR, "certificates", f"{name}_qr.png")
    generate_qr_code(details, qr_code_path)

    # Add the QR code to the certificate
    qr_code = Image.open(qr_code_path)
    qr_code_size = 150
    qr_code = qr_code.resize((qr_code_size, qr_code_size))
    certificate.paste(qr_code, (width - qr_code_size - 50, height - qr_code_size - 50))

    # Ensure the certificates directory exists
    certificates_dir = os.path.join(BASE_DIR, "certificates")
    os.makedirs(certificates_dir, exist_ok=True)

    # Save the certificate as a PDF
    certificate_path = os.path.join(certificates_dir, f"{name}_certificate.pdf")
    certificate.save(certificate_path)

    return certificate_path




# Route for the frontend form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        event_name = request.form['event_name']
        details = request.form['details']

        certificate_path = generate_certificate(name, event_name, details)
        
        # If the certificate generation failed
        if not os.path.exists(certificate_path):
            return f"Error: Could not generate the certificate.", 500

        return send_file(certificate_path, as_attachment=True)

    return render_template('index.html')


if __name__ == '__main__':
    if not os.path.exists('certificates'):
        os.makedirs('certificates')
    app.run(debug=True)
