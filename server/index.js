const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
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
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer <token>
    if (!token) return res.status(401).send({ error: '请先登录' });
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your_secret_key');
        req.user = decoded;
        next();
    } catch (e) {
        res.status(401).send({ error: '登录已过期，请重新登录' });
    }
};

const isAdmin = (req, res, next) => {
    if (req.user.role !== 'admin') return res.status(403).send({ error: '需要管理员权限' });
    next();
};

// 检查子账号访问期限的中间件
const checkSubscription = async (req, res, next) => {
    // 超级管理员跳过检查
    if (req.user.role === 'admin') {
        return next();
    }

    try {
        const [rows] = await db.execute(
            'SELECT expire_at, max_profiles FROM licenses WHERE user_id = ?',
            [req.user.id]
        );

        if (rows.length === 0) {
            return res.status(403).send({ error: '未找到访问授权', code: 'NO_LICENSE' });
        }

        const license = rows[0];
        const now = new Date();
        const expireAt = new Date(license.expire_at);

        // 检查是否过期
        if (expireAt < now) {
            return res.status(403).send({ error: '访问权限已过期', code: 'LICENSE_EXPIRED', expire_at: license.expire_at });
        }

        // 将license信息附加到请求对象
        req.license = license;
        next();
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
};

// --- Helper Functions ---

// 记录审计日志
const logAudit = async (userId, action, ipAddress) => {
    try {
        await db.execute(
            'INSERT INTO audit_logs (user_id, action, ip_address) VALUES (?, ?, ?)',
            [userId, action, ipAddress]
        );
    } catch (e) {
        console.error('Audit log error:', e.message);
    }
};

// --- API Endpoints ---

// 1. User Login
app.post('/api/auth/login', async (req, res) => {
    const { username, password } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        const [rows] = await db.execute('SELECT * FROM users WHERE username = ?', [username]);
        if (rows.length === 0) {
            await logAudit(null, `登录失败：用户不存在 (${username})`, clientIp);
            return res.status(401).send({ error: '用户不存在' });
        }

        const user = rows[0];
        
        // 检查账号状态
        if (user.status === 'disabled') {
            await logAudit(user.id, '登录失败：账号已被禁用', clientIp);
            return res.status(403).send({ error: '账号已被禁用', code: 'ACCOUNT_DISABLED' });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            await logAudit(user.id, '登录失败：密码错误', clientIp);
            return res.status(401).send({ error: '密码错误' });
        }

        // 如果是子账号，检查访问期限
        if (user.role === 'user') {
            const [licenseRows] = await db.execute('SELECT expire_at FROM licenses WHERE user_id = ?', [user.id]);
            if (licenseRows.length > 0) {
                const expireAt = new Date(licenseRows[0].expire_at);
                if (expireAt < new Date()) {
                    await logAudit(user.id, '登录失败：访问权限已过期', clientIp);
                    return res.status(403).send({ error: '访问权限已过期', code: 'LICENSE_EXPIRED', expire_at: licenseRows[0].expire_at });
                }
            }
        }

        const token = jwt.sign(
            { id: user.id, username: user.username, role: user.role },
            process.env.JWT_SECRET || 'your_secret_key',
            { expiresIn: '24h' }
        );

        await logAudit(user.id, '登录成功', clientIp);

        res.send({
            success: true,
            token,
            user: {
                id: user.id,
                username: user.username,
                role: user.role,
                status: user.status
            }
        });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 2. Admin: Create User (with license)
app.post('/api/admin/users', authenticate, isAdmin, async (req, res) => {
    const { username, password, role, expire_at, max_profiles, balance } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 检查用户名是否已存在
        const [existing] = await db.execute('SELECT id FROM users WHERE username = ?', [username]);
        if (existing.length > 0) {
            return res.status(400).send({ error: 'Username already exists' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        
        // 开启事务
        const connection = await db.getConnection();
        await connection.beginTransaction();

        try {
            // 创建用户
            const [userResult] = await connection.execute(
                'INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)',
                [username, hashedPassword, role || 'user', 'active']
            );
            const userId = userResult.insertId;

            // 创建license（仅对子账号）
            if (role === 'user' || !role) {
                const defaultExpireAt = expire_at || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 默认30天
                await connection.execute(
                    'INSERT INTO licenses (user_id, expire_at, max_profiles, balance) VALUES (?, ?, ?, ?)',
                    [userId, defaultExpireAt, max_profiles || 5, balance || 0.00]
                );
            }

            await connection.commit();
            await logAudit(req.user.id, `创建用户：${username}`, clientIp);

            res.send({ success: true, message: 'User created', userId });
        } catch (err) {
            await connection.rollback();
            throw err;
        } finally {
            connection.release();
        }
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 3. Admin: Get All Users
app.get('/api/admin/users', authenticate, isAdmin, async (req, res) => {
    try {
        const [rows] = await db.execute(`
            SELECT u.id, u.username, u.role, u.status, u.created_at, 
                   l.expire_at, l.max_profiles, l.balance 
            FROM users u
            LEFT JOIN licenses l ON u.id = l.user_id
            ORDER BY u.id DESC
        `);
        
        // 获取每个用户的标签
        const [userTags] = await db.execute(`
            SELECT ut.user_id, t.id, t.name, t.color
            FROM user_tags ut
            JOIN tags t ON ut.tag_id = t.id
        `);
        
        // 将标签关联到用户
        const usersWithTags = rows.map(user => ({
            ...user,
            tags: userTags.filter(ut => ut.user_id === user.id).map(ut => ({
                id: ut.id,
                name: ut.name,
                color: ut.color
            }))
        }));
        
        res.send({ success: true, users: usersWithTags });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 4. Admin: Get Single User
app.get('/api/admin/users/:id', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    try {
        const [rows] = await db.execute(`
            SELECT u.id, u.username, u.role, u.status, u.created_at, 
                   l.expire_at, l.max_profiles, l.balance 
            FROM users u
            LEFT JOIN licenses l ON u.id = l.user_id
            WHERE u.id = ?
        `, [id]);
        
        if (rows.length === 0) {
            return res.status(404).send({ error: 'User not found' });
        }
        
        // 获取用户标签
        const [userTags] = await db.execute(`
            SELECT t.id, t.name, t.color
            FROM user_tags ut
            JOIN tags t ON ut.tag_id = t.id
            WHERE ut.user_id = ?
        `, [id]);
        
        res.send({ 
            success: true, 
            user: {
                ...rows[0],
                tags: userTags
            }
        });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 5. Admin: Update User
app.put('/api/admin/users/:id', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const { username, password, role, status, expire_at, max_profiles, balance, tags } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 不能修改超级管理员（id=1）的角色和状态
        if (id === '1') {
            if (role && role !== 'admin') {
                return res.status(403).send({ error: 'Cannot change super admin role' });
            }
            if (status && status !== 'active') {
                return res.status(403).send({ error: 'Cannot disable super admin' });
            }
        }

        const connection = await db.getConnection();
        await connection.beginTransaction();

        try {
            // 构建用户更新字段
            const userUpdates = [];
            const userValues = [];
            
            if (username) {
                // 检查新用户名是否已存在
                const [existing] = await connection.execute(
                    'SELECT id FROM users WHERE username = ? AND id != ?',
                    [username, id]
                );
                if (existing.length > 0) {
                    connection.release();
                    return res.status(400).send({ error: 'Username already exists' });
                }
                userUpdates.push('username = ?');
                userValues.push(username);
            }
            
            if (password) {
                const hashedPassword = await bcrypt.hash(password, 10);
                userUpdates.push('password = ?');
                userValues.push(hashedPassword);
            }
            
            if (role) {
                userUpdates.push('role = ?');
                userValues.push(role);
            }
            
            if (status) {
                userUpdates.push('status = ?');
                userValues.push(status);
            }

            // 更新用户表
            if (userUpdates.length > 0) {
                userValues.push(id);
                await connection.execute(
                    `UPDATE users SET ${userUpdates.join(', ')} WHERE id = ?`,
                    userValues
                );
            }

            // 更新license表
            const licenseUpdates = [];
            const licenseValues = [];
            
            if (expire_at !== undefined) {
                licenseUpdates.push('expire_at = ?');
                licenseValues.push(expire_at);
            }
            
            if (max_profiles !== undefined) {
                licenseUpdates.push('max_profiles = ?');
                licenseValues.push(max_profiles);
            }
            
            if (balance !== undefined) {
                licenseUpdates.push('balance = ?');
                licenseValues.push(balance);
            }

            if (licenseUpdates.length > 0) {
                // 检查是否已有license记录
                const [existingLicense] = await connection.execute(
                    'SELECT id FROM licenses WHERE user_id = ?',
                    [id]
                );

                if (existingLicense.length > 0) {
                    licenseValues.push(id);
                    await connection.execute(
                        `UPDATE licenses SET ${licenseUpdates.join(', ')} WHERE user_id = ?`,
                        licenseValues
                    );
                } else {
                    // 创建新的license记录
                    await connection.execute(
                        'INSERT INTO licenses (user_id, expire_at, max_profiles, balance) VALUES (?, ?, ?, ?)',
                        [id, expire_at || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), max_profiles || 5, balance || 0.00]
                    );
                }
            }

            // 更新用户标签
            if (tags !== undefined && Array.isArray(tags)) {
                // 删除原有标签关联
                await connection.execute('DELETE FROM user_tags WHERE user_id = ?', [id]);
                
                // 添加新的标签关联
                for (const tagId of tags) {
                    await connection.execute(
                        'INSERT INTO user_tags (user_id, tag_id) VALUES (?, ?)',
                        [id, tagId]
                    );
                }
            }

            await connection.commit();
            await logAudit(req.user.id, `更新用户 ID：${id}`, clientIp);

            res.send({ success: true, message: 'User updated' });
        } catch (err) {
            await connection.rollback();
            throw err;
        } finally {
            connection.release();
        }
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 6. Admin: Delete User
app.delete('/api/admin/users/:id', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 不能删除超级管理员
        if (id === '1') {
            return res.status(403).send({ error: 'Cannot delete super admin' });
        }

        // 不能删除自己
        if (parseInt(id) === req.user.id) {
            return res.status(403).send({ error: 'Cannot delete yourself' });
        }

        const [result] = await db.execute('DELETE FROM users WHERE id = ?', [id]);
        
        if (result.affectedRows === 0) {
            return res.status(404).send({ error: 'User not found' });
        }

        await logAudit(req.user.id, `删除用户 ID：${id}`, clientIp);
        res.send({ success: true, message: 'User deleted' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 7. Admin: Update User License Only
app.put('/api/admin/users/:id/license', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const { expire_at, max_profiles, balance } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 检查用户是否存在
        const [userRows] = await db.execute('SELECT id, role FROM users WHERE id = ?', [id]);
        if (userRows.length === 0) {
            return res.status(404).send({ error: 'User not found' });
        }

        // 超级管理员不需要license
        if (userRows[0].role === 'admin') {
            return res.status(400).send({ error: 'Admin users do not need license' });
        }

        const updates = [];
        const values = [];
        
        if (expire_at !== undefined) {
            updates.push('expire_at = ?');
            values.push(expire_at);
        }
        
        if (max_profiles !== undefined) {
            updates.push('max_profiles = ?');
            values.push(max_profiles);
        }
        
        if (balance !== undefined) {
            updates.push('balance = ?');
            values.push(balance);
        }

        if (updates.length === 0) {
            return res.status(400).send({ error: 'No fields to update' });
        }

        // 检查是否已有license记录
        const [existingLicense] = await db.execute(
            'SELECT id FROM licenses WHERE user_id = ?',
            [id]
        );

        if (existingLicense.length > 0) {
            values.push(id);
            await db.execute(
                `UPDATE licenses SET ${updates.join(', ')} WHERE user_id = ?`,
                values
            );
        } else {
            // 创建新的license记录
            await db.execute(
                'INSERT INTO licenses (user_id, expire_at, max_profiles, balance) VALUES (?, ?, ?, ?)',
                [id, expire_at || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), max_profiles || 5, balance || 0.00]
            );
        }

        await logAudit(req.user.id, `更新授权 ID：${id}`, clientIp);
        res.send({ success: true, message: 'License updated' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 8. User: Get Subscription Status (License Check)
app.get('/api/user/status', authenticate, async (req, res) => {
    try {
        // 超级管理员跳过license检查
        if (req.user.role === 'admin') {
            return res.send({
                success: true,
                active: true,
                role: 'admin',
                is_admin: true
            });
        }

        const [rows] = await db.execute(
            'SELECT * FROM licenses WHERE user_id = ?',
            [req.user.id]
        );

        if (rows.length === 0) {
            return res.send({
                success: true,
                active: false,
                message: 'No license found',
                code: 'NO_LICENSE'
            });
        }

        const license = rows[0];
        const now = new Date();
        const expireAt = new Date(license.expire_at);
        const isExpired = expireAt < now;

        res.send({
            success: true,
            active: !isExpired,
            is_expired: isExpired,
            license: {
                expire_at: license.expire_at,
                max_profiles: license.max_profiles,
                balance: license.balance,
                days_remaining: isExpired ? 0 : Math.ceil((expireAt - now) / (1000 * 60 * 60 * 24))
            }
        });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 9. User: Change Own Password
app.put('/api/user/password', authenticate, async (req, res) => {
    const { old_password, new_password } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        const [rows] = await db.execute('SELECT password FROM users WHERE id = ?', [req.user.id]);
        if (rows.length === 0) {
            return res.status(404).send({ error: 'User not found' });
        }

        const isMatch = await bcrypt.compare(old_password, rows[0].password);
        if (!isMatch) {
            return res.status(401).send({ error: 'Old password is incorrect' });
        }

        const hashedPassword = await bcrypt.hash(new_password, 10);
        await db.execute('UPDATE users SET password = ? WHERE id = ?', [hashedPassword, req.user.id]);

        await logAudit(req.user.id, '修改密码', clientIp);
        res.send({ success: true, message: 'Password updated' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 10. Admin: Get Audit Logs
app.get('/api/admin/audit-logs', authenticate, isAdmin, async (req, res) => {
    const { page = 1, limit = 50, user_id } = req.query;
    const offset = (parseInt(page) - 1) * parseInt(limit);
    const limitNum = parseInt(limit);
    
    try {
        let query = `
            SELECT al.*, u.username 
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
        `;
        let countQuery = 'SELECT COUNT(*) as total FROM audit_logs';
        const params = [];

        if (user_id) {
            query += ' WHERE al.user_id = ?';
            countQuery += ' WHERE user_id = ?';
            params.push(parseInt(user_id));
        }

        query += ` ORDER BY al.created_at DESC LIMIT ${limitNum} OFFSET ${offset}`;

        const [rows] = await db.execute(query, params);
        const [countResult] = await db.execute(countQuery, user_id ? [parseInt(user_id)] : []);

        res.send({
            success: true,
            logs: rows,
            pagination: {
                page: parseInt(page),
                limit: limitNum,
                total: countResult[0].total
            }
        });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 11. Admin: Get Dashboard Stats
app.get('/api/admin/stats', authenticate, isAdmin, async (req, res) => {
    try {
        // 用户统计
        const [userStats] = await db.execute(`
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_count,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN status = 'disabled' THEN 1 ELSE 0 END) as disabled_count
            FROM users
        `);

        // 即将过期的用户（7天内）
        const [expiringSoon] = await db.execute(`
            SELECT COUNT(*) as count 
            FROM licenses 
            WHERE expire_at BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
        `);

        // 已过期用户
        const [expired] = await db.execute(`
            SELECT COUNT(*) as count 
            FROM licenses 
            WHERE expire_at < NOW()
        `);

        // 今日登录次数
        const [todayLogins] = await db.execute(`
            SELECT COUNT(*) as count 
            FROM audit_logs 
            WHERE action = 'Successful login' 
            AND DATE(created_at) = CURDATE()
        `);

        res.send({
            success: true,
            stats: {
                ...userStats[0],
                expiring_soon: expiringSoon[0].count,
                expired: expired[0].count,
                today_logins: todayLogins[0].count
            }
        });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// --- Tags Management APIs ---

// 12. Admin: Get All Tags
app.get('/api/admin/tags', authenticate, isAdmin, async (req, res) => {
    try {
        const [rows] = await db.execute('SELECT * FROM tags ORDER BY created_at DESC');
        res.send({ success: true, tags: rows });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 13. Admin: Create Tag
app.post('/api/admin/tags', authenticate, isAdmin, async (req, res) => {
    const { name, color } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 检查标签名是否已存在
        const [existing] = await db.execute('SELECT id FROM tags WHERE name = ?', [name]);
        if (existing.length > 0) {
            return res.status(400).send({ error: 'Tag name already exists' });
        }

        const [result] = await db.execute(
            'INSERT INTO tags (name, color) VALUES (?, ?)',
            [name, color || '#6366f1']
        );

        await logAudit(req.user.id, `创建标签：${name}`, clientIp);
        res.send({ success: true, message: 'Tag created', tagId: result.insertId });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 14. Admin: Update Tag
app.put('/api/admin/tags/:id', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const { name, color } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        const updates = [];
        const values = [];
        
        if (name) {
            // 检查新名称是否已存在
            const [existing] = await db.execute(
                'SELECT id FROM tags WHERE name = ? AND id != ?',
                [name, id]
            );
            if (existing.length > 0) {
                return res.status(400).send({ error: 'Tag name already exists' });
            }
            updates.push('name = ?');
            values.push(name);
        }
        
        if (color) {
            updates.push('color = ?');
            values.push(color);
        }

        if (updates.length === 0) {
            return res.status(400).send({ error: 'No fields to update' });
        }

        values.push(id);
        await db.execute(
            `UPDATE tags SET ${updates.join(', ')} WHERE id = ?`,
            values
        );

        await logAudit(req.user.id, `更新标签 ID：${id}`, clientIp);
        res.send({ success: true, message: 'Tag updated' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 15. Admin: Delete Tag
app.delete('/api/admin/tags/:id', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 删除标签（关联表会自动级联删除）
        const [result] = await db.execute('DELETE FROM tags WHERE id = ?', [id]);
        
        if (result.affectedRows === 0) {
            return res.status(404).send({ error: 'Tag not found' });
        }

        await logAudit(req.user.id, `删除标签 ID：${id}`, clientIp);
        res.send({ success: true, message: 'Tag deleted' });
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

// 16. Admin: Update User Tags Only
app.put('/api/admin/users/:id/tags', authenticate, isAdmin, async (req, res) => {
    const { id } = req.params;
    const { tags } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    
    try {
        // 检查用户是否存在
        const [userRows] = await db.execute('SELECT id FROM users WHERE id = ?', [id]);
        if (userRows.length === 0) {
            return res.status(404).send({ error: 'User not found' });
        }

        const connection = await db.getConnection();
        await connection.beginTransaction();

        try {
            // 删除原有标签关联
            await connection.execute('DELETE FROM user_tags WHERE user_id = ?', [id]);
            
            // 添加新的标签关联
            if (tags && Array.isArray(tags) && tags.length > 0) {
                for (const tagId of tags) {
                    await connection.execute(
                        'INSERT INTO user_tags (user_id, tag_id) VALUES (?, ?)',
                        [id, tagId]
                    );
                }
            }

            await connection.commit();
            await logAudit(req.user.id, `更新用户标签 ID：${id}`, clientIp);
            res.send({ success: true, message: 'User tags updated' });
        } catch (err) {
            await connection.rollback();
            throw err;
        } finally {
            connection.release();
        }
    } catch (e) {
        res.status(500).send({ error: e.message });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`🚀 Independent Account Server running on port ${PORT}`);
});

module.exports = { app, authenticate, checkSubscription };
