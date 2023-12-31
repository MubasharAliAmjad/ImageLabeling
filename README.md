# Image Labelling

## Overview

The Image Labelling project allows users to label images with relevant tags.

## Getting Started

### Prerequisites

- Python 3.x
- [Pipenv](https://pipenv.pypa.io/en/latest/) (optional, but recommended for managing virtual environments)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/image-labelling.git
   cd image-labelling

   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt

   ```

3. Apply database migrations

   ```bash
   python manage.py migrate

   ```

4. Usage
   Run the development server with following command.

   ```bash
   python manage.py runserver

   ```

In case xmlsec raise error, Run following commands for in this order (for Linux based OS)

```bash
sudo apt-get install python3-dev

sudo apt-get install pkg-config

sudo apt-get install libxmlsec1-dev

sudo apt-get install build-essential

sudo apt-get install python3-dev```