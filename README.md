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

It should work within 1 - 2 tries.

It's not 100% reliable because it uses Selenium to click on links in a headless browser.

## How do you know it still works?

[Look at the CI](https://github.com/ms-jpq/download-windows-iso/actions)

If it mostly didn't time out in the past week, the script should work.

Some timeouts are expected because Microsoft has a rate limiter.

I will try to update it whenever it breaks.
