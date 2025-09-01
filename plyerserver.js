const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'Glink@2003'; // In production, use environment variable

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public')); // Serve static files

// Mock database (in production, use a real database)
let users = [
    {
        id: 1,
        clubName: 'Demo Club',
        email: 'demo@club.com',
        password: '$2a$10$8K1p/a0dRaPh6WIGdJ5.5uG6oRc5H6L7xNlL6cKZJZJZJZJZJZJZJ', // password: demo123
        subscription: {
            plan: 'premium',
            planName: 'Premium Club',
            billingCycle: 'monthly',
            price: 49.99,
            status: 'active',
            nextBillingDate: '2023-08-15'
        },
        paymentMethods: [
            {
                id: 1,
                type: 'visa',
                last4: '1234',
                expiry: '12/2024',
                isDefault: true
            }
        ],
        paymentHistory: [
            {
                id: 1,
                date: '2023-07-15',
                amount: 49.99,
                method: { type: 'visa', last4: '1234' },
                status: 'completed'
            },
            {
                id: 2,
                date: '2023-06-15',
                amount: 49.99,
                method: { type: 'visa', last4: '1234' },
                status: 'completed'
            }
        ]
    }
];

// Authentication middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid token' });
        }
        req.user = user;
        next();
    });
};

// Routes

// Login route
app.post('/api/login', (req, res) => {
    const { email, password } = req.body;
    
    const user = users.find(u => u.email === email);
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // In a real app, compare hashed password
    if (password !== 'demo123') {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign(
        { id: user.id, email: user.email }, 
        JWT_SECRET, 
        { expiresIn: '24h' }
    );
    
    res.json({ token, user: { id: user.id, clubName: user.clubName, email: user.email } });
});

// Get subscription data
app.get('/api/subscription', authenticateToken, (req, res) => {
    const user = users.find(u => u.id === req.user.id);
    res.json(user.subscription);
});

// Cancel subscription
app.post('/api/subscription/cancel', authenticateToken, (req, res) => {
    const user = users.find(u => u.id === req.user.id);
    user.subscription.status = 'cancelled';
    res.json({ message: 'Subscription cancelled successfully' });
});

// Change plan
app.post('/api/subscription/change-plan', authenticateToken, (req, res) => {
    const { plan } = req.body;
    const user = users.find(u => u.id === req.user.id);
    
    const planMap = {
        'basic': { name: 'Basic Club', price: 19.99 },
        'premium': { name: 'Premium Club', price: 49.99 },
        'enterprise': { name: 'Enterprise Club', price: 99.99 }
    };
    
    user.subscription.plan = plan;
    user.subscription.planName = planMap[plan].name;
    user.subscription.price = planMap[plan].price;
    
    res.json({ message: 'Plan changed successfully' });
});

// Get payment methods
app.get('/api/payment-methods', authenticateToken, (req, res) => {
    const user = users.find(u => u.id === req.user.id);
    res.json(user.paymentMethods);
});

// Add payment method
app.post('/api/payment-methods', authenticateToken, (req, res) => {
    const { cardNumber, cardHolder, expiryDate, cvv } = req.body;
    const user = users.find(u => u.id === req.user.id);
    
    // Simple card type detection
    let type = 'credit';
    if (/^4/.test(cardNumber)) type = 'visa';
    if (/^5[1-5]/.test(cardNumber)) type = 'mastercard';
    if (/^3[47]/.test(cardNumber)) type = 'amex';
    
    const newMethod = {
        id: user.paymentMethods.length + 1,
        type,
        last4: cardNumber.slice(-4),
        expiry: expiryDate,
        isDefault: false
    };
    
    user.paymentMethods.push(newMethod);
    res.json({ message: 'Payment method added successfully', method: newMethod });
});

// Get payment history
app.get('/api/payment-history', authenticateToken, (req, res) => {
    const user = users.find(u => u.id === req.user.id);
    res.json(user.paymentHistory);
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});