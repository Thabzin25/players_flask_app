const express = require('express');
const cors = require('cors');
const db = require('./db');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// Get all players
app.get('/api/players', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM Players');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Add a player
app.post('/api/players', async (req, res) => {
  const { full_name, dob, nationality, position, weight, height, current_club_id, status_id } = req.body;
  try {
    const [result] = await db.query(
      'INSERT INTO Players (full_name, dob, nationality, position, weight, height, current_club_id, status_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [full_name, dob, nationality, position, weight, height, current_club_id, status_id]
    );
    res.json({ id: result.insertId, ...req.body });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete a player
app.delete('/api/players/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM Players WHERE id = ?', [id]);
    res.json({ message: 'Player deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
