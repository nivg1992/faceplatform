FROM mcr.microsoft.com/devcontainers/python:3.12
RUN pip install poetry

RUN  wget -O /tmp/cmake.tar.gz "https://github.com/Kitware/CMake/releases/download/v3.30.0/cmake-3.30.0-linux-x86_64.tar.gz" && \
    mkdir /tmp/cmake-dir && \
    tar -zxvf /tmp/cmake.tar.gz -C /tmp/cmake-dir --strip-components=1 && \ 
    cp /tmp/cmake-dir/bin/* /usr/local/bin && \
    cp -R /tmp/cmake-dir/share/* /usr/local/share

RUN curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install 22
    
RUN npm install -g pnpm
