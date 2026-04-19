# GCloud Installation Guide

## macOS
```bash
# Homebrew (recommended)
brew install --cask google-cloud-sdk

# Or manual installer
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## Linux
```bash
# Debian/Ubuntu
sudo apt-get install google-cloud-cli

# Or manual installer
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## Windows
Download and run the installer from:
https://cloud.google.com/sdk/docs/install#windows

## Verify Installation
```bash
gcloud --version
gcloud auth login
gcloud config set project $PROJECT_ID
```
