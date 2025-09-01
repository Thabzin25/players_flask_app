const express = require('express');
const mysql = require('mysql2');
const router = express.Router();

// Database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Replace with your MySQL username
    password: 'Glink@2003', // Replace with your MySQL password
    database: 'scoutingdb'
});

// Connect to database
db.connect((err) => {
    if (err) {
        console.error('Database connection failed: ', err);
        return;
    }
    console.log('Connected to scoutingdb database for teams');
});

// GET all teams
router.get('/teams', (req, res) => {
    const query = 'SELECT * FROM Clubs ORDER BY name ASC';
    
    db.query(query, (err, results) => {
        if (err) {
            console.error('Error fetching teams:', err);
            return res.status(500).json({ error: 'Failed to fetch teams' });
        }
        res.json(results);
    });
});

// GET team statistics
router.get('/teams/stats', (req, res) => {
    // Get total teams
    const totalTeamsQuery = 'SELECT COUNT(*) as total_teams FROM Clubs';
    
    db.query(totalTeamsQuery, (err, totalResults) => {
        if (err) {
            console.error('Error fetching total teams:', err);
            return res.status(500).json({ error: 'Failed to fetch statistics' });
        }
        
        // Get total countries
        const countriesQuery = 'SELECT COUNT(DISTINCT country) as total_countries FROM Clubs';
        
        db.query(countriesQuery, (err, countriesResults) => {
            if (err) {
                console.error('Error fetching countries count:', err);
                return res.status(500).json({ error: 'Failed to fetch statistics' });
            }
            
            // Get premium teams count
            const premiumQuery = 'SELECT COUNT(*) as premium_teams FROM Clubs WHERE subscription_id = 1';
            
            db.query(premiumQuery, (err, premiumResults) => {
                if (err) {
                    console.error('Error fetching premium teams:', err);
                    return res.status(500).json({ error: 'Failed to fetch statistics' });
                }
                
                // Get oldest team
                const oldestQuery = 'SELECT name, founded_year FROM Clubs ORDER BY founded_year ASC LIMIT 1';
                
                db.query(oldestQuery, (err, oldestResults) => {
                    if (err) {
                        console.error('Error fetching oldest team:', err);
                        return res.status(500).json({ error: 'Failed to fetch statistics' });
                    }
                    
                    // Send response
                    res.json({
                        totalTeams: totalResults[0].total_teams,
                        totalCountries: countriesResults[0].total_countries,
                        premiumTeams: premiumResults[0].premium_teams,
                        oldestTeamName: oldestResults[0] ? oldestResults[0].name : 'N/A',
                        oldestTeamYear: oldestResults[0] ? oldestResults[0].founded_year : 'N/A'
                    });
                });
            });
        });
    });
});

// POST a new team
router.post('/teams', (req, res) => {
    const { name, country, location, manager_name, founded_year, subscription_id } = req.body;
    
    const query = 'INSERT INTO Clubs (name, country, location, manager_name, founded_year, subscription_id) VALUES (?, ?, ?, ?, ?, ?)';
    
    db.query(query, [name, country, location, manager_name, founded_year, subscription_id], (err, results) => {
        if (err) {
            console.error('Error adding team:', err);
            return res.status(500).json({ error: 'Failed to add team' });
        }
        
        // Return the newly created team
        const newTeamQuery = 'SELECT * FROM Clubs WHERE id = ?';
        db.query(newTeamQuery, [results.insertId], (err, teamResults) => {
            if (err) {
                console.error('Error fetching new team:', err);
                return res.status(500).json({ error: 'Failed to fetch new team' });
            }
            
            res.status(201).json(teamResults[0]);
        });
    });
});

// PUT update a team
router.put('/teams/:id', (req, res) => {
    const teamId = req.params.id;
    const { name, country, location, manager_name, founded_year, subscription_id } = req.body;
    
    const query = 'UPDATE Clubs SET name = ?, country = ?, location = ?, manager_name = ?, founded_year = ?, subscription_id = ? WHERE id = ?';
    
    db.query(query, [name, country, location, manager_name, founded_year, subscription_id, teamId], (err, results) => {
        if (err) {
            console.error('Error updating team:', err);
            return res.status(500).json({ error: 'Failed to update team' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }
        
        res.json({ message: 'Team updated successfully' });
    });
});

// DELETE a team
router.delete('/teams/:id', (req, res) => {
    const teamId = req.params.id;
    
    const query = 'DELETE FROM Clubs WHERE id = ?';
    
    db.query(query, [teamId], (err, results) => {
        if (err) {
            console.error('Error deleting team:', err);
            return res.status(500).json({ error: 'Failed to delete team' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }
        
        res.json({ message: 'Team deleted successfully' });
    });
});

module.exports = router;