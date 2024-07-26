import requests
from bs4 import BeautifulSoup
import time
import random
import string
from urllib.parse import urljoin, urlencode
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from faker import Faker

fake = Faker()

def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def generate_query_params():
    """Generate random query parameters."""
    return {"param{}".format(random.randint(1, 10)): random_string() for _ in range(random.randint(1, 5))}

def generate_custom_headers():
    """Generate random custom headers."""
    return {
        'X-Custom-Header': random_string(),
        'X-Another-Header': random_string()
    }

def generate_user_agent():
    """Generate a random user agent."""
    browser = random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
    version = f"{random.randint(60, 99)}.0.{random.randint(1000, 9999)}.{random.randint(0, 99)}"
    os = random.choice(['Windows NT 10.0; Win64; x64', 'Macintosh; Intel Mac OS X 10_15_7', 'X11; Ubuntu; Linux x86_64'])
    user_agent = f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version} Safari/537.36"
    return user_agent

def get_post_urls(base_url):
    """Fetch all post URLs from a website."""
    post_urls = []
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/post/' in href:
                full_url = urljoin(base_url, href)
                post_urls.append(full_url)
    except requests.RequestException as e:
        print(f"Failed to fetch post URLs: {e}")
    return post_urls

def generate_traffic(url, num_requests, delay, method='GET', data=None, headers=None, pattern='steady', use_proxies=False, random_params=False, custom_headers=False, auto_agents=False, progress_callback=None):
    """
    Generate traffic by sending HTTP requests to a URL.
    """
    logs = []
    for i in range(num_requests):
        if progress_callback:
            progress_callback(i + 1, num_requests)

        user_agent = generate_user_agent() if auto_agents else random.choice(USER_AGENTS)
        headers = headers or {}
        headers.update({'User-Agent': user_agent})

        if custom_headers:
            headers.update(generate_custom_headers())

        if random_params and method == 'GET':
            url = f"{url}?{urlencode(generate_query_params())}"

        proxies = None
        if use_proxies:
            proxy = random.choice(PROXIES)
            proxies = {'http': proxy, 'https': proxy}

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, proxies=proxies)
            elif method == 'POST':
                response = requests.post(url, data=data, headers=headers, proxies=proxies)
            elif method == 'PUT':
                response = requests.put(url, data=data, headers=headers, proxies=proxies)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, proxies=proxies)
            else:
                logs.append(f"Unsupported method: {method}")
                continue

            logs.append(f"Status Code: {response.status_code} for {url}")
        except requests.RequestException as e:
            logs.append(f"Request failed: {e}")

        if pattern == 'burst':
            time.sleep(delay / 2)
        elif pattern == 'random':
            time.sleep(random.uniform(0.5, delay))
        elif pattern == 'spike':
            time.sleep(delay / 10)
        elif pattern == 'throttled':
            time.sleep(delay * 2)
        else:
            time.sleep(delay)

    with open('traffic_logs.txt', 'a') as log_file:
        for log in logs:
            log_file.write(log + '\n')

    return logs

def start_traffic_generation():
    base_url = url_entry.get()
    num_requests = int(num_requests_entry.get())
    delay = float(delay_entry.get())
    method = method_var.get()
    pattern = pattern_var.get()
    use_proxies = proxy_var.get()
    random_params = random_params_var.get()
    custom_headers = custom_headers_var.get()
    auto_agents = auto_agents_var.get()

    if not base_url or num_requests <= 0 or delay <= 0:
        messagebox.showerror("Input Error", "Please enter valid URL, number of requests, and delay.")
        return

    post_urls = get_post_urls(base_url)
    if not post_urls:
        messagebox.showerror("Error", "No post URLs found.")
        return

    def update_progress(current, total):
        progress_var.set((current / total) * 100)
        root.update_idletasks()
        if current == total:
            generate_graph()

    output_text.delete('1.0', tk.END)
    for url in post_urls:
        output_text.insert(tk.END, f"Sending traffic to: {url}\n")
        root.update_idletasks()
        logs = generate_traffic(url, num_requests, delay, method, headers=None, pattern=pattern, use_proxies=use_proxies, random_params=random_params, custom_headers=custom_headers, auto_agents=auto_agents, progress_callback=update_progress)

    messagebox.showinfo("Success", "Traffic generation completed.")

def generate_graph():
    """Generate a graph of traffic data."""
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(range(len(request_logs)), request_logs, 'b-', label='Requests')
    ax.set_xlabel('Request Number')
    ax.set_ylabel('Status Code')
    ax.set_title('Traffic Generation Overview')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=13, column=0, columnspan=2, padx=10, pady=10)

def save_configuration():
    """Save the current configuration to a file."""
    config = {
        'base_url': url_entry.get(),
        'num_requests': num_requests_entry.get(),
        'delay': delay_entry.get(),
        'method': method_var.get(),
        'pattern': pattern_var.get(),
        'use_proxies': proxy_var.get(),
        'random_params': random_params_var.get(),
        'custom_headers': custom_headers_var.get(),
        'auto_agents': auto_agents_var.get()
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        import json
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        messagebox.showinfo("Saved", "Configuration saved successfully.")

def load_configuration():
    """Load configuration from a file."""
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        import json
        with open(file_path, 'r') as file:
            config = json.load(file)
        url_entry.delete(0, tk.END)
        url_entry.insert(0, config.get('base_url', ''))
        num_requests_entry.delete(0, tk.END)
        num_requests_entry.insert(0, config.get('num_requests', ''))
        delay_entry.delete(0, tk.END)
        delay_entry.insert(0, config.get('delay', ''))
        method_var.set(config.get('method', 'GET'))
        pattern_var.set(config.get('pattern', 'steady'))
        proxy_var.set(config.get('use_proxies', False))
        random_params_var.set(config.get('random_params', False))
        custom_headers_var.set(config.get('custom_headers', False))
        auto_agents_var.set(config.get('auto_agents', False))
        messagebox.showinfo("Loaded", "Configuration loaded successfully.")

# Create the main window
root = tk.Tk()
root.title("Website Traffic Generator")

# Base URL
tk.Label(root, text="Base URL:").grid(row=0, column=0, padx=10, pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=5)

# Number of Requests
tk.Label(root, text="Number of Requests:").grid(row=1, column=0, padx=10, pady=5)
num_requests_entry = tk.Entry(root, width=50)
num_requests_entry.grid(row=1, column=1, padx=10, pady=5)

# Delay
tk.Label(root, text="Delay (seconds):").grid(row=2, column=0, padx=10, pady=5)
delay_entry = tk.Entry(root, width=50)
delay_entry.grid(row=2, column=1, padx=10, pady=5)

# Method
tk.Label(root, text="HTTP Method:").grid(row=3, column=0, padx=10, pady=5)
method_var = tk.StringVar(value='GET')
method_menu = tk.OptionMenu(root, method_var, 'GET', 'POST', 'PUT', 'DELETE')
method_menu.grid(row=3, column=1, padx=10, pady=5)

# Traffic Pattern
tk.Label(root, text="Traffic Pattern:").grid(row=4, column=0, padx=10, pady=5)
pattern_var = tk.StringVar(value='steady')
pattern_menu = tk.OptionMenu(root, pattern_var, 'steady', 'burst', 'random', 'spike', 'throttled')
pattern_menu.grid(row=4, column=1, padx=10, pady=5)

# Use Proxies
proxy_var = tk.BooleanVar(value=False)
proxy_check = tk.Checkbutton(root, text="Use Proxies", variable=proxy_var)
proxy_check.grid(row=5, column=0, padx=10, pady=5, columnspan=2)

# Random Query Parameters
random_params_var = tk.BooleanVar(value=False)
random_params_check = tk.Checkbutton(root, text="Random Query Parameters", variable=random_params_var)
random_params_check.grid(row=6, column=0, padx=10, pady=5, columnspan=2)

# Custom Headers
custom_headers_var = tk.BooleanVar(value=False)
custom_headers_check = tk.Checkbutton(root, text="Custom Headers", variable=custom_headers_var)
custom_headers_check.grid(row=7, column=0, padx=10, pady=5, columnspan=2)

# Auto Generate User Agents
auto_agents_var = tk.BooleanVar(value=False)
auto_agents_check = tk.Checkbutton(root, text="Auto Generate User Agents", variable=auto_agents_var)
auto_agents_check.grid(row=8, column=0, padx=10, pady=5, columnspan=2)

# Progress Bar
tk.Label(root, text="Progress:").grid(row=9, column=0, padx=10, pady=5)
progress_var = tk.DoubleVar(value=0)
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300)
progress_bar.grid(row=9, column=1, padx=10, pady=5)

# Output Text Area
tk.Label(root, text="Output:").grid(row=10, column=0, padx=10, pady=5)
output_text = scrolledtext.ScrolledText(root, width=80, height=15)
output_text.grid(row=10, column=1, padx=10, pady=5)

# Buttons
tk.Button(root, text="Start", command=start_traffic_generation).grid(row=11, column=0, columnspan=2, padx=10, pady=10)
tk.Button(root, text="Save Configuration", command=save_configuration).grid(row=12, column=0, padx=10, pady=10)
tk.Button(root, text="Load Configuration", command=load_configuration).grid(row=12, column=1, padx=10, pady=10)

# Graph Placeholder
tk.Label(root, text="Traffic Graph:").grid(row=13, column=0, padx=10, pady=5, columnspan=2)
graph_frame = tk.Frame(root)
graph_frame.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

# Run the GUI application
root.mainloop()

