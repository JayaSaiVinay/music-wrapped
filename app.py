from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import pandas as pd
import os

app = Flask(__name__)

# Set up a folder for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(host='localhost', user='root', passwd='root', database='spotify')

# Route to upload CSV file
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Save the file to the server
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Read the CSV into a DataFrame
            df = pd.read_csv(file_path)

            # Clean column names
            df.columns = df.columns.str.strip()

            # Insert data into MySQL
            mydb = get_db_connection()
            mycursor = mydb.cursor()

            # Clear previous data in the table (optional, if each upload should overwrite existing data)
            mycursor.execute("DELETE FROM test")
            
            # Insert new data
            for _, row in df.iterrows():
                sql = "INSERT INTO test (endTime, artistName, trackName, msPlayed) VALUES (%s, %s, %s, %s)"
                val = (row['endTime'], row['artistName'], row['trackName'], row['msPlayed'])
                mycursor.execute(sql, val)

            mydb.commit()
            mycursor.close()
            mydb.close()

            return redirect(url_for('top_tracks'))

    return render_template('upload.html')

# Route to display top tracks
@app.route('/top_tracks')
def top_tracks():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    sql = """
    SELECT trackName, artistName, SUM(msPlayed) / 60000 AS totalMinutes
    FROM test
    GROUP BY artistName, trackName
    ORDER BY totalMinutes DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('top_tracks.html', top_tracks=result)

# Route to display top tracks excluding night listening
@app.route('/top_tracks_removing_night')
def top_tracks_removing_night():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    sql = """
    SELECT trackName, artistName, SUM(msPlayed) / 60000 AS totalMinutes
    FROM test
    WHERE HOUR(endTime) >= 9 AND HOUR(endTime) < 23 AND artistName != "Epir"
    GROUP BY artistName, trackName
    ORDER BY totalMinutes DESC
    LIMIT 100;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('top_tracks_removing_night.html', result=result)

# Route to display top tracks by play count
@app.route('/top_tracks_by_count')
def top_tracks_by_count():
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    sql = """
    SELECT trackName, artistName, COUNT(*) AS playCount
    FROM test
    WHERE msPlayed > 30000 
    AND artistName NOT IN ("Epir", "Celtic Traveler", "Harmony Tales", "Fantasy Village", "Eldenwood")
    AND MONTH(endTime) <= 10
    GROUP BY artistName, trackName
    ORDER BY playCount DESC
    LIMIT 15;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return render_template('top_tracks_by_count.html', tracks=result)

if __name__ == '__main__':
    app.run(debug=True)
