from flask import Flask, render_template, request, send_file
from PIL import Image
import stepic
import os
import io

app = Flask(__name__)

# Fungsi untuk mengenkripsi teks menggunakan Caesar Cipher (menghasilkan ASCII)
def caesar_cipher_encrypt(text, shift):
    result = []
    ascii_values = []
    
    for char in text:
        if char.isupper():  # Jika huruf besar
            encrypted_char = chr((ord(char) + shift - 65) % 26 + 65)
        elif char.islower():  # Jika huruf kecil
            encrypted_char = chr((ord(char) + shift - 97) % 26 + 97)
        else:  # Jika karakter bukan huruf (angka atau simbol)
            encrypted_char = char
        
        # Menyimpan hasil karakter dan ASCII-nya
        result.append(encrypted_char)
        ascii_values.append(ord(encrypted_char))
    
    return result, ascii_values

# Fungsi untuk mendekripsi teks berdasarkan ASCII dan shift
def caesar_cipher_decrypt(encrypted_text, shift):
    decrypted_text = []
    
    for char in encrypted_text:
        if char.isupper():  # Huruf kapital
            decrypted_char = chr((ord(char) - shift - 65) % 26 + 65)
        elif char.islower():  # Huruf kecil
            decrypted_char = chr((ord(char) - shift - 97) % 26 + 97)
        else:
            decrypted_char = char  # Jika karakter non-alfabet
        decrypted_text.append(decrypted_char)
    
    return ''.join(decrypted_text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        text = request.form.get('text')
        shift = int(request.form.get('key'))
        encrypted_chars, _ = caesar_cipher_encrypt(text, shift)
        
        return {
            'encrypted_text': ''.join(encrypted_chars)
        }
    
    return render_template('Encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        text = request.form.get('text')
        shift = int(request.form.get('key'))
        decrypted_text = caesar_cipher_decrypt(text, shift)
        
        return {
            'decrypted_text': decrypted_text
        }
    
    return render_template('Decrypt.html')

@app.route('/stegano_encrypt', methods=['POST'])
def stegano_encrypt():
    if request.method == 'POST':
        try:
            # Validasi input
            if 'image' not in request.files:
                return {'error': 'Tidak ada file gambar yang dikirim'}, 400
            if 'text' not in request.form:
                return {'error': 'Tidak ada teks yang dikirim'}, 400
            
            text = request.form.get('text')
            image_file = request.files.get('image')
            
            if image_file.filename == '':
                return {'error': 'Nama file kosong'}, 400

            # Baca gambar
            image = Image.open(image_file)
            
            # Konversi ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Proses steganografi menggunakan stepic
            output = stepic.encode(image, text.encode())
            
            # Simpan ke BytesIO
            img_io = io.BytesIO()
            output.save(img_io, 'PNG', quality=100)
            img_io.seek(0)
            
            return send_file(
                img_io,
                mimetype='image/png',
                as_attachment=True,
                download_name='stegano_result.png'
            )
                
        except Exception as e:
            print(f"Error detail: {str(e)}")
            return {'error': f'Gagal melakukan steganografi: {str(e)}'}, 400

@app.route('/stegano_decrypt', methods=['POST'])
def stegano_decrypt():
    if request.method == 'POST':
        try:
            # Validasi input
            if 'image' not in request.files:
                return {'error': 'Tidak ada file gambar yang dikirim'}, 400
            
            image_file = request.files.get('image')
            
            if image_file.filename == '':
                return {'error': 'Nama file kosong'}, 400

            # Baca gambar
            image = Image.open(image_file)
            
            # Konversi ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Dekripsi menggunakan stepic
            decoded_text = stepic.decode(image)
            
            return {
                'success': True,
                'decoded_text': decoded_text
            }
                
        except Exception as e:
            print(f"Error detail: {str(e)}")
            return {'error': f'Gagal melakukan dekripsi steganografi: {str(e)}'}, 400

if __name__ == '__main__':
    app.run(debug=True)
