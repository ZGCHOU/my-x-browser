const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jwt-simple');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// --- Database Connection (Standard MySQL2) ---
let db;
async function connectDB() {
    try {
        db = await mysql.createPool({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'icanx_db',
            waitForConnections: true,
            connectionLimit: 10,
            queueLimit: 0
        });
        console.log('✅ Connected to MySQL Database');
    } catch (err) {
        console.error('❌ Database connection failed:', err.message);
    }
}
connectDB();

// --- Auth Middleware ---
const authenticate = (req, res, next) => {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).send({ error: 'Auth required' });
    try {
        const decoded = jwt.decode(token, process.env.JWT_SECRET || 'your_secret_key');
        req.user = decoded;
        next();
    } catch (e) {
        res.status(401).send({ error: 'Invalid token' });
    }
};

const isAdmin = (req, res, next) => {
    if (req.user.role !== 'admin') return res.status(403).send({ error: 'Admin only access' });
    next();
};

// --- API Endpoints ---

// 1. User Login
app.post('/api/auth/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        const [rows] = await db.execute('SELECT * FROM users WHERE username = ?', [username]);
        if (rows.length === 0) return res.status(401).send({ error: 'User not found' });

        const user = rows[0];
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(401).send({ error: 'Incorrect password' });

        const token = jwt.encode({ id: user.id, username: user.username, role: user.role }, process.env.JWT_SECRET || 'your_secret_key');
        res.send({ success: true, token, user: { id: user.id, username: user.username, role: user.role } });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 2. Admin: Create User
app.post('/api/admin/create-user', authenticate, isAdmin, async (req, res) => {
    const { username, password, role } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        await db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [username, hashedPassword, role || 'user']);
        res.send({ success: true, message: 'User created' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 3. User: Get Subscription Status (License Check)
app.get('/api/user/status', authenticate, async (req, res) => {
    try {
        const [rows] = await db.execute('SELECT * FROM licenses WHERE user_id = ?', [req.user.id]);
        if (rows.length === 0) return res.send({ active: false, message: 'No license found' });
        res.send({ success: true, license: rows[0] });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 Independent Account Server running on port ${PORT}`);
});
