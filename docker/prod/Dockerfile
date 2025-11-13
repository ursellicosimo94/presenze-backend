FROM python:3.14

RUN apt-get update

RUN apt-get install -y \
    build-essential \
    zsh \
    git \
    curl \
    wget \
    vim \
    nano \
    zip \
    unzip \
    wget

RUN rm -rf /var/lib/apt/lists/*

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting /root/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-completions /root/.oh-my-zsh/custom/plugins/zsh-completions

RUN sed -i 's/^plugins=(git)/plugins=(git z zsh-autosuggestions zsh-syntax-highlighting zsh-completions sudo docker)/' /root/.zshrc