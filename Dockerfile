# Safe Git Push - Docker image
# 使い方 / Usage:
#   docker build -t safe-git-push .
#   docker run --rm -it -v "$PWD:/work" -w /work safe-git-push
#
# 非対話モード / Non-interactive:
#   docker run --rm -v "$PWD:/work" -w /work safe-git-push \
#     --yes --public --repo my-repo --message "Initial commit"

FROM python:3.11-slim

# git / gh (GitHub CLI) をインストール
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY linux/safe_git_push.py /app/safe_git_push.py

# colorama をあらかじめ入れておく（なければスクリプト自身が入れる）
RUN pip install --no-cache-dir colorama

# 作業ディレクトリをマウントして使う
WORKDIR /work

ENTRYPOINT ["python", "/app/safe_git_push.py"]
