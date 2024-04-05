# Job Application Automation for JobsBank Canada

## Overview
This project automates the process of finding job listings on JobsBank Canada and applying to them by sending personalized cover letters and resumes via email. It consists of two main Python scripts:
1. `JobsBankCanadaAutoApply.py`: Scrapes JobsBank Canada for job listings based on specified criteria and saves the listings to a CSV file.
2. `AutoEmailApplication.py`: Reads the saved job listings and automatically sends applications to the jobs that haven't been applied to yet.

## Features
- **Job Listing Scraper**: Automatically searches for job listings on JobsBank Canada using Selenium.
- **Application Sender**: Automates the process of sending job applications via email, including a personalized cover letter and resume.

## Getting Started

### Prerequisites
Before you can run these scripts, you need to have Python installed on your machine. Additionally, you need the following packages:
- `selenium`
- `pandas`
- `webdriver_manager`
- `smtplib`, `email` (should be included in the standard Python library)

### Installation
1. Clone this repository to your local machine
2. Install the required Python packages


### Configuration
- **JobsBankCanadaAutoApply.py**: Modify the search criteria within the script to fit your job search preferences.
- **AutoEmailApplication.py**: Update `sender_address` and `sender_pass` with your email credentials. Be sure to secure your password properly.

### Usage
1. Run the `JobsBankCanadaAutoApply.py` script to scrape job listings and save them
2. Run the `AutoEmailApplication.py` script to apply to the jobs


## Contributing
Contributions are welcome! Please feel free to fork the repository, make changes, and submit pull requests. You can also open issues for bugs, feature requests, or other discussions.


## Disclaimer
This tool is for educational and research purposes only. By using it, you agree to respect JobsBank Canada's Terms of Service. It is your responsibility to ensure that your use of the tool complies with all relevant laws and terms of service.

## Acknowledgments
- Thanks to Selenium WebDriver for making web automation possible.
- Gratitude to JobsBank Canada for being a valuable resource for Canadian job seekers.
