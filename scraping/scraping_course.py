from playwright.sync_api import sync_playwright
import time
import json

def scrape_course_content():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Opening course content page...")
        page.goto("https://tds.s-anand.net/#/2025-01/")
        
        # Wait for all JS to load
        page.wait_for_load_state("networkidle")
        time.sleep(5)  # Extra buffer to allow rendering

        print("Extracting section and lesson titles...")

        # Evaluate inside browser context to extract content
        course_data = page.evaluate("""
        () => {
            const results = [];
            const sections = document.querySelectorAll('nav > div');
            sections.forEach(section => {
                const sectionTitle = section.querySelector('h2')?.innerText || 'Untitled Section';
                const lessons = [];
                section.querySelectorAll('li a').forEach(lesson => {
                    lessons.push({
                        title: lesson.innerText.trim(),
                        url: lesson.href
                    });
                });
                results.push({
                    section: sectionTitle,
                    lessons: lessons
                });
            });
            return results;
        }
        """)

        # Save to JSON
        with open("course.json", "w", encoding="utf-8") as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)

        print("✅ Saved course content to course.json")
        browser.close()

if __name__ == "__main__":
    scrape_course_content()
