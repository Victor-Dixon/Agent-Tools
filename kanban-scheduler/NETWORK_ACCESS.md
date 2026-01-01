# 🌐 Accessing Kanban from Another Laptop

## Quick Setup

### On Your Main Laptop (where the app is running):

1. **Make sure the app is running:**
   ```bash
   npm start
   # or
   npm run dev
   ```

2. **Allow React dev server to accept network connections:**
   
   Create or edit `client/.env` and add:
   ```
   HOST=0.0.0.0
   DANGEROUSLY_DISABLE_HOST_CHECK=true
   ```

   Or set it when starting:
   ```bash
   HOST=0.0.0.0 DANGEROUSLY_DISABLE_HOST_CHECK=true npm run client
   ```

3. **Find your IP address:**
   ```bash
   hostname -I | awk '{print $1}'
   ```
   
   You'll see something like: `10.0.0.29` or `192.168.1.100`

4. **Configure firewall (if needed):**
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 3000/tcp
   sudo ufw allow 5000/tcp
   
   # Or temporarily disable for testing
   sudo ufw disable
   ```

### On the Other Laptop:

1. **Make sure both laptops are on the same WiFi/network**

2. **Open a web browser and go to:**
   ```
   http://YOUR_IP_ADDRESS:3000
   ```
   
   For example: `http://10.0.0.29:3000`

3. **If you see a connection error, try:**
   - Make sure the main laptop's firewall isn't blocking ports 3000 and 5000
   - Verify both devices are on the same network
   - Try accessing the API directly: `http://YOUR_IP_ADDRESS:5000/health`

## Alternative: Use the API Proxy Configuration

If the client doesn't connect to the API automatically, you can configure it:

1. **Create `client/.env.local`:**
   ```
   REACT_APP_API_URL=http://YOUR_IP_ADDRESS:5000/api
   ```

2. **Restart the client:**
   ```bash
   # Stop the client (Ctrl+C) and restart
   npm run client
   ```

3. **On the other laptop, access:**
   ```
   http://YOUR_IP_ADDRESS:3000
   ```

## Current Network Settings

Your server is configured to:
- ✅ Listen on all network interfaces (`0.0.0.0`)
- ✅ Accept CORS requests from any origin (development mode)
- ✅ Allow API access from other devices

## Troubleshooting

### Can't connect from other laptop:
1. **Check if both devices are on same network:**
   ```bash
   # On main laptop
   ip addr show
   # Look for your network IP (usually starts with 192.168.x.x or 10.0.x.x)
   ```

2. **Test if ports are accessible:**
   ```bash
   # On the other laptop, try:
   curl http://YOUR_IP_ADDRESS:5000/health
   ```

3. **Check firewall:**
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   ```

### API calls fail:
- The React app might be trying to use `localhost` for API calls
- Solution: Set `REACT_APP_API_URL` in `client/.env.local` to point to your network IP

## Security Note

⚠️ **For development only!** This setup allows anyone on your local network to access the app. For production:
- Use proper authentication
- Set up HTTPS
- Restrict CORS to specific origins
- Use a reverse proxy like nginx

