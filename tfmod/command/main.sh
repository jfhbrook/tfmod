if ! cd ~/.local/state/tfmod || ! [ -d .venv ]; then
  fatal 'TfMod is not installed correctly' \
        'To install TfMod, run "tfmod update"'
fi

# rather than using uv, just use the virtualenv directly...

# shellcheck disable=SC1091
source .venv/bin/activate
exec python3 -m tfmod "${ARGV[@]}"
