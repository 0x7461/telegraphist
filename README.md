# telegraphist - Advanced Backup Solution for Telegram Chats

> **Customized fork of [TelegramBackup](https://github.com/N4rr34n6/TelegramBackup) by N4rr34n6**
> Enhanced with environment-based configuration, organized output structure, and modern Python tooling.
> Formerly `gr4mfetch`, renamed 2026-10-01; old GitHub links redirect here.

telegraphist is a comprehensive tool designed for extracting, organizing, and archiving messages from your Telegram chats, channels, and groups. It preserves not only message content but also media files, reactions, replies, forwarded content, and other rich features that make Telegram unique. Whether you need to back up personal conversations, archive large channels, or export group discussions, telegraphist offers a complete solution.

## 🎯 Fork Enhancements

This fork adds the following improvements over the original:

- **🔐 Environment-based Configuration**: Credentials stored securely in `.env` file (never committed to git)
- **📁 Organized Output Structure**: Backups organized by entity type (Users/Channels/Groups/Supergroups)
- **📦 Modern Package Management**: Uses `uv` for fast, reliable dependency management
- **🗂️ Isolated Entity Backups**: Each entity gets its own directory with database, HTML, and media
- **🛡️ Enhanced Security**: Comprehensive `.gitignore` to protect sensitive data

## 🌟 Key Features

- **Complete Message Archiving**: Preserve text messages, media files, reactions, replies, service messages, and more
- **Rich Media Support**: Download and view photos, videos, voice messages, audio files, and documents
- **Interactive HTML Export**: Browse your archived messages with a clean, responsive interface similar to Telegram's own design
- **Incremental Updates**: Update existing backups with only new messages without recreating the entire archive
- **Contact Management**: Extract and save your complete contact list in a searchable format
- **Message Threading**: View message replies with links to original messages and preview on hover
- **Reaction Support**: See all emoji reactions to messages just like in Telegram
- **Date Grouping**: Messages are organized by date for easier navigation
- **Multiple Entity Types**: Support for private chats, channels, supergroups, and regular groups
- **Web Preview Support**: Link previews are preserved in the backup
- **SQLite Storage**: All data is stored in a structured SQLite database for easy access and querying
- **Session Security**: Automatic session management with cleanup of sensitive service messages

## 📋 Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Internet connection
- Telegram account

### Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/0x7461/telegraphist.git
    cd telegraphist
    ```

2. **Install dependencies with uv**:
    ```bash
    uv sync
    ```

    This automatically creates a virtual environment and installs:
    - `telethon` - Telegram API client
    - `jinja2` - HTML template engine
    - `beautifulsoup4` - HTML parsing
    - `python-dotenv` - Environment variable management

## 🔑 Getting Telegram API Credentials

Before using telegraphist, you need to obtain your own Telegram API credentials:

1. **Visit the Telegram API Development Tools**:
   - Go to https://my.telegram.org
   - Log in with your Telegram account

2. **Create a New Application**:
   - Click on "API Development tools"
   - Fill out the form with your application details
   - Suggested values:
     - App title: `telegraphist` (or your preference)
     - Short name: `telegraphist`
     - Platform: `Desktop`
   - Click "Create application"

3. **Get Your API Credentials**:
   - After creating the application, you'll see your **api_id** (a number) and **api_hash** (a string)
   - Keep these values secure - they're associated with your Telegram account

4. **Configure telegraphist**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your credentials:
     ```env
     # Your API ID (a number, no quotes)
     API_ID=12345678

     # Your API Hash (a string, keep as-is)
     API_HASH=abcdef1234567890abcdef1234567890

     # Optional: Session name
     SESSION_NAME=telegram_session
     ```

> **IMPORTANT**:
> - The `.env` file is git-ignored and will never be committed
> - Never share your API credentials or commit them to version control
> - `API_ID` should be a number without quotes
> - `API_HASH` should be the hash string without quotes

## 🚀 Usage

1. **Run the script**:
    ```bash
    uv run python telegram_backup.py
    ```

2. **First-Time Login**:
   - Enter your Telegram phone number when prompted (include country code, e.g., +12345678900)
   - You'll receive a code on your Telegram app - enter this code when prompted
   - If you have two-factor authentication enabled, you'll need to enter your password

3. **Managing Contacts and Entities**:
   - The script will automatically extract your contacts and save them to a CSV file
   - It will generate a list of all available entities (users, channels, groups) and save it to a CSV file
   - Review the entity list in your console to identify which ones you want to backup

4. **Backup Options**:
   Choose from the menu options:
   - **[E] Process a specific entity**: Backup a single chat, channel, or group
   - **[T] Process all entities**: Backup everything
   - **[U] Update existing backup**: Add only new messages to an existing backup
   - **[D] Delete Telegram service messages**: Clean up service messages
   - **[X] Close current session**: End the current session securely
   - **[S] Exit**: Exit the program

5. **When processing entities**:
   - You can specify how many messages to retrieve (leave blank for all)
   - Choose whether to download all media files (Y/N)
   - For large chats, consider processing in batches to avoid timeouts

6. **Updating existing backups**:
   - When using the [U] option, select the entity you want to update
   - The script will identify the last message in your existing backup
   - Only messages newer than this will be retrieved and added to the database
   - The HTML file will be regenerated with all messages (old and new)

7. **Accessing Your Backup**:
   - All backups are organized in the `output/` directory by entity type:
     ```
     output/
     ├── Users/[entity_name]/
     ├── Channels/[entity_name]/
     ├── Supergroups/[entity_name]/
     └── Groups/[entity_name]/
     ```
   - Each entity folder contains:
     - SQLite database (`.db` file) with all message data
     - HTML file for browsing messages in your browser
     - `media/` subdirectory with downloaded files
   - Open the HTML file in your browser to view archived messages with date grouping, reactions, replies, and media playback

## 📱 HTML Export Features

The generated HTML export includes:

- **Message Grouping by Date**: Messages are organized by day for easier navigation
- **Sender Information**: Each message shows who sent it
- **Message Threading**: Replies are linked to original messages with preview on hover
- **Reactions Display**: See emoji reactions to messages
- **Media Playback**: Directly play audio, voice messages and videos in the browser
- **Image Display**: View images inline
- **Web Link Previews**: Link previews similar to Telegram's interface
- **Service Messages**: System notifications (joins, leaves, etc.) are properly displayed
- **Forwarded Messages**: Clear indication of forwarded content with source links when available
- **Mobile-Friendly Design**: Responsive layout works on all devices

## 💾 Database Structure

The SQLite database contains the following main tables:

- **messages**: Stores the core message data including text, media, timestamps, and metadata
- **buttons**: Records message buttons and inline URLs
- **replies**: Tracks reply relationships between messages
- **reactions**: Stores emoji reactions to messages with counts

You can query this database directly using any SQLite browser for advanced analysis or custom exports.

## ⚠️ Handling Large Backups

If you're backing up chats with hundreds of thousands of messages:

1. **Start with a smaller batch**: First try backing up a limited number (e.g., 1000) to test
2. **Ensure adequate storage**: Media files can consume significant disk space
3. **Use incremental updates**: After the initial backup, use the update feature for periodic updates
4. **Run in a stable environment**: Avoid using USB drives or removable storage for the backup process
5. **Be patient**: Large backups can take considerable time depending on your internet connection

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **Syntax Error with API Credentials**:
   - Ensure `api_id` is an integer without quotes
   - Ensure `api_hash` is a string with quotes
   - Double-check that you saved the file after making changes

2. **Connection Errors**:
   - Verify your internet connection
   - Check if Telegram is accessible in your region
   - Some networks may block Telegram's API servers

3. **Permission Errors**:
   - Run the script from a location where you have read/write permissions
   - Avoid running from USB drives or network shares if possible

4. **Missing Dependencies**:
   - If you get import errors, verify that all required packages are installed
   - Try running `pip install -r requirements.txt` again

5. **Session File Issues**:
   - If you get errors related to the `.session` file, delete it and start a new session
   - These files are stored in the same directory as the script

6. **Unicode/Encoding Issues**:
   - If you see encoding problems in CSV files, make sure your terminal supports UTF-8
   - Try opening the CSV files in a modern spreadsheet application instead of a text editor

### Advanced Tips

- **Customizing HTML Output**: You can modify the `template.html` file to change how the exported HTML looks
- **Working with the Database**: The SQLite database can be opened with tools like DB Browser for SQLite if you want to perform custom queries
- **Automating Backups**: Consider setting up a scheduled task to run the script periodically with `uv run python telegram_backup.py`
- **Media File Management**: Large media files are stored in each entity's `media/` subdirectory, organized by entity type for easy navigation
- **Organized Backups**: The hierarchical structure (`output/EntityType/entity_name/`) makes it easy to find and manage specific backups

## 📂 Project Structure

```
telegraphist/
├── .env                    # Your credentials (git-ignored, create from .env.example)
├── .env.example            # Template for credentials
├── telegram_backup.py      # Main backup script
├── template.html           # HTML export template
├── pyproject.toml          # Project dependencies (managed by uv)
├── uv.lock                 # Dependency lock file
├── *.session               # Telegram session files (git-ignored)
└── output/                 # All backup data (git-ignored)
    ├── contacts_*.csv      # Your contact list
    ├── entities_*.csv      # Available chats/channels
    ├── Users/              # Private chats
    │   └── [entity_name]/
    │       ├── [entity_name].db
    │       ├── [entity_name].html
    │       └── media/
    ├── Channels/           # Broadcast channels
    │   └── [entity_name]/
    │       ├── [entity_name].db
    │       ├── [entity_name].html
    │       └── media/
    ├── Supergroups/        # Large groups
    │   └── [entity_name]/
    │       ├── [entity_name].db
    │       ├── [entity_name].html
    │       └── media/
    └── Groups/             # Regular groups
        └── [entity_name]/
            ├── [entity_name].db
            ├── [entity_name].html
            └── media/
```

## 📝 Technical Details

- **Message Processing**: telegraphist iterates through messages of a selected entity, extracts their content and metadata, and stores everything in an SQLite database.
- **Media Handling**: Media files are downloaded to a structured directory and referenced in the database by path and hash.
- **HTML Rendering**: Using Jinja2 templating, the script generates a responsive HTML interface for browsing the archived messages.
- **Flood Control**: The script implements flood control management by respecting Telegram API rate limits.
- **Character Encoding**: Special attention is paid to proper UTF-8 encoding to handle all languages and emoji correctly.

## ⚖️ Ethical Use and Legal Considerations

**telegraphist** is intended for personal use, enabling users to backup their own Telegram data. The misuse of this tool, such as unauthorized data extraction from accounts or channels where you do not have permission, is strictly prohibited. Ensure that all data you process with this tool complies with Telegram's terms of service and local data protection laws.

## 📄 License

This project is provided under the GNU Affero General Public License v3.0, inherited from the original TelegramBackup project. You can find the full license text in the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

This project is a fork of [TelegramBackup](https://github.com/N4rr34n6/TelegramBackup) by **N4rr34n6**. All core functionality and the original design are credited to the original author. This fork adds customizations for personal workflow preferences while maintaining the excellent foundation provided by the original project.

---

*telegraphist provides a comprehensive, customizable, and reliable solution for preserving your Telegram communications. Whether for personal archiving or professional data analysis, this tool offers unmatched flexibility and functionality.*
