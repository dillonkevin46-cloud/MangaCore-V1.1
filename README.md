# 🔥 MagmaCore ITSM Platform

MagmaCore is a comprehensive, Django-based IT Service Management (ITSM) and Helpdesk platform. It is designed to streamline IT operations by providing a robust Ticketing System, Asset Management with active network monitoring, a Knowledge Base, and a Dynamic Form Builder.

The crown jewel of MagmaCore is its **Advanced Email-to-Ticket Engine**, which seamlessly integrates with the Microsoft Graph API to convert user emails into threaded tickets, process inline Outlook images, strip out messy HTML signatures, and send beautifully formatted HTML email receipts.

---

## ✨ Core Modules & Features

### 1. 🎫 Helpdesk Ticketing (`app_tickets`)
* **Microsoft Graph API Engine:** A background daemon that polls an Office 365 mailbox to automatically generate tickets.
* **Smart Threading:** Uses Regex to detect `#ID` in subject lines, appending email replies as comments rather than creating duplicate tickets.
* **Bulletproof HTML Machete:** Automatically strips out Outlook HTML signatures, previous email chains, `<style>` tags, and hidden formatting to keep the Helpdesk dashboard clean.
* **Advanced Attachment Handling:** Safely decodes base64 attachments, fixes Outlook's broken `cid:` inline images, and actively prevents signature image duplication (e.g., repeating Facebook/LinkedIn icons).
* **Auto-Responders & HTML Mail Trails:** Sends users their ticket number upon creation, and sends gorgeous HTML-formatted email trails when technicians reply from the web dashboard.

### 2. 🖥️ Asset & Network Management (`app_assets`)
* **Asset Tracking:** Track hardware, software, IPs, models, and employee assignments.
* **Active Monitoring:** Background engine that pings networked assets and logs uptime/downtime.
* **Locations & Categories:** Group assets by office branch or hardware type.

### 3. 📚 Knowledge Base (`app_kb`)
* Centralized repository for IT documentation, FAQs, and SOPs.
* CKEditor integration for rich-text article formatting and image uploads.

### 4. 📝 Dynamic Forms (`app_forms`)
* Custom Form Builder to create IT onboarding/offboarding requests, hardware requests, etc.
* Track and manage user responses natively.

### 5. ⚙️ Core Administration (`app_core`)
* Address Book and Contact Management.
* Technician Checklists and Task Management.
* Centralized Dashboard for high-level metrics.

---

## 🛠️ Technology Stack

* **Backend:** Python 3, Django 4+
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap (Themes: Moono-Lisa/Dark Mode)
* **Text Editor:** Django CKEditor (with Image Uploader)
* **API Integration:** Microsoft Graph API (OAuth2 Client Credentials Flow)

---

## 🔑 Microsoft Azure Setup (Crucial)

To use the Email-to-Ticket engine, you must configure a Microsoft Azure App Registration:

1. Go to the [Azure Portal (Entra ID)](https://entra.microsoft.com/).
2. Navigate to **App Registrations** -> **New Registration** (Name it "MagmaCore").
3. Go to **API Permissions** -> Add a permission -> **Microsoft Graph** -> **Application permissions** (NOT Delegated).
4. Add the following permissions:
   * `Mail.ReadWrite` (Allows the engine to read and mark emails as read).
   * `Mail.Send` (Allows the web dashboard to send out replies).
5. **CRITICAL:** Click the **"✓ Grant admin consent for [Your Company]"** button so both permissions have a green checkmark.
6. Go to **Certificates & secrets** and generate a new Client Secret. 
7. Go to **Overview** to copy your Tenant ID and Client ID.

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-repo/mangacore-v1.1.git](https://github.com/your-repo/mangacore-v1.1.git)
cd mangacore-v1.1
2. Create a Virtual Environment
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Environment Variables (settings.py or .env)
Ensure the following Microsoft Graph credentials are set in your environment or directly injected into MagmaCore/settings.py:

Python

MS_GRAPH_TENANT_ID = 'your-azure-tenant-id'
MS_GRAPH_CLIENT_ID = 'your-azure-client-id'
MS_GRAPH_CLIENT_SECRET = 'your-azure-client-secret'
MS_GRAPH_MAILBOX = 'support@yourdomain.com'
5. Database Migrations
Bash

python manage.py makemigrations
python manage.py migrate
6. Create Superuser (Admin)
Bash

python manage.py createsuperuser
7. Run the Web Server
Bash

python manage.py runserver
Access the application at http://127.0.0.1:8000.

🏃‍♂️ Running the Background Engines
MagmaCore relies on Python management commands running as background processes (daemons) to function fully. Open a separate terminal window for each:

The Email-to-Ticket Engine
This engine polls Microsoft Graph every 60 seconds, reads unread emails, parses attachments, threads comments, and marks emails as read.

Bash

python -u manage.py check_email_tickets
(Note: Use the -u flag in Python to force the terminal logs to print in real-time without buffering).

The Asset Monitoring Engine
This engine actively pings the IP addresses of hardware logged in app_assets to track network uptime.

Bash

python -u manage.py run_monitor
(For production environments, it is highly recommended to run these commands using a process manager like Supervisor, Systemd, or inside Docker Containers).

📂 Project Structure
Plaintext

MagmaCore/
├── MagmaCore/               # Main Django settings, URLs, ASGI/WSGI
├── app_core/                # Dashboard, User Auth, Checklists, Address Book
├── app_tickets/             # Ticketing logic, Graph API Utils, Email Engine
├── app_assets/              # Hardware tracking, Ping Monitor Engine
├── app_kb/                  # Knowledge Base models and views
├── app_forms/               # Dynamic form builder
├── staticfiles/             # CSS, JS, CKEditor assets, Admin themes
└── manage.py                # Django execution script
🛡️ License & Contact
MagmaCore v1.1 - Built for robust internal IT Service Management.

For technical support regarding the Microsoft Graph endpoints or URL routing, consult the utils.py and check_email_tickets.py inline documentation.

***

### How to use this:
Simply create a new file named `README.md` in the root folder of your project (where your `manage.py` file is), paste all of this text inside, and save it. GitHub (and VS Code) will automatically format it with headers, bullet points, and code blocks!