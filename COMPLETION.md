# Shell Completion Setup

Elemental CMS supports tab completion for commands and snippet names.

## Quick Setup

After installing `elemental-cms` via pip, the completion scripts are included in the package.

### Method 1: Using included scripts (Recommended)

Find where the package was installed and run the enable script:

```bash
# Find the installation directory
ELEMENTAL_DIR=$(python -c "import elementalcms, os; print(os.path.dirname(elementalcms.__file__))")
cd $ELEMENTAL_DIR/..

# Run the enable script
bash enable-completion.sh
```

Or simply:

```bash
# One-liner
bash $(python -c "import elementalcms, os; print(os.path.join(os.path.dirname(os.path.dirname(elementalcms.__file__)), 'enable-completion.sh'))")
```

### Method 2: Manual setup

Alternatively, download and run the enable script:

```bash
curl -O https://raw.githubusercontent.com/paranoid-software/elemental-cms/main/enable-completion.sh
chmod +x enable-completion.sh
./enable-completion.sh
```

Then reload your shell:

```bash
source ~/.zshrc  # for Zsh
# or
source ~/.bashrc  # for Bash
```

## Manual Setup

If you prefer to set it up manually:

### Zsh

```bash
_ELEMENTAL_CMS_COMPLETE=zsh_source elemental-cms > ~/.elemental-cms-complete.zsh
echo '. ~/.elemental-cms-complete.zsh' >> ~/.zshrc
source ~/.zshrc
```

### Bash

```bash
_ELEMENTAL_CMS_COMPLETE=bash_source elemental-cms > ~/.elemental-cms-complete.bash
echo '. ~/.elemental-cms-complete.bash' >> ~/.bashrc
source ~/.bashrc
```

### Fish

```bash
_ELEMENTAL_CMS_COMPLETE=fish_source elemental-cms > ~/.config/fish/completions/elemental-cms.fish
```

## Usage

Once enabled, you can use tab completion:

```bash
elemental-cms <TAB>               # Shows available commands
elemental-cms snippets <TAB>      # Shows snippet subcommands
elemental-cms snippets diff -s <TAB>  # Shows available snippet names
```

## Disable Completion

To disable completion:

```bash
./disable-completion.sh
```

Or manually remove the completion loading from your shell config file (`~/.zshrc`, `~/.bashrc`, etc.).

## Troubleshooting

### "command not found: elemental-cms"

Make sure `elemental-cms` is installed and in your PATH:

```bash
pip install elemental-cms
# or for development
pip install -e .
```

### "command not found: compdef" (Zsh)

Make sure your `.zshrc` initializes the completion system before loading elemental-cms completion:

```bash
autoload -Uz compinit && compinit
. ~/.elemental-cms-complete.zsh
```

The `enable-completion.sh` script handles this automatically.

