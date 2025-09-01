const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database connection
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'Glink@2003',
  database: 'scoutingdb'
});

db.connect((err) => {
  if (err) {
    console.error('Database connection failed: ' + err.stack);
    return;
  }
  console.log('Connected to database.');
});

// API Routes for Players
app.get('/api/players', (req, res) => {
  const query = `
    SELECT Players.playerId, Players.fullName, Players.dob, 
           Players.nationality, Players.position, Players.weight, 
           Players.height, Clubs.name as clubName, Clubs.clubId
    FROM Players 
    LEFT JOIN Clubs ON Players.currentClubId = Clubs.clubId
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch players' });
    } else {
      res.json(results);
    }
  });
});

app.post('/api/players', (req, res) => {
  const { fullName, dob, nationality, position, weight, height, currentClubId } = req.body;
  
  const query = `
    INSERT INTO Players (fullName, dob, nationality, position, weight, height, currentClubId)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `;
  
  db.query(query, [fullName, dob, nationality, position, weight, height, currentClubId], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to add player' });
      } else {
        res.json({ message: 'Player added successfully', id: results.insertId });
      }
    }
  );
});

app.delete('/api/players/:id', (req, res) => {
  const playerId = req.params.id;
  
  const query = 'DELETE FROM Players WHERE playerId = ?';
  
  db.query(query, [playerId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to delete player' });
    } else {
      res.json({ message: 'Player deleted successfully' });
    }
  });
});

// API Routes for Scouts
app.get('/api/scouts', (req, res) => {
  const query = `
    SELECT 
      s.scoutId, 
      s.name, 
      s.region, 
      s.contactInfo, 
      s.experienceLevel, 
      s.statusId,
      st.description AS status, 
      s.assignedClubId,
      c.name AS assignedClub, 
      s.players_found,
      s.success_rate
    FROM Scouts s
    LEFT JOIN Statuses st ON s.statusId = st.statusId
    LEFT JOIN Clubs c ON s.assignedClubId = c.clubId
    ORDER BY s.scoutId
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch scouts' });
    } else {
      res.json(results);
    }
  });
});

app.post('/api/scouts', (req, res) => {
  const { name, region, contactInfo, experienceLevel, statusId, assignedClubId, players_found, success_rate } = req.body;
  
  const query = `
    INSERT INTO Scouts (name, region, contactInfo, experienceLevel, statusId, assignedClubId, players_found, success_rate)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;
  
  db.query(query, [name, region, contactInfo, experienceLevel, statusId, assignedClubId || null, players_found || 0, success_rate || 0], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to add scout: ' + err.message });
      } else {
        res.json({ message: 'Scout added successfully', id: results.insertId });
      }
    }
  );
});

app.put('/api/scouts/:id', (req, res) => {
  const scoutId = req.params.id;
  const { name, region, contactInfo, experienceLevel, statusId, assignedClubId, players_found, success_rate } = req.body;

  const query = `
    UPDATE Scouts 
    SET name = ?, region = ?, contactInfo = ?, experienceLevel = ?, statusId = ?, assignedClubId = ?, players_found = ?, success_rate = ?
    WHERE scoutId = ?
  `;
  
  db.query(query, [name, region, contactInfo, experienceLevel, statusId, assignedClubId || null, players_found || 0, success_rate || 0, scoutId], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to update scout' });
      } else {
        res.json({ message: 'Scout updated successfully' });
      }
    }
  );
});

// Update only scout stats
app.put('/api/scouts/:id/stats', (req, res) => {
  const scoutId = req.params.id;
  const { players_found, success_rate } = req.body;

  const query = `
    UPDATE Scouts 
    SET players_found = ?, success_rate = ?
    WHERE scoutId = ?
  `;
  
  db.query(query, [players_found || 0, success_rate || 0, scoutId], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to update scout stats' });
      } else {
        res.json({ message: 'Scout stats updated successfully' });
      }
    }
  );
});

app.delete('/api/scouts/:id', (req, res) => {
  const scoutId = req.params.id;
  
  const query = 'DELETE FROM Scouts WHERE scoutId = ?';
  
  db.query(query, [scoutId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to delete scout' });
    } else {
      res.json({ message: 'Scout deleted successfully' });
    }
  });
});

// Get scout statistics
app.get('/api/scouts/stats', (req, res) => {
  const query = `
    SELECT 
      (SELECT COUNT(*) FROM Scouts) as totalScouts,
      (SELECT COUNT(*) FROM Scouts WHERE statusId = 1) as activeScouts,
      (SELECT COUNT(*) FROM Scouts WHERE statusId != 1) as inactiveScouts,
      (SELECT COALESCE(AVG(success_rate), 0) FROM Scouts) as avgSuccessRate,
      (SELECT COALESCE(SUM(players_found), 0) FROM Scouts) as totalPlayersFound
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch scout statistics' });
    } else {
      // Get most active scout
      const mostActiveQuery = `
        SELECT name, players_found, success_rate 
        FROM Scouts 
        ORDER BY players_found DESC 
        LIMIT 1
      `;
      
      db.query(mostActiveQuery, (err, mostActiveResult) => {
        if (err) {
          console.error(err);
          res.status(500).json({ error: 'Failed to fetch most active scout' });
        } else {
          const mostActive = mostActiveResult[0] || { 
            name: "No data", 
            players_found: 0, 
            success_rate: 0 
          };
          
          // Get least active scout
          const leastActiveQuery = `
            SELECT name, players_found, success_rate 
            FROM Scouts 
            WHERE players_found > 0 
            ORDER BY players_found ASC 
            LIMIT 1
          `;
          
          db.query(leastActiveQuery, (err, leastActiveResult) => {
            if (err) {
              console.error(err);
              res.status(500).json({ error: 'Failed to fetch least active scout' });
            } else {
              const leastActive = leastActiveResult[0] || { 
                name: "No data", 
                players_found: 0, 
                success_rate: 0 
              };
              
              // Generate initials for avatars
              mostActive.initials = mostActive.name ? 
                mostActive.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2) : 'N/A';
                
              leastActive.initials = leastActive.name ? 
                leastActive.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2) : 'N/A';
              
              // Add weekly activity data (dummy data for demo)
              const weeklyActivity = [
                { label: "Mon", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Tue", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Wed", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Thu", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Fri", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Sat", value: Math.floor(Math.random() * 40) + 60 },
                { label: "Sun", value: Math.floor(Math.random() * 40) + 60 }
              ];
              
              res.json({
                totalScouts: results[0].totalScouts,
                activeScouts: results[0].activeScouts,
                inactiveScouts: results[0].inactiveScouts,
                avgSuccessRate: Math.round(results[0].avgSuccessRate),
                totalPlayersFound: results[0].totalPlayersFound,
                mostActive: mostActive,
                leastActive: leastActive,
                weeklyActivity: weeklyActivity,
                percentageChange: Math.floor(Math.random() * 21) - 10 // Random between -10 and +10
              });
            }
          });
        }
      });
    }
  });
});

// Get clubs for dropdown
app.get('/api/clubs', (req, res) => {
  const query = 'SELECT clubId, name FROM Clubs ORDER BY name';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch clubs' });
    } else {
      res.json(results);
    }
  });
});

// Get statuses for dropdown
app.get('/api/statuses', (req, res) => {
  const query = 'SELECT statusId, description FROM Statuses ORDER BY statusId';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch statuses' });
    } else {
      res.json(results);
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});



// API Routes for Teams

// Get all teams
app.get('/api/teams', (req, res) => {
  const query = 'SELECT * FROM Clubs ORDER BY name';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch teams' });
    } else {
      res.json(results);
    }
  });
});

// Add a new team
app.post('/api/teams', (req, res) => {
  const { name, country, location, managerName, foundedYear } = req.body;
  
  const query = `
    INSERT INTO Clubs (name, country, location, managerName, foundedYear)
    VALUES (?, ?, ?, ?, ?)
  `;
  
  db.query(query, [name, country, location, managerName, foundedYear], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to add team' });
      } else {
        res.json({ message: 'Team added successfully', id: results.insertId });
      }
    }
  );
});

// Update a team
app.put('/api/teams/:id', (req, res) => {
  const teamId = req.params.id;
  const { name, country, location, managerName, foundedYear } = req.body;

  const query = `
    UPDATE Clubs 
    SET name = ?, country = ?, location = ?, managerName = ?, foundedYear = ?
    WHERE clubId = ?
  `;
  
  db.query(query, [name, country, location, managerName, foundedYear, teamId], 
    (err, results) => {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to update team' });
      } else {
        res.json({ message: 'Team updated successfully' });
      }
    }
  );
});

// Delete a team
app.delete('/api/teams/:id', (req, res) => {
  const teamId = req.params.id;
  
  const query = 'DELETE FROM Clubs WHERE clubId = ?';
  
  db.query(query, [teamId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to delete team' });
    } else {
      res.json({ message: 'Team deleted successfully' });
    }
  });
});

// Get team statistics
app.get('/api/teams/stats', (req, res) => {
  const query = `
    SELECT 
      (SELECT COUNT(*) FROM Clubs) as totalTeams,
      (SELECT COUNT(DISTINCT country) FROM Clubs) as totalCountries,
      (SELECT MIN(foundedYear) FROM Clubs) as oldestTeamYear
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch team statistics' });
    } else {
      res.json(results[0]);
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});



// API Routes for Subscriptions

// Get all subscriptions with related data
app.get('/api/subscriptions', (req, res) => {
  const query = `
    SELECT 
      s.subscriptionId,
      s.description,
      s.plan,
      s.statusId,
      s.scoutId,
      s.clubId,
      s.amount,
      s.start_date,
      s.renewal_date,
      st.description as status,
      c.name as team_name,
      sc.name as scout_name
    FROM Subscriptions s
    LEFT JOIN Statuses st ON s.statusId = st.statusId
    LEFT JOIN Clubs c ON s.clubId = c.clubId
    LEFT JOIN Scouts sc ON s.scoutId = sc.scoutId
    ORDER BY s.renewal_date DESC
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch subscriptions' });
    } else {
      res.json(results);
    }
  });
});

// Get a single subscription
app.get('/api/subscriptions/:id', (req, res) => {
  const subscriptionId = req.params.id;
  
  const query = `
    SELECT 
      s.subscriptionId,
      s.description,
      s.plan,
      s.statusId,
      s.scoutId,
      s.clubId,
      s.amount,
      s.start_date,
      s.renewal_date,
      st.description as status,
      c.name as team_name,
      sc.name as scout_name
    FROM Subscriptions s
    LEFT JOIN Statuses st ON s.statusId = st.statusId
    LEFT JOIN Clubs c ON s.clubId = c.clubId
    LEFT JOIN Scouts sc ON s.scoutId = sc.scoutId
    WHERE s.subscriptionId = ?
  `;
  
  db.query(query, [subscriptionId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch subscription' });
    } else if (results.length === 0) {
      res.status(404).json({ error: 'Subscription not found' });
    } else {
      res.json(results[0]);
    }
  });
});

// Get payment history for a subscription
app.get('/api/subscriptions/:id/payments', (req, res) => {
  const subscriptionId = req.params.id;
  
  const query = `
    SELECT 
      paymentId,
      paymentDate,
      amount,
      paymentMethod
    FROM Payments
    WHERE subscriptionId = ?
    ORDER BY paymentDate DESC
  `;
  
  db.query(query, [subscriptionId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch payment history' });
    } else {
      res.json(results);
    }
  });
});

// Add a new subscription
app.post('/api/subscriptions', (req, res) => {
  const { subscriberType, subscriberId, planId, startDate, paymentMethod } = req.body;
  
  // Determine plan details based on planId
  let planName, amount;
  switch (planId) {
    case '1':
      planName = 'Basic';
      amount = 29;
      break;
    case '2':
      planName = 'Pro';
      amount = 79;
      break;
    case '3':
      planName = 'Premium';
      amount = 149;
      break;
    default:
      return res.status(400).json({ error: 'Invalid plan ID' });
  }
  
  // Calculate renewal date (1 month from start date)
  const renewalDate = new Date(startDate);
  renewalDate.setMonth(renewalDate.getMonth() + 1);
  
  // Prepare subscription data
  const subscriptionData = {
    description: `${planName} Plan Subscription`,
    plan: planName,
    statusId: 1, // Active
    amount: amount,
    start_date: startDate,
    renewal_date: renewalDate.toISOString().split('T')[0]
  };
  
  // Set subscriber type
  if (subscriberType === 'team') {
    subscriptionData.clubId = subscriberId;
  } else if (subscriberType === 'scout') {
    subscriptionData.scoutId = subscriberId;
  } else {
    return res.status(400).json({ error: 'Invalid subscriber type' });
  }
  
  // Insert subscription
  const subscriptionQuery = 'INSERT INTO Subscriptions SET ?';
  
  db.query(subscriptionQuery, subscriptionData, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to add subscription' });
    } else {
      const subscriptionId = results.insertId;
      
      // Create initial payment record
      const paymentData = {
        subscriptionId: subscriptionId,
        paymentDate: new Date().toISOString().split('T')[0],
        amount: amount,
        paymentMethod: paymentMethod
      };
      
      const paymentQuery = 'INSERT INTO Payments SET ?';
      
      db.query(paymentQuery, paymentData, (err, paymentResults) => {
        if (err) {
          console.error(err);
          // We'll still return success since the subscription was created
          res.json({ message: 'Subscription created successfully', id: subscriptionId });
        } else {
          res.json({ message: 'Subscription created successfully', id: subscriptionId });
        }
      });
    }
  });
});

// Renew a subscription
app.post('/api/subscriptions/:id/renew', (req, res) => {
  const subscriptionId = req.params.id;
  
  // Get current subscription details
  const getQuery = 'SELECT * FROM Subscriptions WHERE subscriptionId = ?';
  
  db.query(getQuery, [subscriptionId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch subscription' });
    } else if (results.length === 0) {
      res.status(404).json({ error: 'Subscription not found' });
    } else {
      const subscription = results[0];
      
      // Calculate new renewal date (1 month from current renewal date)
      const newRenewalDate = new Date(subscription.renewal_date);
      newRenewalDate.setMonth(newRenewalDate.getMonth() + 1);
      
      // Update subscription
      const updateQuery = `
        UPDATE Subscriptions 
        SET renewal_date = ?, statusId = 1 
        WHERE subscriptionId = ?
      `;
      
      db.query(updateQuery, [newRenewalDate, subscriptionId], (err, updateResults) => {
        if (err) {
          console.error(err);
          res.status(500).json({ error: 'Failed to renew subscription' });
        } else {
          // Create payment record
          const paymentData = {
            subscriptionId: subscriptionId,
            paymentDate: new Date().toISOString().split('T')[0],
            amount: subscription.amount,
            paymentMethod: 'renewal'
          };
          
          const paymentQuery = 'INSERT INTO Payments SET ?';
          
          db.query(paymentQuery, paymentData, (err, paymentResults) => {
            if (err) {
              console.error(err);
              // We'll still return success since the subscription was renewed
              res.json({ message: 'Subscription renewed successfully' });
            } else {
              res.json({ message: 'Subscription renewed successfully' });
            }
          });
        }
      });
    }
  });
});

// Cancel a subscription
app.delete('/api/subscriptions/:id', (req, res) => {
  const subscriptionId = req.params.id;
  
  const query = 'UPDATE Subscriptions SET statusId = 3 WHERE subscriptionId = ?';
  
  db.query(query, [subscriptionId], (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to cancel subscription' });
    } else {
      res.json({ message: 'Subscription canceled successfully' });
    }
  });
});

// Get subscription statistics
app.get('/api/subscriptions/stats', (req, res) => {
  const query = `
    SELECT 
      (SELECT COUNT(*) FROM Subscriptions WHERE statusId = 1) as totalSubscriptions,
      (SELECT COALESCE(SUM(amount), 0) FROM Subscriptions WHERE statusId = 1) as monthlyRevenue,
      (SELECT COUNT(*) FROM Subscriptions WHERE statusId = 1 AND renewal_date > DATE_SUB(NOW(), INTERVAL 1 MONTH)) as newSubscriptions
  `;
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch subscription statistics' });
    } else {
      const stats = results[0];
      
      // Calculate growth rate (dummy calculation for demo)
      const growthRate = Math.min(100, Math.floor(Math.random() * 30) + 5);
      
      res.json({
        totalSubscriptions: stats.totalSubscriptions,
        monthlyRevenue: stats.monthlyRevenue,
        growthRate: growthRate
      });
    }
  });
});

// Get all teams
app.get('/api/teams', (req, res) => {
  const query = 'SELECT clubId, name FROM Clubs ORDER BY name';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch teams' });
    } else {
      res.json(results);
    }
  });
});

// Get all scouts
app.get('/api/scouts', (req, res) => {
  const query = 'SELECT scoutId, name FROM Scouts ORDER BY name';
  
  db.query(query, (err, results) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch scouts' });
    } else {
      res.json(results);
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});


// Registration endpoint
app.post('/register', async (req, res) => {
  const {
    firstName,
    lastName,
    email,
    mobile,
    idType,
    idNumber,
    country,
    gender,
    dob,
    password,
    role,
    licenseNumber,
    experience,
    region,
    clubName,
    clubRegistration,
    league,
    website,
    position,
    foot,
    height,
    weight,
    currentClub
  } = req.body;

  try {
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insert based on role
    if (role === 'Player') {
      // Calculate age from DOB
      const birthDate = new Date(dob);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }

      // Insert into players table
      const playerQuery = `INSERT INTO players (fullName, dob, nationality, position, weight, height, statusId, Age) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
      const playerValues = [
        `${firstName} ${lastName}`,
        dob,
        country,
        position,
        weight,
        height,
        1, // Assuming statusId 1 is "Active"
        age
      ];

      db.execute(playerQuery, playerValues, (err, results) => {
        if (err) {
          console.error(err);
          return res.status(500).json({ message: 'Database error' });
        }
        res.json({ message: 'Player registered successfully' });
      });

    } else if (role === 'Scout') {
      // Insert into scouts table
      const scoutQuery = `INSERT INTO scouts (name, region, contactInfo, experienceLevel, statusId) 
                          VALUES (?, ?, ?, ?, ?)`;
      const scoutValues = [
        `${firstName} ${lastName}`,
        region,
        email,
        `${experience} years`,
        1 // Assuming statusId 1 is "Active"
      ];

      db.execute(scoutQuery, scoutValues, (err, results) => {
        if (err) {
          console.error(err);
          return res.status(500).json({ message: 'Database error' });
        }
        
        // Create a basic subscription for the scout
        const subscriptionQuery = `INSERT INTO subscriptions (description, plan, statusId, scoutId, Amount) 
                                   VALUES (?, ?, ?, ?, ?)`;
        const subscriptionValues = [
          'Basic Scout Subscription',
          'Basic',
          1, // Assuming statusId 1 is "Active"
          results.insertId,
          '0.00' // Free basic plan
        ];
        
        db.execute(subscriptionQuery, subscriptionValues);
        res.json({ message: 'Scout registered successfully' });
      });

    } else if (role === 'Football Club') {
      // Insert into clubs table
      const clubQuery = `INSERT INTO clubs (name, country, location, managerName) 
                         VALUES (?, ?, ?, ?)`;
      const clubValues = [
        clubName,
        country,
        region || '', // Using region as location if available
        `${firstName} ${lastName}`
      ];

      db.execute(clubQuery, clubValues, (err, results) => {
        if (err) {
          console.error(err);
          return res.status(500).json({ message: 'Database error' });
        }
        res.json({ message: 'Football Club registered successfully' });
      });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});