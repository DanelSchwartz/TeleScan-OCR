# Telegram OCR Project

## Overview
This project automatically extracts text from images sent in Telegram chats or groups. It features multilingual OCR, keyword filtering, quality checks, and more.

## Setup
1. Install Python 3.6+.
2. Clone this repository.
3. Install dependencies: `pip install -r requirements.txt`.
4. Configure your Telegram API credentials.
5. Run `src/telegram_client.py` to start the OCR listener.

## Folder Structure and Files
- **`src/`**: Contains all the source code for the project.
  - **`__init__.py`**: An empty file indicating that the directory is a Python package.
  - **`telegram_client.py`**: Manages interactions with the Telegram API, listens for new images, and initiates the OCR process.
  - **`image_processor.py`**: Includes functions for preprocessing images to improve OCR results, such as adjusting contrast and reducing noise.
  - **`ocr_handler.py`**: Handles the core OCR functionality, including support for multiple languages and extracting text from processed images.
  - **`utilities.py`**: Provides utility functions for the project, such as exporting data to JSON and CSV formats and logging operations.
- **`data/logs/`**: Intended for storing logs and exported data files. Depending on your implementation, this could include JSON, CSV, or plain text files.
- **`requirements.txt`**: Lists all the Python dependencies required for the project, ensuring consistent setups across environments.


## Features
- **OCR Extraction**: Extracts text from images across multiple languages.
- **Image Quality Filtering**: Skips low-quality images to enhance efficiency.
- **Keyword Filtering**: Filters extracted text by user-defined keywords.
- **Data Export**: Exports data to JSON and CSV formats.
- **Image Downloading**: Downloads processed images, with exports including image paths.


## Dependencies and Licensing

#### Installation
Users are responsible for installing Tesseract OCR on their systems to use this project. We provide guidance for the installation process on various operating systems, but please refer to the official Tesseract documentation for the most up-to-date instructions.


### Tesseract OCR
This project utilizes Tesseract OCR for optical character recognition. Tesseract OCR is an open-source OCR engine freely available under the Apache License 2.0. We use Tesseract OCR without modification, relying on its powerful capabilities to extract text from images.

For more information about Tesseract OCR, including installation instructions and source code, please visit the [Tesseract OCR GitHub repository](https://github.com/tesseract-ocr/tesseract).

To view the Apache License 2.0 under which Tesseract OCR is distributed, please see the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) on the Apache Foundation's website.

We extend our gratitude to the Tesseract OCR developers and contributors for their hard work and dedication to creating and maintaining this invaluable tool.


## Contributing 
We welcome contributions! If you're interested in enhancing the Telegram OCR Project, please read our contributing guidelines and submit pull requests to our repository.