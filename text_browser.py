import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from urllib.parse import urljoin

console = Console()
history = []

def fetch_and_parse(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return None

def display_page(soup, url):
    console.clear()
    console.rule("[bold green]Text Browser")
    
    # Page title
    title = soup.title.string if soup.title else "Untitled Page"
    console.print(Text(title, style="bold underline cyan"))

    # Main content (text from paragraph tags)
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text:
            console.print(text)

    # Links
    links = soup.find_all('a', href=True)
    link_map = []
    if links:
        console.print("\n[bold magenta]Links:[/bold magenta]")
        for i, link in enumerate(links, 1):
            text = link.get_text(strip=True) or "(no text)"
            href = urljoin(url, link['href'])
            console.print(f"[{i}] [blue]{text}[/blue] → {href}")
            link_map.append(href)
    else:
        console.print("\n[dim]No links found.[/dim]")

    return link_map

def main():
    current_url = Prompt.ask("Enter a URL to start (e.g., https://example.com)")
    while True:
        soup = fetch_and_parse(current_url)
        if not soup:
            current_url = Prompt.ask("\nEnter another URL or type 'exit'")
            if current_url.lower() == 'exit':
                break
            continue

        link_map = display_page(soup, current_url)

        action = Prompt.ask("\nType link number, new URL, [yellow]'back'[/yellow], or [red]'exit'[/red]").strip().lower()

        if action == 'exit':
            break
        elif action == 'back':
            if history:
                current_url = history.pop()
            else:
                console.print("[dim]No history available.[/dim]")
        elif action.isdigit():
            idx = int(action) - 1
            if 0 <= idx < len(link_map):
                history.append(current_url)
                current_url = link_map[idx]
            else:
                console.print("[red]Invalid link number.[/red]")
        else:
            if action.startswith('http'):
                history.append(current_url)
                current_url = action
            else:
                console.print("[red]Enter a full URL starting with http/https.[/red]")

if __name__ == '__main__':
    main()
