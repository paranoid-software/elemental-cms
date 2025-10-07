#!/bin/bash

# Disable shell completion for elemental-cms CLI

echo "Removing shell completion for elemental-cms..."

# Detect shell
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    echo "Detected Zsh shell"
    
    # Remove completion file
    if [ -f ~/.elemental-cms-complete.zsh ]; then
        rm ~/.elemental-cms-complete.zsh
        echo "Removed ~/.elemental-cms-complete.zsh"
    fi
    
    # Remove from .zshrc
    if [ -f ~/.zshrc ]; then
        # Create a backup
        cp ~/.zshrc ~/.zshrc.backup
        # Remove the completion lines
        sed -i.tmp '/# Elemental CMS completion/d' ~/.zshrc
        sed -i.tmp '/elemental-cms-complete\.zsh/d' ~/.zshrc
        rm ~/.zshrc.tmp
        echo "Removed completion from ~/.zshrc (backup at ~/.zshrc.backup)"
    fi
    
    echo ""
    echo "✅ Completion disabled! Run one of the following:"
    echo "   1. source ~/.zshrc"
    echo "   2. Open a new terminal"
    
elif [ "$SHELL_NAME" = "bash" ]; then
    echo "Detected Bash shell"
    
    # Remove completion file
    if [ -f ~/.elemental-cms-complete.bash ]; then
        rm ~/.elemental-cms-complete.bash
        echo "Removed ~/.elemental-cms-complete.bash"
    fi
    
    # Remove from .bashrc or .bash_profile
    BASH_RC=~/.bashrc
    [ -f ~/.bash_profile ] && BASH_RC=~/.bash_profile
    
    if [ -f "$BASH_RC" ]; then
        # Create a backup
        cp "$BASH_RC" "${BASH_RC}.backup"
        # Remove the completion lines
        sed -i.tmp '/# Elemental CMS completion/d' "$BASH_RC"
        sed -i.tmp '/elemental-cms-complete\.bash/d' "$BASH_RC"
        rm "${BASH_RC}.tmp"
        echo "Removed completion from $BASH_RC (backup at ${BASH_RC}.backup)"
    fi
    
    echo ""
    echo "✅ Completion disabled! Run one of the following:"
    echo "   1. source $BASH_RC"
    echo "   2. Open a new terminal"
    
elif [ "$SHELL_NAME" = "fish" ]; then
    echo "Detected Fish shell"
    
    # Remove completion file
    if [ -f ~/.config/fish/completions/elemental-cms.fish ]; then
        rm ~/.config/fish/completions/elemental-cms.fish
        echo "Removed ~/.config/fish/completions/elemental-cms.fish"
    fi
    
    echo ""
    echo "✅ Completion disabled!"
    echo "Fish will automatically stop using the completion."
    
else
    echo "❌ Unsupported shell: $SHELL_NAME"
    echo "Supported shells: zsh, bash, fish"
    exit 1
fi

