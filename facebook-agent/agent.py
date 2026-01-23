import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

# Load environment variables
load_dotenv()


class FacebookGroupAgent:
    
    def __init__(self):
        
        """Initialize the Facebook Group automation agent."""
        # Facebook credentials
        self.access_token = os.getenv('FB_ACCESS_TOKEN')
        self.group_id = os.getenv('FB_GROUP_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'

        # Gemini setup
        self.llm = model = ChatGoogleGenerativeAI(
            model="gemini-3-pro-preview",
            temperature=0.7, 
            max_tokens=4098,
            timeout=None,
            max_retries=2,
        )

        # System prompt
        self.system_prompt = """You are a helpful and friendly community assistant in a Facebook group. Your role is to provide valuable insights, answer questions, and engage meaningfully with group members. Be conversational, empathetic, and concise. Always aim to add value to the discussion.
        """

        # Setup LangChain prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human","Original Post: {post_content}\n\nGenerate a helpful, engaging comment for this post.")
        ])

        self.reply_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """Previous context: Original Post: {original_post}\n\nYour Previous Comment: {ai_comment}\n\nUser's Reply: {user_reply}\n\nGenerate a thoughtful follow-up response:""")
        ])

        # Create chains
        self.comment_chain = self.prompt_template | self.llm
        self.reply_chain = self.reply_template | self.llm
        print('LLM and Prompts initialized successfully')
        
        # Google Sheets setup
        self.setup_google_sheets()
        print('Google Sheets initialized successfully')

        # State management
        self.last_checked = datetime.now() - timedelta(hours=1)
        self.processed_posts = set()
        self.ai_comments = {}  # Store AI comments for threading

        print("✓ Facebook Group Agent initialized successfully")

    def setup_google_sheets(self):
        """Setup Google Sheets connection for logging."""
        try:
            creds_file = os.getenv('GOOGLE_SHEETS_CREDS', 'credentials.json')
            sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'FB_Agent_Logs')

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(
                creds_file, scopes=scopes)
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open(sheet_name).sheet1

            # Setup headers if empty
            if not self.sheet.row_values(1):
                self.sheet.append_row([
                    'Timestamp', 'Post Link', 'User Name',
                    'User Comment', 'AI Response', 'Type'
                ])

            print("✓ Google Sheets connected successfully")
        except Exception as e:
            print(f"⚠ Google Sheets setup failed: {e}")
            self.sheet = None

    def make_api_request(self, endpoint: str, method: str = 'GET',
                         params: Dict = None, data: Dict = None,
                         max_retries: int = 3) -> Optional[Dict]:
        """Make API request with exponential backoff."""
        url = f"{self.base_url}/{endpoint}"

        if params is None:
            params = {}
        params['access_token'] = self.access_token

        for attempt in range(max_retries):
            try:
                if method == 'GET':
                    response = requests.get(url, params=params)
                elif method == 'POST':
                    response = requests.post(url, params=params, data=data)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = (2 ** attempt) * 5
                    print(f"⚠ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(
                        f"⚠ API error {response.status_code}: {response.text}")
                    return None

            except Exception as e:
                print(f"⚠ Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return None

    def get_new_posts(self) -> List[Dict]:
        """Fetch new posts from the Facebook group since last check."""
        params = {
            'fields': 'id,message,from,created_time,permalink_url',
            'since': int(self.last_checked.timestamp())
        }

        result = self.make_api_request(f"{self.group_id}/feed", params=params)

        if result and 'data' in result:
            posts = result['data']
            print(f"✓ Found {len(posts)} new posts")
            return posts

        return []

    def get_post_comments(self, post_id: str) -> List[Dict]:
        """Get all comments on a specific post."""
        params = {
            'fields': 'id,message,from,created_time,parent'
        }

        result = self.make_api_request(f"{post_id}/comments", params=params)

        if result and 'data' in result:
            return result['data']

        return []

    def post_comment(self, post_id: str, message: str) -> Optional[str]:
        """Post a comment on a Facebook post."""
        data = {'message': message}

        result = self.make_api_request(
            f"{post_id}/comments",
            method='POST',
            data=data
        )

        if result and 'id' in result:
            print(f"✓ Posted comment: {result['id']}")
            return result['id']

        return None

    def generate_response(self, post_content: str) -> str:
        """Generate AI response for a post using LangChain."""
        try:
            response = self.comment_chain.invoke({
                "post_content": post_content
            })
            return response.content
        except Exception as e:
            print(f"⚠ LLM error: {e}")
            return None

    def generate_reply(self, original_post: str, ai_comment: str,
                       user_reply: str) -> str:
        """Generate AI reply to a user's response."""
        try:
            response = self.reply_chain.invoke({
                "original_post": original_post,
                "ai_comment": ai_comment,
                "user_reply": user_reply
            })
            return response.content
        except Exception as e:
            print(f"⚠ LLM error: {e}")
            return None

    def log_to_sheets(self, timestamp: str, post_link: str,
                      user_name: str, user_comment: str,
                      ai_response: str, interaction_type: str):
        """Log interaction to Google Sheets."""
        if not self.sheet:
            return

        try:
            self.sheet.append_row([
                timestamp, post_link, user_name,
                user_comment, ai_response, interaction_type
            ])
            print("✓ Logged to Google Sheets")
        except Exception as e:
            print(f"⚠ Sheets logging failed: {e}")

    def process_post(self, post: Dict):
        """Process a new post and generate response."""
        post_id = post['id']

        if post_id in self.processed_posts:
            return

        post_message = post.get('message', '')
        if not post_message:
            return

        user_name = post.get('from', {}).get('name', 'Unknown')
        post_link = post.get(
            'permalink_url', f"https://facebook.com/{post_id}")

        print(f"\n📝 Processing post from {user_name}")
        print(f"   Content: {post_message[:100]}...")

        # Generate AI response
        ai_response = self.generate_response(post_message)

        if not ai_response:
            return

        print(f"🤖 Generated response: {ai_response[:100]}...")

        # Post comment
        comment_id = self.post_comment(post_id, ai_response)

        if comment_id:
            # Store for threading
            self.ai_comments[comment_id] = {
                'original_post': post_message,
                'ai_comment': ai_response,
                'post_id': post_id
            }

            # Log to sheets
            self.log_to_sheets(
                datetime.now().isoformat(),
                post_link,
                user_name,
                post_message,
                ai_response,
                'New Post'
            )

            self.processed_posts.add(post_id)

    def check_replies(self):
        """Check for replies to AI comments and respond."""
        for comment_id, context in list(self.ai_comments.items()):
            post_id = context['post_id']
            comments = self.get_post_comments(post_id)

            for comment in comments:
                # Check if this is a reply to our comment
                parent_id = comment.get('parent', {}).get('id')

                if parent_id == comment_id:
                    reply_id = comment['id']

                    # Skip if already processed
                    if reply_id in self.processed_posts:
                        continue

                    user_reply = comment.get('message', '')
                    user_name = comment.get('from', {}).get('name', 'Unknown')

                    print(f"\n💬 Reply detected from {user_name}")
                    print(f"   Reply: {user_reply[:100]}...")

                    # Generate follow-up
                    ai_reply = self.generate_reply(
                        context['original_post'],
                        context['ai_comment'],
                        user_reply
                    )

                    if ai_reply:
                        print(f"🤖 Generated reply: {ai_reply[:100]}...")

                        # Post reply to the user's comment
                        new_comment_id = self.post_comment(reply_id, ai_reply)

                        if new_comment_id:
                            # Log to sheets
                            self.log_to_sheets(
                                datetime.now().isoformat(),
                                f"https://facebook.com/{post_id}",
                                user_name,
                                user_reply,
                                ai_reply,
                                'Reply'
                            )

                            self.processed_posts.add(reply_id)

    def run_cycle(self):
        """Run one complete cycle of the agent."""
        print(f"\n{'='*60}")
        print(
            f"🔄 Running cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Get and process new posts
        new_posts = self.get_new_posts()
        for post in new_posts:
            self.process_post(post)

        # Check for replies to our comments
        self.check_replies()

        # Update last checked time
        self.last_checked = datetime.now()

        print(
            f"\n✓ Cycle complete. Processed {len(self.processed_posts)} items total.")

    def run(self, interval_minutes: int = 5):
        """Run the agent continuously."""
        print(f"\n🚀 Starting Facebook Group Agent")
        print(f"   Polling interval: {interval_minutes} minutes")
        print(f"   Group ID: {self.group_id}")
        print(f"   Press Ctrl+C to stop\n")

        try:
            while True:
                self.run_cycle()
                print(
                    f"\n⏳ Waiting {interval_minutes} minutes until next cycle...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n👋 Agent stopped by user")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    agent = FacebookGroupAgent()

    # Run with 5-minute intervals (adjust as needed)
    agent.run(interval_minutes=5)


if __name__ == "__main__":
    main()
