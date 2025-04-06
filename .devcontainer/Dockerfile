# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:sp25

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --dev

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh

USER root

RUN apt-get update && apt-get install -y wget gnupg curl unzip

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable


ENV CHROME_DRIVER_VERSION 135.0.7049.42
RUN wget -q -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /opt/chromedriver && \
    ln -s /opt/chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

USER vscode
