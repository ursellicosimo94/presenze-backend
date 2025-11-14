FROM python:3.14

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    build-essential \
    zsh \
    git \
    curl \
    wget \
    vim \
    nano \
    zip \
    unzip \
    wget \
    python3-dev \
    libsqlite3-dev \
    libssl-dev \
    libffi-dev \
    poppler-utils \
    ca-certificates \
    libmupdf-dev

RUN rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements-dev.txt /tmp/requirements-dev.txt
COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting /root/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-completions /root/.oh-my-zsh/custom/plugins/zsh-completions

RUN sed -i 's/^plugins=(git)/plugins=(git z zsh-autosuggestions zsh-syntax-highlighting zsh-completions sudo docker)/' /root/.zshrc
