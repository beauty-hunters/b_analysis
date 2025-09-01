#!/usr/bin/env python3
"""
FONLL Web Form Automation - Parallelized Version

A Python script to automatically fill out and submit FONLL prediction forms
using Selenium WebDriver based on YAML configuration files, with support for
parallel processing of multiple predictions.
"""

import yaml
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import multiprocessing as mp
from dataclasses import dataclass

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Selenium not found. Install with: pip install selenium")
    print("Also make sure to install ChromeDriver: https://chromedriver.chromium.org/")
    sys.exit(1)

# Configure logging with thread safety
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)-10s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fonll_automation.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of processing a single prediction"""
    prediction_name: str
    success: bool
    error_message: Optional[str] = None
    downloaded_files: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.downloaded_files is None:
            self.downloaded_files = []


class FONLLWorker:
    """Worker class for processing individual predictions with independent WebDriver instances."""
    
    def __init__(self, config: Dict[str, Any], worker_id: int):
        """Initialize worker with configuration and unique ID."""
        self.config = config
        self.worker_id = worker_id
        self.driver = None
        self.logger = logging.getLogger(f"Worker-{worker_id}")
        
    def setup_driver(self):
        """Setup Chrome WebDriver with proper download configuration for this worker."""
        chrome_options = Options()
        
        # Add worker-specific options
        if self.config.get('browser_options', {}).get('headless', True):  # Default to headless for parallel
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Worker-specific user data directory to avoid conflicts
        chrome_options.add_argument(f'--user-data-dir=/tmp/chrome_worker_{self.worker_id}')
        
        # Set up proper download preferences with worker-specific directory
        output_dir = Path(self.config['output_dir']) / f"worker_{self.worker_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        prefs = {
            "download.default_directory": str(output_dir.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_settings.popups": 0,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "download.open_pdf_externally": False,
            "plugins.always_open_pdf_externally": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Additional arguments for better performance in parallel
        chrome_options.add_argument('--disable-features=DownloadBubble')
        chrome_options.add_argument('--disable-features=DownloadBubbleV2')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        
        try:
            # Try webdriver-manager first, with fallback
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                self.driver = webdriver.Chrome(options=chrome_options)
                
        except Exception as e:
            self.logger.error(f"WebDriver init failed for worker {self.worker_id}: {e}")
            raise
        
        # Set timeouts
        self.driver.set_page_load_timeout(300)
        if hasattr(self.driver, 'command_executor'):
            self.driver.command_executor.set_timeout(300)
        
        self.logger.info(f"WebDriver initialized for worker {self.worker_id}")
    
    def fill_form_field(self, field_config: Dict[str, Any]) -> bool:
        """Fill a single form field based on configuration."""
        try:
            field_type = field_config['type']
            selector = field_config['selector']
            value = field_config['value']
            
            # Wait for element to be present
            wait = WebDriverWait(self.driver, self.config.get('wait_timeout', 10))
            
            if field_type == 'input':
                element = wait.until(EC.presence_of_element_located((By.NAME, selector)))
                element.clear()
                element.send_keys(str(value))
                
            elif field_type == 'select':
                element = wait.until(EC.presence_of_element_located((By.NAME, selector)))
                select = Select(element)
                
                # Try different selection methods
                try:
                    select.select_by_value(str(value))
                except:
                    try:
                        select.select_by_visible_text(str(value))
                    except:
                        select.select_by_index(int(value))
                        
            elif field_type == 'radio':
                # Find radio button by value
                element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'input[name="{selector}"][value="{value}"]')
                ))
                element.click()
                
            elif field_type == 'checkbox':
                element = wait.until(EC.presence_of_element_located((By.NAME, selector)))
                if (value and not element.is_selected()) or (not value and element.is_selected()):
                    element.click()
            
            self.logger.debug(f"Successfully filled field {selector} with value {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fill field {field_config}: {e}")
            return False

    def trigger_all_downloads(self):
        """Find and trigger all possible download mechanisms"""
        download_strategies = [
            self.trigger_file_links,
            self.trigger_download_buttons,
            self.trigger_javascript_links,
            self.trigger_form_downloads,
        ]
        
        download_triggered = False
        
        for strategy in download_strategies:
            try:
                if strategy():
                    download_triggered = True
                    time.sleep(1)  # Brief pause between strategies
            except Exception as e:
                self.logger.debug(f"Download strategy {strategy.__name__} failed: {e}")
        
        return download_triggered

    def trigger_file_links(self):
        """Trigger direct file download links"""
        file_extensions = ['.dat', '.txt', '.csv', '.out', '.pdf', '.zip']
        download_found = False
        
        for ext in file_extensions:
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, f'a[href*="{ext}"]')
                for link in links:
                    if self.safe_click_element(link, f"file link ({ext})"):
                        download_found = True
            except Exception as e:
                self.logger.debug(f"No {ext} links found: {e}")
        
        return download_found

    def trigger_download_buttons(self):
        """Trigger download buttons"""
        button_selectors = [
            'input[value*="Download"]',
            'input[value*="download"]',
            'input[value*="Save"]',
            'input[value*="save"]',
            'button:contains("Download")',
            'button:contains("download")',
            'button:contains("Save")',
            'button:contains("save")',
        ]
        
        download_found = False
        
        for selector in button_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if self.safe_click_element(button, "download button"):
                        download_found = True
            except Exception as e:
                self.logger.debug(f"No buttons found with {selector}: {e}")
        
        return download_found

    def trigger_javascript_links(self):
        """Trigger JavaScript-based downloads"""
        js_patterns = [
            'a[onclick*="download"]',
            'a[onclick*="save"]',
            'a[onclick*="export"]',
            'button[onclick*="download"]',
            'button[onclick*="save"]',
            'button[onclick*="export"]',
        ]
        
        download_found = False
        
        for pattern in js_patterns:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                for element in elements:
                    if self.safe_click_element(element, "JavaScript download"):
                        download_found = True
            except Exception as e:
                self.logger.debug(f"No JS elements found with {pattern}: {e}")
        
        return download_found

    def trigger_form_downloads(self):
        """Handle form-based downloads"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            for form in forms:
                form_action = form.get_attribute('action') or ''
                
                if any(ext in form_action for ext in ['.dat', '.txt', '.csv', 'download']):
                    self.logger.info(f"Found potential download form: {form_action}")
                    
                    try:
                        form.submit()
                        return True
                    except Exception as e:
                        self.logger.warning(f"Failed to submit form: {e}")
                        
        except Exception as e:
            self.logger.debug(f"Form download search failed: {e}")
        
        return False

    def safe_click_element(self, element, element_type="element"):
        """Safely click an element with proper error handling"""
        try:
            if not element.is_displayed() or not element.is_enabled():
                return False
            
            text = element.text or element.get_attribute('value') or element.get_attribute('innerHTML')[:50]
            href = element.get_attribute('href') or element.get_attribute('onclick') or 'no-href'
            
            self.logger.info(f"Clicking {element_type}: {text} -> {href[:100]}...")
            
            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.05)
            
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to click {element_type}: {e}")
            return False

    def wait_for_downloads_completion(self, timeout=60):
        """Wait for all downloads to complete"""
        self.logger.info("Waiting for downloads to complete...")
        
        output_dir = Path(self.config['output_dir']) / f"worker_{self.worker_id}"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for temporary download files
            temp_files = list(output_dir.glob("*.crdownload")) + list(output_dir.glob("*.part"))
            
            if not temp_files:
                self.logger.info("Downloads completed")
                return True
            
            self.logger.debug(f"Downloads in progress: {len(temp_files)} files")
            time.sleep(2)
        
        self.logger.warning("Download timeout reached")
        return False

    def rename_downloaded_files(self, prediction_name: str, initial_files: set):
        """Rename downloaded files to include prediction name"""
        output_dir = Path(self.config['output_dir']) / f"worker_{self.worker_id}"
        current_files = set(output_dir.iterdir())
        new_files = current_files - initial_files
        
        # Filter out temporary files
        completed_files = [f for f in new_files if not any(f.name.endswith(ext) for ext in ['.crdownload', '.part', '.tmp'])]
        
        renamed_files = []
        for file_path in completed_files:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{prediction_name}_{timestamp}{file_path.suffix}"
                
                # Move to main output directory
                main_output_dir = Path(self.config['output_dir'])
                main_output_dir.mkdir(parents=True, exist_ok=True)
                new_path = main_output_dir / new_name
                
                file_path.rename(new_path)
                renamed_files.append(str(new_path))
                self.logger.info(f"Renamed and moved {file_path.name} -> {new_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to rename {file_path.name}: {e}")
        
        return renamed_files

    def save_page_source(self, prediction_name: str, error: bool = False):
        """Save page source for debugging"""
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "error" if error else "results"
        filename = output_dir / f"{prediction_name}_{status}_{timestamp}_worker{self.worker_id}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.info(f"Page saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save page: {e}")

    def submit_form_and_download(self, prediction_name: str) -> Tuple[bool, List[str]]:
        """Submit the FONLL form, wait for results, and download output files."""
        try:
            output_dir = Path(self.config['output_dir']) / f"worker_{self.worker_id}"
            initial_files = set(output_dir.iterdir())

            # Submit the form
            submit_button = WebDriverWait(self.driver, self.config['wait_timeout']).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
            )
            submit_button.click()
            self.logger.info(f"Form submitted for: {prediction_name}")

            # Wait for results
            self.logger.info("Waiting for results to appear...")
            result_indicators = [
                (By.TAG_NAME, "pre"),
                (By.TAG_NAME, "code"),
                (By.CSS_SELECTOR, "a[href*='.dat']"),
                (By.CSS_SELECTOR, "a[href*='.txt']"),
                (By.XPATH, "//*[contains(text(), 'Results')]"),
            ]

            results_found = False
            for by, selector in result_indicators:
                try:
                    WebDriverWait(self.driver, self.config.get('download_wait_time', 60)).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self.logger.info(f"Results detected using: {selector}")
                    results_found = True
                    break
                except TimeoutException:
                    continue

            if not results_found:
                self.logger.warning("No explicit results detected — proceeding with download attempt anyway")

            # Attempt to trigger downloads
            self.logger.info("Attempting to trigger downloads...")
            download_attempted = self.trigger_all_downloads()

            downloaded_files = []
            if download_attempted:
                self.wait_for_downloads_completion(self.config.get('download_wait_time', 60))
                downloaded_files = self.rename_downloaded_files(prediction_name, initial_files)

            # Save page source for debugging
            self.save_page_source(prediction_name, error=not download_attempted)
            return download_attempted, downloaded_files

        except Exception as e:
            self.logger.error(f"Error in automated process: {e}")
            self.save_page_source(prediction_name, error=True)
            return False, []

    def process_prediction(self, prediction_config: Dict[str, Any]) -> ProcessingResult:
        """Process a single prediction configuration."""
        prediction_name = prediction_config.get('name', 'unknown')
        start_time = time.time()
        
        try:
            self.setup_driver()
            self.logger.info(f"Processing prediction: {prediction_name}")
            
            # Navigate to FONLL form
            self.driver.get(self.config['fonll_url'])
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, self.config.get('wait_timeout', 10))
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
            
            # Fill form fields
            fields = prediction_config.get('fields', [])
            success_count = 0
            
            for field_config in fields:
                if self.fill_form_field(field_config):
                    success_count += 1
                time.sleep(0.01)  # Small delay between fields
                
            # Handle email if provided
            email = self.config.get('email', None)
            if email:
                self.logger.info(f"Filling email field with: {email}")
                try:
                    # Tick the checkbox to enable email results
                    checkbox = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[name="email"][value="1"]')
                    ))
                    if not checkbox.is_selected():
                        checkbox.click()

                    # Fill in the email address
                    email_field = wait.until(EC.presence_of_element_located((By.NAME, 'emailaddress')))
                    email_field.clear()
                    email_field.send_keys(email)
                except Exception as e:
                    self.logger.warning(f"Failed to fill email: {e}")
              
            self.logger.info(f"Successfully filled {success_count}/{len(fields)} fields")
            
            # Submit form and handle download
            if success_count > 0:
                success, downloaded_files = self.submit_form_and_download(prediction_name)
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    prediction_name=prediction_name,
                    success=success,
                    downloaded_files=downloaded_files,
                    processing_time=processing_time
                )
            else:
                error_msg = f"No fields were successfully filled for {prediction_name}"
                self.logger.error(error_msg)
                return ProcessingResult(
                    prediction_name=prediction_name,
                    success=False,
                    error_message=error_msg,
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            error_msg = f"Error processing prediction {prediction_name}: {e}"
            self.logger.error(error_msg)
            return ProcessingResult(
                prediction_name=prediction_name,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources for this worker."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info(f"WebDriver closed successfully for worker {self.worker_id}")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver for worker {self.worker_id}: {e}")


class ParallelFONLLAutomation:
    """Main class for parallel FONLL automation."""
    
    def __init__(self, config_path: str):
        """Initialize automation with configuration file."""
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate YAML configuration file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            return self.validate_config(config)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            sys.exit(1)
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration structure."""
        required_fields = ['fonll_url', 'output_dir', 'predictions']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")
        
        # Set default values
        config.setdefault('browser_options', {})
        config.setdefault('wait_timeout', 10)
        config.setdefault('delay_between_predictions', 2)
        config.setdefault('download_wait_time', 30)
        config.setdefault('max_workers', min(4, len(config.get('predictions', []))))  # Default to 4 or number of predictions
        config.setdefault('chunk_size', 1)  # Process predictions one at a time per worker
        
        return config
    
    def run_predictions_parallel(self) -> Dict[str, Any]:
        """Process predictions in parallel using ThreadPoolExecutor."""
        predictions = self.config.get('predictions', [])
        max_workers = min(self.config.get('max_workers', 4), len(predictions))
        
        logger.info(f"Starting parallel processing of {len(predictions)} predictions with {max_workers} workers")
        
        results = []
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="FONLL") as executor:
            # Submit all predictions to the executor
            future_to_prediction = {}
            
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="FONLL") as executor:
            future_to_prediction = {
                executor.submit(FONLLWorker(self.config, worker_id=i).process_prediction, prediction_config):
                prediction_config.get('name', f'prediction_{i}')
                for i, prediction_config in enumerate(predictions)
            }

            for future in as_completed(future_to_prediction):
                prediction_name = future_to_prediction[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        logger.info(f"✅ {prediction_name} completed successfully in {result.processing_time:.1f}s")
                        if result.downloaded_files:
                            logger.info(f"   Downloaded: {', '.join(result.downloaded_files)}")
                    else:
                        logger.error(f"❌ {prediction_name} failed: {result.error_message}")
                        
                except Exception as e:
                    logger.error(f"❌ {prediction_name} failed with exception: {e}")
                    results.append(ProcessingResult(
                        prediction_name=prediction_name,
                        success=False,
                        error_message=str(e)
                    ))
        
        total_time = time.time() - start_time
        
        # Compile summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        summary = {
            'total_predictions': len(predictions),
            'successful': len(successful),
            'failed': len(failed),
            'total_time': total_time,
            'average_time_per_prediction': total_time / len(predictions) if predictions else 0,
            'results': results
        }
        
        logger.info(f"🏁 Parallel processing completed in {total_time:.1f}s")
        logger.info(f"📊 Success rate: {len(successful)}/{len(predictions)} ({len(successful)/len(predictions)*100:.1f}%)")
        
        if failed:
            logger.warning(f"❌ Failed predictions: {[r.prediction_name for r in failed]}")
        
        return summary

    def run_predictions_sequential(self) -> Dict[str, Any]:
        """Process predictions sequentially (original behavior)."""
        predictions = self.config.get('predictions', [])
        logger.info(f"Starting sequential processing of {len(predictions)} predictions")
        
        results = []
        start_time = time.time()
        
        for i, prediction_config in enumerate(predictions):
            worker = FONLLWorker(self.config, worker_id=0)  # Single worker
            result = worker.process_prediction(prediction_config)
            results.append(result)
            
            if result.success:
                logger.info(f"✅ {result.prediction_name} completed successfully")
            else:
                logger.error(f"❌ {result.prediction_name} failed: {result.error_message}")
            
            # Add delay between predictions if specified
            if i < len(predictions) - 1:
                delay = self.config.get('delay_between_predictions', 0)
                if delay > 0:
                    time.sleep(delay)
        
        total_time = time.time() - start_time
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        summary = {
            'total_predictions': len(predictions),
            'successful': len(successful),
            'failed': len(failed),
            'total_time': total_time,
            'average_time_per_prediction': total_time / len(predictions) if predictions else 0,
            'results': results
        }
        
        logger.info(f"🏁 Sequential processing completed in {total_time:.1f}s")
        logger.info(f"📊 Success rate: {len(successful)}/{len(predictions)} ({len(successful)/len(predictions)*100:.1f}%)")
        
        return summary


def create_sample_config(filename: str = 'fonll_config.yaml'):
    """Create a sample configuration file with parallel options."""
    sample_config = {
        'fonll_url': 'http://www.lpthe.jussieu.fr/~cacciari/fonll/fonllform.html',
        'output_dir': './fonll_results',
        'wait_timeout': 15,
        'delay_between_predictions': 3,  # Only used in sequential mode
        'download_wait_time': 30,
        'max_workers': 4,  # Maximum number of parallel workers
        'parallel_mode': True,  # Set to False for sequential processing
        'browser_options': {
            'headless': True,  # Recommended for parallel processing
            'no_sandbox': True,
            'window_size': '1920,1080'
        },
        'email': 'your.email@example.com',  # Optional: receive results by email
        'predictions': [
            {
                'name': 'charm_7tev_central',
                'description': 'Charm production at 7 TeV, central rapidity',
                'fields': [
                    {
                        'type': 'select',
                        'selector': 'energy',
                        'value': '7000',
                        'description': 'Center-of-mass energy'
                    },
                    {
                        'type': 'radio',
                        'selector': 'quark',
                        'value': 'charm',
                        'description': 'Heavy quark type'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmin',
                        'value': '0',
                        'description': 'Minimum pT (GeV)'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmax',
                        'value': '50',
                        'description': 'Maximum pT (GeV)'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymin',
                        'value': '-0.5',
                        'description': 'Minimum rapidity'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymax',
                        'value': '4.5'
                    },
                    {
                        'type': 'select',
                        'selector': 'scheme',
                        'value': 'FONLL-C'
                    }
                ]
            },
            {
                'name': 'charm_13tev_mid_rapidity',
                'description': 'Charm production at 13 TeV, mid rapidity',
                'fields': [
                    {
                        'type': 'select',
                        'selector': 'energy',
                        'value': '13000'
                    },
                    {
                        'type': 'radio',
                        'selector': 'quark',
                        'value': 'charm'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmin',
                        'value': '1'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmax',
                        'value': '30'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymin',
                        'value': '-1.0'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymax',
                        'value': '1.0'
                    },
                    {
                        'type': 'select',
                        'selector': 'scheme',
                        'value': 'FONLL-B'
                    }
                ]
            },
            {
                'name': 'bottom_8tev_central',
                'description': 'Bottom production at 8 TeV, central rapidity',
                'fields': [
                    {
                        'type': 'select',
                        'selector': 'energy',
                        'value': '8000'
                    },
                    {
                        'type': 'radio',
                        'selector': 'quark',
                        'value': 'bottom'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmin',
                        'value': '3'
                    },
                    {
                        'type': 'input',
                        'selector': 'ptmax',
                        'value': '60'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymin',
                        'value': '-0.8'
                    },
                    {
                        'type': 'input',
                        'selector': 'ymax',
                        'value': '0.8'
                    },
                    {
                        'type': 'select',
                        'selector': 'scheme',
                        'value': 'FONLL-C'
                    }
                ]
            }
        ]
    }
    
    with open(filename, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Sample configuration created: {filename}")
    print("Please inspect the FONLL form and adjust field selectors as needed.")
    print("\nParallel processing features:")
    print("- Set 'parallel_mode: true' to enable parallel processing")
    print("- Adjust 'max_workers' to control the number of parallel browsers")
    print("- Use 'headless: true' for better performance in parallel mode")


def main():
    """Main function to run the FONLL automation."""
    parser = argparse.ArgumentParser(description='Automate FONLL web form submissions with parallel support')
    parser.add_argument('config', nargs='?', default='fonll_config.yaml',
                       help='Path to YAML configuration file (default: fonll_config.yaml)')
    parser.add_argument('--create-config', action='store_true',
                       help='Create a sample configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--inspect-form', action='store_true',
                       help='Open browser to inspect form elements (for config creation)')
    parser.add_argument('--sequential', action='store_true',
                       help='Force sequential processing (ignore parallel_mode in config)')
    parser.add_argument('--parallel', action='store_true',
                       help='Force parallel processing (ignore parallel_mode in config)')
    parser.add_argument('--max-workers', type=int,
                       help='Override max_workers setting from config')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate configuration without running automation')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create_config:
        create_sample_config(args.config)
        return
    
    if args.inspect_form:
        # Simple form inspection mode
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = None
        try:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ ChromeDriver initialized using webdriver-manager")
            except ImportError:
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ ChromeDriver initialized from PATH")
        except Exception as e:
            print(f"❌ Failed to initialize ChromeDriver: {e}")
            print("\n💡 Try installing webdriver-manager:")
            print("   pip install webdriver-manager")
            return
        
        print("🔍 Opening FONLL form for inspection...")
        print("📋 Use browser Developer Tools (F12) to inspect form elements")
        print("🎯 Look for 'name' attributes in HTML elements")
        
        driver.get('http://www.lpthe.jussieu.fr/~cacciari/fonll/fonllform.html')
        input("👀 Inspect the form elements, then press Enter to close browser...")
        driver.quit()
        return
    
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        print(f"Use --create-config to create a sample configuration file.")
        print(f"Use --inspect-form to open browser and inspect form elements.")
        sys.exit(1)
    
    try:
        automation = ParallelFONLLAutomation(args.config)
        
        # Override config settings with command line arguments
        if args.max_workers:
            automation.config['max_workers'] = args.max_workers
        
        # Determine processing mode
        parallel_mode = automation.config.get('parallel_mode', True)
        if args.sequential:
            parallel_mode = False
        elif args.parallel:
            parallel_mode = True
        
        if args.dry_run:
            print("🔍 Configuration validation:")
            print(f"  - FONLL URL: {automation.config['fonll_url']}")
            print(f"  - Output directory: {automation.config['output_dir']}")
            print(f"  - Number of predictions: {len(automation.config.get('predictions', []))}")
            print(f"  - Processing mode: {'Parallel' if parallel_mode else 'Sequential'}")
            if parallel_mode:
                print(f"  - Max workers: {automation.config.get('max_workers', 4)}")
            print(f"  - Browser headless: {automation.config.get('browser_options', {}).get('headless', False)}")
            print("✅ Configuration is valid")
            return
        
        # Run automation
        logger.info(f"🚀 Starting FONLL automation in {'parallel' if parallel_mode else 'sequential'} mode")
        
        if parallel_mode:
            summary = automation.run_predictions_parallel()
        else:
            summary = automation.run_predictions_sequential()
        
        # Print final summary
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        print(f"Total predictions: {summary['total_predictions']}")
        print(f"Successful: {summary['successful']} ({summary['successful']/summary['total_predictions']*100:.1f}%)")
        print(f"Failed: {summary['failed']} ({summary['failed']/summary['total_predictions']*100:.1f}%)")
        print(f"Total time: {summary['total_time']:.1f}s")
        print(f"Average time per prediction: {summary['average_time_per_prediction']:.1f}s")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed predictions:")
            for result in summary['results']:
                if not result.success:
                    print(f"   - {result.prediction_name}: {result.error_message}")
        
        # Count total downloaded files
        total_files = sum(len(r.downloaded_files) for r in summary['results'] if r.downloaded_files)
        if total_files > 0:
            print(f"\n📁 Total files downloaded: {total_files}")
            print(f"   Output directory: {automation.config['output_dir']}")
        
        sys.exit(0 if summary['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
