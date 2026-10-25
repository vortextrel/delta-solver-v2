FROM python:3.11-slim
WORKDIR /app
# Install Playwright system dependencies
RUN apt-get update && apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Install the Chromium browser for Playwright
RUN playwright install chromium

# Create a startup script to run both the web server and the bot
RUN echo '#!/bin/bash\nuvicorn server:app --host 0.0.0.0 --port 10000 &\npython bot.py\nwait -n' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
