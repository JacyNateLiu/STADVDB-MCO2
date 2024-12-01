const express = require('express');
const mysql = require('mysql2');
const app = express();
const port = 3000;

// Create a connection to the MySQL database
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'game_store'
});

// Connect to the database
db.connect(err => {
    if (err) {
        console.error('Database connection failed:', err.stack);
        return;
    }
    console.log('Connected to the database.');
});

// API endpoint to fetch games
app.get('/api/games', (req, res) => {
    const query = 'SELECT * FROM multi_platforms';
    db.query(query, (err, results) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error retrieving games');
            return;
        }
        res.json(results);
    });
});

// Serve the frontend files
app.use(express.static('frontend'));

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
