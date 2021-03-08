# Download Windows ISO

Python script to download Windows from Microsoft's website

## Requirements

1. Python

2. Docker

No other dependencies.

## How to use

```sh
wget https://raw.githubusercontent.com/ms-jpq/download-windows-iso/bindows/download.py
python3 download.py
```

It will keep trying to download image until it succeeds.

## How do you know it still works?

[Look at the CI](https://github.com/ms-jpq/download-windows-iso/actions)

If it worked the past week, the script should work.

Some timeouts are expected because Microsoft has a bot filter, and because the CI is running on a public cloud.

I will try to update it whenever it breaks.
