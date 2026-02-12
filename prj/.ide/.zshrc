# 0. Redirect internal Zsh files to User Home (Keep .ide/ clean)
export HISTFILE="$HOME/.zsh_history"
export ZSH_COMPDUMP="$HOME/.zcompdump"
# This covers cases where compinit is called in the global .zshrc
export _comp_dumpfile="$HOME/.zcompdump"

# 1. Load the user's default Zsh configuration
if [[ -f "$HOME/.zshrc" ]]; then
    source "$HOME/.zshrc"
fi

# 2. Load the Project-Specific Zephyr Initialization
if [[ -f "$ZDOTDIR/.zephyr-init.sh" ]]; then
    source "$ZDOTDIR/.zephyr-init.sh"
fi
