# Alfred - AI Software Development Assistant

Alfred is a FastAPI-based AI assistant that orchestrates a team of AI agents to build or update software conversationally.

## Prerequisites

- Python 3.12 or higher
- Git (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/mahergzani/Alfred.git
cd Alfred
```

### 2. Set up Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the `backend` directory with your API keys:
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
# Add other environment variables as needed
```

### 5. Run the Application

**Easy way (recommended):**
```bash
# From the backend directory
# On macOS/Linux:
./start.sh

# On Windows:
start.bat
```

**Manual way:**
```bash
# From the backend directory
uvicorn main:app --reload
```

**For network access (to allow others to connect):**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- Local: http://localhost:8000
- Network: http://YOUR_IP_ADDRESS:8000

### 6. API Documentation
Once running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Sharing with Others on Your Network

To allow others on your local network to access Alfred:

1. **Start the server with network access:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Find your IP address:**
   ```bash
   # On macOS/Linux:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows:
   ipconfig
   ```

3. **Make sure your firewall allows connections on port 8000**

4. **Share your IP address with others:**
   - They can access Alfred at: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`

## Internet Access (Optional)

For access from anywhere on the internet, you have several options:

### Option 1: ngrok (Quick & Easy)
```bash
# Install ngrok (one-time setup)
# Download from: https://ngrok.com/download

# Run Alfred normally
uvicorn main:app --reload

# In another terminal, expose it to the internet
ngrok http 8000
```
This gives you a public URL like: `https://abc123.ngrok.io`

### Option 2: Cloud Deployment
Deploy to cloud platforms like:
- **Heroku**: Easy deployment with git
- **Railway**: Simple deployment platform  
- **Render**: Free tier available
- **AWS/GCP/Azure**: For production deployments

### Option 3: Router Port Forwarding
Set up port forwarding on your router (not recommended for security reasons).

## Deployment Options

For wider access, consider deploying to:
- **Heroku**: Easy deployment with git
- **Railway**: Simple deployment platform
- **Vercel/Netlify**: For static frontends
- **AWS/GCP/Azure**: For production deployments
- **Docker**: For containerized deployment

## Troubleshooting

### Common Issues:
1. **Import errors**: Make sure you're using the virtual environment and all dependencies are installed
2. **Port already in use**: Change the port in `main.py` or kill existing processes
3. **API key errors**: Ensure your `.env` file is properly configured
4. **Network access**: Check firewall settings and ensure you're using `host="0.0.0.0"`

### Getting Help:
- Check the console output for error messages
- Ensure all environment variables are set correctly
- Verify Python version compatibility (3.12+)

## Development

For development with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will automatically restart the server when you make changes to the code.