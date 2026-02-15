#!/bin/bash

set -e

echo "====== Dual GitHub Account Setup (HTTPS Clean Method) ======"

git config --global credential.helper store

read -p "Enter First GitHub Username: " USER1
read -p "Enter First GitHub Email: " EMAIL1
read -p "Enter Folder Path for First Account (example: ~/github-work): " DIR1

read -p "Enter Second GitHub Username: " USER2
read -p "Enter Second GitHub Email: " EMAIL2
read -p "Enter Folder Path for Second Account (example: ~/github-personal): " DIR2

DIR1=$(eval echo $DIR1)
DIR2=$(eval echo $DIR2)

mkdir -p "$DIR1"
mkdir -p "$DIR2"

# Create account-specific gitconfig files
CONFIG1="$HOME/.gitconfig-$USER1"
CONFIG2="$HOME/.gitconfig-$USER2"

cat > "$CONFIG1" <<EOF
[user]
    name = $USER1
    email = $EMAIL1
EOF

cat > "$CONFIG2" <<EOF
[user]
    name = $USER2
    email = $EMAIL2
EOF

# Add conditional include to global config
git config --global includeIf."gitdir:$DIR1/".path "$CONFIG1"
git config --global includeIf."gitdir:$DIR2/".path "$CONFIG2"

echo ""
echo "Setup Complete!"
echo ""
echo "Now:"
echo "Place first account projects inside:"
echo "  $DIR1"
echo ""
echo "Place second account projects inside:"
echo "  $DIR2"
echo ""
echo "Git will automatically use correct identity."
echo ""
echo "When pushing first time, Git will ask for PAT."
echo "Use correct username + its Personal Access Token."
