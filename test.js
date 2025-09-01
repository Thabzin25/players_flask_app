const db = require('./db'); // <- only declare once

async function testConnection() {
  try {
    const [rows] = await db.query('SELECT * FROM Players');
    console.log(rows);
  } catch (err) {
    console.error('Error connecting to database:', err);
  }
}

testConnection();
