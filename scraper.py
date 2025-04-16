import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class AjaxEcommerceScraper:
    def __init__(self):
        print("Initializing scraper...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            # Try to initialize the driver
            self.driver = webdriver.Chrome(options=chrome_options)
            print("WebDriver initialized successfully")
        except WebDriverException as e:
            print(f"Failed to initialize WebDriver: {e}")
            raise
            
        self.base_url = "https://webscraper.io/test-sites/e-commerce/ajax"
        self.results = []
        
    def navigate_to_site(self):
        """Navigate to the base URL of the site."""
        print(f"Navigating to {self.base_url}...")
        self.driver.get(self.base_url)
        time.sleep(5)  # Wait longer for page to fully load
        
        # Save screenshot for debugging
        self.driver.save_screenshot("homepage.png")
        print(f"Saved homepage screenshot to {os.path.abspath('homepage.png')}")
        
        # Wait for the page to load properly
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sidebar-nav"))
            )
            print("Base page loaded successfully")
        except TimeoutException:
            print("Timeout waiting for page to load!")
            # Try to get the page source to diagnose
            print(f"Page source excerpt: {self.driver.page_source[:500]}...")
        
    def get_categories(self):
        """Get all main categories from the homepage."""
        print("Attempting to find categories...")
        
        # Print page source for debugging
        print("Page source excerpt:")
        print(self.driver.page_source[:1000])
        
        try:
            # Try different selectors to find the categories
            selectors = [
                "div.sidebar-nav ul.nav li.sidebar-category a",
                ".sidebar-category a",
                "ul.nav li a",
                "div.sidebar-nav a"
            ]
            
            categories = []
            for selector in selectors:
                print(f"Trying selector: {selector}")
                categories = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if categories:
                    print(f"Found {len(categories)} elements with selector: {selector}")
                    break
            
            result = []
            for cat in categories:
                name = cat.text.strip()
                href = cat.get_attribute("href")
                if name and href:
                    result.append((name, href))
                    print(f"Category: {name}, URL: {href}")
            
            print(f"Found {len(result)} categories: {[name for name, _ in result]}")
            return result
        except Exception as e:
            print(f"Error finding categories: {e}")
            return []
        
    def get_subcategories(self, category_url):
        """Get all subcategories from a category page."""
        print(f"Navigating to category URL: {category_url}")
        self.driver.get(category_url)
        time.sleep(5)  # Wait longer for page to load
        
        # Save screenshot for debugging
        filename = f"category_{category_url.split('/')[-1]}.png"
        self.driver.save_screenshot(filename)
        print(f"Saved category screenshot to {os.path.abspath(filename)}")
        
        try:
            # Try different selectors for subcategories
            selectors = [
                "div.sidebar-nav ul.nav li.sidebar-sub-category a",
                ".sidebar-sub-category a",
                "ul.nav li.sidebar-sub-category a",
                "div.sidebar-nav li.active ul li a"
            ]
            
            subcategories = []
            for selector in selectors:
                print(f"Trying selector for subcategories: {selector}")
                subcategories = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if subcategories:
                    print(f"Found {len(subcategories)} elements with selector: {selector}")
                    break
            
            result = []
            for sub in subcategories:
                name = sub.text.strip()
                href = sub.get_attribute("href")
                if name and href:
                    result.append((name, href))
                    print(f"Subcategory: {name}, URL: {href}")
            
            print(f"Found {len(result)} subcategories: {[name for name, _ in result]}")
            return result
        except TimeoutException:
            print("No subcategories found or timeout waiting for subcategories")
            return []
        except Exception as e:
            print(f"Error finding subcategories: {e}")
            return []
        
    def extract_product_data(self, max_products=50):
        """Extract product data from the current page."""
        print("Extracting product data from current page...")
        
        # Save screenshot for debugging
        filename = f"products_page.png"
        self.driver.save_screenshot(filename)
        print(f"Saved products page screenshot to {os.path.abspath(filename)}")
        
        try:
            # Wait for products to be visible
            selectors = [
                ".thumbnail",
                "div.thumbnail",
                "div.row div.thumbnail",
                "div.products div.thumbnail"
            ]
            
            for selector in selectors:
                print(f"Trying selector for products: {selector}")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if products:
                        print(f"Found {len(products)} products with selector: {selector}")
                        break
                except:
                    products = []
                    continue
            
            if not products:
                print("No products found on page")
                return 0
                
            product_count = 0
            current_category = "Unknown"
            
            # Try to get current category/subcategory name
            for selector in ["h1", "h2", "h3", ".active"]:
                try:
                    current_category = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    print(f"Current category from selector {selector}: {current_category}")
                    break
                except:
                    continue
            
            for product in products:
                if product_count >= max_products:
                    break
                    
                try:
                    # Try different selectors for product elements
                    name_selectors = [".title", "a.title", "h4.title a", "h4 a"]
                    name = None
                    for selector in name_selectors:
                        try:
                            name = product.find_element(By.CSS_SELECTOR, selector).text.strip()
                            if name:
                                break
                        except:
                            continue
                    
                    price_selectors = [".price", "h4.price", "p.price"]
                    price = None
                    for selector in price_selectors:
                        try:
                            price = product.find_element(By.CSS_SELECTOR, selector).text.strip()
                            if price:
                                break
                        except:
                            continue
                    
                    # Getting product URL
                    url_selectors = [".title", "a.title", "h4.title a", "h4 a"]
                    url = None
                    for selector in url_selectors:
                        try:
                            url = product.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
                            if url:
                                break
                        except:
                            continue
                    
                    # Handle ratings (some products might not have ratings)
                    rating = 0
                    rating_selectors = [".ratings", "div.ratings", "p.ratings"]
                    for selector in rating_selectors:
                        try:
                            rating_element = product.find_element(By.CSS_SELECTOR, selector)
                            star_selectors = [".glyphicon-star", ".fa-star"]
                            for star_selector in star_selectors:
                                try:
                                    filled_stars = rating_element.find_elements(By.CSS_SELECTOR, star_selector)
                                    rating = len(filled_stars)
                                    break
                                except:
                                    continue
                            if rating > 0:
                                break
                        except:
                            continue
                    
                    # Handle reviews count
                    reviews_count = 0
                    review_selectors = [".ratings p", "p.review", ".reviews"]
                    for selector in review_selectors:
                        try:
                            reviews_text = product.find_element(By.CSS_SELECTOR, selector).text.strip()
                            reviews_count = int(''.join(filter(str.isdigit, reviews_text)))
                            break
                        except:
                            continue
                    
                    if name and price:
                        self.results.append({
                            'category': current_category,
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews_count,
                            'url': url or ""
                        })
                        product_count += 1
                        print(f"Extracted product: {name}, Price: {price}, Rating: {rating}, Reviews: {reviews_count}")
                    
                except NoSuchElementException as e:
                    print(f"Error extracting product data: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error extracting product: {e}")
                    continue
            
            return product_count
        except TimeoutException:
            print("Timeout waiting for products to appear!")
            return 0
        except Exception as e:
            print(f"Error in extract_product_data: {e}")
            return 0
        
    def handle_pagination(self, max_products=50):
        """Handle AJAX pagination to get all products up to max_products."""
        print("Handling pagination...")
        products_extracted = self.extract_product_data(max_products)
        page_number = 1
        
        # Continue clicking on next page while there are more pages and we haven't reached max_products
        while products_extracted < max_products:
            try:
                print(f"Looking for next page button (current page: {page_number})")
                
                # Try different selectors for the next page button
                next_button = None
                selectors = [
                    ".pagination .next",
                    "ul.pagination li.next a",
                    "nav ul.pagination li.next",
                    "ul.pagination li:last-child a"
                ]
                
                for selector in selectors:
                    try:
                        next_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if next_button:
                            print(f"Found next button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not next_button:
                    print("Next button not found")
                    break
                
                if "disabled" in next_button.get_attribute("class"):
                    print("Next button is disabled, no more pages")
                    break  # No more pages
                
                print("Clicking next page")
                next_button.click()
                page_number += 1
                time.sleep(5)  # Wait longer for AJAX to load
                
                new_products = self.extract_product_data(max_products - products_extracted)
                print(f"Extracted {new_products} products from page {page_number}")
                
                if new_products == 0:
                    print("No new products found, breaking pagination loop")
                    break  # No new products found
                    
                products_extracted += new_products
                
            except TimeoutException:
                print("Timeout finding next button")
                break
            except NoSuchElementException:
                print("Next button not found")
                break
            except Exception as e:
                print(f"Error in pagination: {e}")
                break
        
    def scrape_all(self, max_products_per_subcategory=50):
        """Scrape data from all categories and subcategories."""
        print("Starting full scrape process...")
        self.navigate_to_site()
        categories = self.get_categories()
        
        if not categories:
            print("No categories found! Taking a screenshot for debugging...")
            self.driver.save_screenshot("debug_screenshot.png")
            print(f"Saved screenshot to {os.path.abspath('debug_screenshot.png')}")
            print("Page source excerpt:")
            print(self.driver.page_source[:2000])  # Print first part of page source for debugging
        
        for category_name, category_url in categories:
            print(f"\n>>> Scraping category: {category_name} <<<")
            subcategories = self.get_subcategories(category_url)
            
            if not subcategories:
                print(f"No subcategories found for {category_name}, treating as direct product page")
                self.handle_pagination(max_products_per_subcategory)
            else:
                for subcategory_name, subcategory_url in subcategories:
                    print(f"\n>> Scraping subcategory: {subcategory_name} <<")
                    self.driver.get(subcategory_url)
                    time.sleep(5)
                    self.handle_pagination(max_products_per_subcategory)
        
        print(f"Scraping complete! Total products found: {len(self.results)}")
        
    def save_results(self, filename="product_data.json"):
        """Save the scraped results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4)
        print(f"Saved {len(self.results)} products to {filename}")
        
    def close(self):
        """Close the webdriver."""
        print("Closing WebDriver...")
        self.driver.quit()

if __name__ == "__main__":
    scraper = AjaxEcommerceScraper()
    try:
        scraper.scrape_all()
        scraper.save_results()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        scraper.close()