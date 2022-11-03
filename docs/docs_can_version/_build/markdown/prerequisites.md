# Prerequisites

The following requirements must be met in order to run the SDK.

## Python 3.8.9

Install Python 3.9


* Download the [Python installer for windows](https://www.python.org/downloads/release/python-389/).


* Add python to PATH. This allows to execute python from **Powershell**. Follow [these steps](https://datatofish.com/add-python-to-windows-path/).


* [Install pip](https://phoenixnap.com/kb/install-pip-windows).

## Virtualenv (optional)

It is suggested to isolate the execution of python scripts. To do so:


* Install virtualenv

```bash
pip install virtualenv
```


* Create a new environment and start it:

```bash
# Create the environment
python -m virtualenv myenv

# Start the environment
.\myvenv\Scripts\activate
```


* Install all the dependencies required for running the SDK:

```bash
pip install -r requirements.txt
```
