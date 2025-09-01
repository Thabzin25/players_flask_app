const express = require('express');
const mysql = require('mysql2');
const router = express.Router();

// Database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Replace with your MySQL username
    password: '', // Replace with your MySQL password
    database: 'scoutingdb'
});

// Connect to database
db.connect((err) => {
    if (err) {
        console.error('Database connection failed: ', err);
        return;
    }
    console.log('Connected to scoutingdb database for subscriptions');
});

// GET all subscriptions with team and plan details
router.get('/subscriptions', (req, res) => {
    const query = `
        SELECT s.*, t.name as team_name, p.name as plan_name 
        FROM Subscriptions s
        JOIN Clubs t ON s.team_id = t.id
        JOIN SubscriptionPlans p ON s.plan_id = p.id
        ORDER BY s.created_at DESC
    `;
    
    db.query(query, (err, results) => {
        if (err) {
            console.error('Error fetching subscriptions:', err);
            return res.status(500).json({ error: 'Failed to fetch subscriptions' });
        }
        res.json(results);
    });
});

// GET subscription statistics
router.get('/subscriptions/stats', (req, res) => {
    // Get total active subscriptions
    const totalSubscriptionsQuery = 'SELECT COUNT(*) as total FROM Subscriptions WHERE status = "active"';
    
    db.query(totalSubscriptionsQuery, (err, totalResults) => {
        if (err) {
            console.error('Error fetching total subscriptions:', err);
            return res.status(500).json({ error: 'Failed to fetch statistics' });
        }
        
        // Get monthly revenue
        const currentMonth = new Date().getMonth() + 1;
        const monthlyRevenueQuery = `
            SELECT SUM(p.price) as revenue 
            FROM Subscriptions s
            JOIN SubscriptionPlans p ON s.plan_id = p.id
            WHERE MONTH(s.start_date) = ? AND s.status = "active"
        `;
        
        db.query(monthlyRevenueQuery, [currentMonth], (err, revenueResults) => {
            if (err) {
                console.error('Error fetching monthly revenue:', err);
                return res.status(500).json({ error: 'Failed to fetch statistics' });
            }
            
            // Get growth rate (simplified)
            const growthRateQuery = `
                SELECT COUNT(*) as last_month_count 
                FROM Subscriptions 
                WHERE MONTH(created_at) = MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH)) 
                AND status = "active"
            `;
            
            db.query(growthRateQuery, (err, growthResults) => {
                if (err) {
                    console.error('Error fetching growth rate:', err);
                    return res.status(500).json({ error: 'Failed to fetch statistics' });
                }
                
                const lastMonthCount = growthResults[0].last_month_count;
                const currentMonthCount = totalResults[0].total;
                
                let growthRate = 0;
                if (lastMonthCount > 0) {
                    growthRate = Math.round(((currentMonthCount - lastMonthCount) / lastMonthCount) * 100);
                }
                
                // Send response
                res.json({
                    totalSubscriptions: totalResults[0].total,
                    monthlyRevenue: revenueResults[0].revenue || 0,
                    growthRate: growthRate
                });
            });
        });
    });
});

// Additional routes for managing subscriptions would go here
// POST, PUT, DELETE operations for subscriptions

module.exports = router;