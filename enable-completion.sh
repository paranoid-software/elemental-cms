#!/bin/bash

# Enable shell completion for elemental-cms CLI
# Run this script once to set up tab completion in your shell

echo "Setting up shell completion for elemental-cms..."

# Detect shell
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    echo "Detected Zsh shell"
    
    # Generate the completion script
    echo "Generating completion script..."
    _ELEMENTAL_CMS_COMPLETE=zsh_source elemental-cms > ~/.elemental-cms-complete.zsh
    
    if [ ! -s ~/.elemental-cms-complete.zsh ]; then
        echo "❌ Failed to generate completion script."
        echo "Make sure 'elemental-cms' command is available in your PATH."
        exit 1
    fi
    
    echo "✓ Completion script generated"
    
    # Check if already configured
    if grep -q "elemental-cms-complete.zsh" ~/.zshrc; then
        echo "✓ Completion already configured in ~/.zshrc"
    else
        # Create backup
        cp ~/.zshrc ~/.zshrc.backup
        echo "✓ Created backup: ~/.zshrc.backup"
        
        # Ensure compinit is present and comes before our completion
        if ! grep -q "autoload -Uz compinit" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# Initialize zsh completion system" >> ~/.zshrc
            echo "autoload -Uz compinit && compinit" >> ~/.zshrc
            echo "✓ Added compinit initialization"
        fi
        
        # Add our completion
        echo "" >> ~/.zshrc
        echo "# Elemental CMS completion" >> ~/.zshrc
        echo ". ~/.elemental-cms-complete.zsh" >> ~/.zshrc
        echo "✓ Added completion to ~/.zshrc"
    fi
    
    echo ""
    echo "✅ Setup complete! Run one of the following:"
    echo "   1. source ~/.zshrc"
    echo "   2. Open a new terminal"
    echo ""
    echo "Then try: elemental-cms snippets diff -s <TAB>"
    
elif [ "$SHELL_NAME" = "bash" ]; then
    echo "Detected Bash shell"
    
    # Generate the completion script
    echo "Generating completion script..."
    _ELEMENTAL_CMS_COMPLETE=bash_source elemental-cms > ~/.elemental-cms-complete.bash
    
    if [ ! -s ~/.elemental-cms-complete.bash ]; then
        echo "❌ Failed to generate completion script."
        echo "Make sure 'elemental-cms' command is available in your PATH."
        exit 1
    fi
    
    echo "✓ Completion script generated"
    
    # Add to .bashrc or .bash_profile
    BASH_RC=~/.bashrc
    [ -f ~/.bash_profile ] && BASH_RC=~/.bash_profile
    
    # Check if already configured
    if grep -q "elemental-cms-complete.bash" "$BASH_RC"; then
        echo "✓ Completion already configured in $BASH_RC"
    else
        # Create backup
        cp "$BASH_RC" "${BASH_RC}.backup"
        echo "✓ Created backup: ${BASH_RC}.backup"
        
        # Add our completion
        echo "" >> "$BASH_RC"
        echo "# Elemental CMS completion" >> "$BASH_RC"
        echo ". ~/.elemental-cms-complete.bash" >> "$BASH_RC"
        echo "✓ Added completion to $BASH_RC"
    fi
    
    echo ""
    echo "✅ Setup complete! Run one of the following:"
    echo "   1. source $BASH_RC"
    echo "   2. Open a new terminal"
    echo ""
    echo "Then try: elemental-cms snippets diff -s <TAB>"
    
elif [ "$SHELL_NAME" = "fish" ]; then
    echo "Detected Fish shell"
    
    # Generate the completion script
    echo "Generating completion script..."
    mkdir -p ~/.config/fish/completions
    _ELEMENTAL_CMS_COMPLETE=fish_source elemental-cms > ~/.config/fish/completions/elemental-cms.fish
    
    if [ ! -s ~/.config/fish/completions/elemental-cms.fish ]; then
        echo "❌ Failed to generate completion script."
        echo "Make sure 'elemental-cms' command is available in your PATH."
        exit 1
    fi
    
    echo "✓ Completion script generated"
    
    echo ""
    echo "✅ Setup complete!"
    echo "Fish will automatically load the completion."
    echo ""
    echo "Try: elemental-cms snippets diff -s <TAB>"
    
else
    echo "❌ Unsupported shell: $SHELL_NAME"
    echo "Supported shells: zsh, bash, fish"
    exit 1
fi

