from flask import Flask, request, jsonify
import sqlite3
from database import init_db

app = Flask(__name__)
init_db()

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.get_json()
    nombre = data.get('nombre')
    fecha = data.get('fecha')
    hora = data.get('hora')

    if not nombre or not fecha or not hora:
        return jsonify({'status': 'error', 'message': 'Faltan campos requeridos'}), 400

    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute("SELECT * FROM citas WHERE fecha=? AND hora=?", (fecha, hora))
    if c.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': 'Hora ya ocupada o bloqueada'}), 409

    c.execute("INSERT INTO citas (nombre, fecha, hora) VALUES (?, ?, ?)", (nombre, fecha, hora))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'message': 'Cita registrada exitosamente'}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
