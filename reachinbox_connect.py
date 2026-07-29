#!/usr/bin/env python3
"""
ReachInbox API connector - Find Jason's reply and send a response
"""
import requests
import json
from typing import Optional, Dict, List

class ReachInboxClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.reachinbox.ai"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_campaigns(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all campaigns"""
        url = f"{self.base_url}/api/v1/campaigns/all"
        params = {"limit": limit, "offset": offset, "sort": "newest"}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return data.get("rows", []) if isinstance(data, dict) else data

    def get_campaign_leads(self, campaign_id: int) -> List[Dict]:
        """Get leads from a specific campaign"""
        url = f"{self.base_url}/api/v1/leads"
        params = {"campaignId": campaign_id, "lastLead": "false"}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return data.get("leads", []) if isinstance(data, dict) else []

    def find_jason_with_reply(self) -> Optional[Dict]:
        """Search all campaigns for Jason who has replied"""
        campaigns = self.get_campaigns()
        for campaign in campaigns:
            leads = self.get_campaign_leads(campaign["id"])
            for lead in leads:
                first_name = lead.get("attributes", {}).get("firstName", "")
                if first_name.lower() == "jason" and lead.get("replyReceived"):
                    lead["campaign"] = campaign
                    return lead
        return None

    def send_reply(self, to_email: str, subject: str, body: str,
                   from_email: str, references: Optional[List[str]] = None,
                   in_reply_to: str = "", original_message_id: str = "") -> Dict:
        """Send a reply to a lead using multipart form-data"""
        url = f"{self.base_url}/api/v1/onebox/send"

        emaildata = {
            "to": [to_email] if isinstance(to_email, str) else to_email,
            "from": from_email,
            "subject": subject,
            "body": body,
            "cc": [],
            "bcc": [],
            "references": references or [],
            "inReplyTo": in_reply_to,
            "originalMessageId": original_message_id
        }

        files = {"emaildata": (None, json.dumps(emaildata))}
        response = requests.post(url, headers=self.headers, files=files)
        return response.json()


def main():
    api_key = "5a6a077f-710c-4035-9e8b-67ebdd7efd31"
    client = ReachInboxClient(api_key)

    print("🔍 Searching for Jason with reply...")
    jason = client.find_jason_with_reply()

    if not jason:
        print("❌ No Jason with a reply found")
        return

    jason_email = jason.get("email")
    first_name = jason.get("attributes", {}).get("firstName", "Jason")
    last_name = jason.get("attributes", {}).get("lastName", "")
    campaign_name = jason.get("campaign", {}).get("name", "Unknown")
    from_email = jason.get("emailUsedToSend", "")

    print(f"\n✅ Found: {first_name} {last_name}")
    print(f"   Email: {jason_email}")
    print(f"   Campaign: {campaign_name}")
    print(f"   From account: {from_email}")

    # Prepare reply
    subject = "Re: Interested in discussing further"
    body = f"""<p>Hi {first_name},</p>

<p>Thanks so much for getting back to me! I really appreciate your reply and interest in connecting.</p>

<p>I'd love to discuss how we can help {jason.get('attributes', {}).get('companyName', 'your organization')} further. Would you be available for a brief call next week?</p>

<p>Looking forward to hearing from you.</p>

<p>Best regards,<br>{from_email.split('@')[0].title()}</p>"""

    print(f"\n📤 Sending reply to {first_name} {last_name}...")
    response = client.send_reply(
        to_email=jason_email,
        subject=subject,
        body=body,
        from_email=from_email
    )

    if response.get("status") == 200:
        print(f"✅ Reply sent successfully!")
    else:
        print(f"❌ Error: {response.get('message', 'Unknown error')}")
        print(f"Response: {json.dumps(response, indent=2)}")


if __name__ == "__main__":
    main()
