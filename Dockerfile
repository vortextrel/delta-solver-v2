FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Startup script for both Web and Bot
RUN echo '#!/bin/bash\nuvicorn server:app --host 0.0.0.0 --port 10000 &\npython bot.py\nwait -n' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
