# Ollama Setup

This application requires an Ollama server to generate synthetic member data. You have several options for connecting to Ollama:

1. **Local Machine (Default)**
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Run Ollama locally on your machine
   - The application will connect to `http://host.docker.internal:11434` by default

2. **Local Network**
   - Run Ollama on any machine in your local network
   - Create a `.env` file and set `OLLAMA_HOST=http://192.168.1.xxx:11434`
   - Replace `192.168.1.xxx` with the IP address of the machine running Ollama

3. **Remote Server**
   - Run Ollama on a remote server
   - Create a `.env` file and set `OLLAMA_HOST=http://your-server:11434`
   - Ensure proper security measures are in place (firewall, authentication, etc.)

## Getting Started

1. **Prerequisites**
   - Docker and Docker Compose
   - Ollama server (local or remote)

2. **Configuration**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file to configure your Ollama connection
   nano .env
   ```

3. **Starting the Application**
   ```bash
   # Build and start the containers
   docker compose up --build
   ```

4. **Verify Connection**
   - Open http://localhost:80 in your browser
   - Try generating some member data
   - Check the backend logs for any connection issues with Ollama