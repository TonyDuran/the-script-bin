#!/bin/bash

# Usage: ./fix_git_email.sh --old wrong.email@example.com --new correct.email@example.com

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --old) OLD_EMAIL="$2"; shift ;;
        --new) NEW_EMAIL="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

if [[ -z "$OLD_EMAIL" || -z "$NEW_EMAIL" ]]; then
    echo "Usage: $0 --old wrong.email@example.com --new correct.email@example.com"
    exit 1
fi

git filter-branch --env-filter '
if [ "$GIT_COMMITTER_EMAIL" = "'"$OLD_EMAIL"'" ]; then
    export GIT_COMMITTER_EMAIL="'"$NEW_EMAIL"'"
fi
if [ "$GIT_AUTHOR_EMAIL" = "'"$OLD_EMAIL"'" ]; then
    export GIT_AUTHOR_EMAIL="'"$NEW_EMAIL"'"
fi
' --tag-name-filter cat -- --all

echo "Email change completed. Run 'git push --force --all' to update the remote repository."

